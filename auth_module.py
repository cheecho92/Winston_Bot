#!/usr/bin/env python3.13
import requests
import json
import os
import secrets
import subprocess
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class OAuthConfig:
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    redirect_uri: str
    scopes: List[str]
    token_file: str
    host: str = "localhost"
    port: int = 3000
    content_type: str = "text/html"
    success_message: bytes = b"Authorization successful! You can close this tab."
    error_message: bytes = b"Authorization failed or invalid state."


class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)

        if "code" in params and "state" in params:
            if params["state"][0] == self.server.state:
                self.server.auth_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-type", self.server.config.content_type)
                self.end_headers()
                self.wfile.write(self.server.config.success_message)
            else:
                self.send_response(400)
                self.send_header("Content-type", self.server.config.content_type)
                self.end_headers()
                self.wfile.write(self.server.config.error_message)
        else:
            self.send_response(400)
            self.send_header("Content-type", self.server.config.content_type)
            self.end_headers()
            self.wfile.write(self.server.config.error_message)


def open_firefox_private(url: str):
    try:
        subprocess.Popen(["firefox", "--private-window", url])
    except Exception:
        print("Could not open Firefox automatically.")
        print("Please open this URL in a private browser window:")
        print(url)


def get_auth_url(config: OAuthConfig, state: str):
    scopes = "+".join(config.scopes)
    return (
        f"{config.auth_url}?response_type=code&client_id={config.client_id}"
        f"&redirect_uri={config.redirect_uri}&scope={scopes}&state={state}"
    )


def exchange_code_for_tokens(config: OAuthConfig, code: str):
    resp = requests.post(
        config.token_url,
        data={
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config.redirect_uri,
        },
    )
    resp.raise_for_status()
    tokens = resp.json()
    tokens["obtained_at"] = int(time.time())
    return tokens


def refresh_access_token(config: OAuthConfig, refresh_token: str):
    resp = requests.post(
        config.token_url,
        data={
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )
    resp.raise_for_status()
    tokens = resp.json()
    tokens["obtained_at"] = int(time.time())
    return tokens


def save_tokens(config: OAuthConfig, tokens: dict):
    with open(config.token_file, "w") as f:
        json.dump(tokens, f, indent=2)


def load_tokens(config: OAuthConfig) -> Optional[dict]:
    if os.path.exists(config.token_file):
        with open(config.token_file, "r") as f:
            return json.load(f)
    return None


def is_token_expired(tokens: dict) -> bool:
    if "expires_in" not in tokens or "obtained_at" not in tokens:
        return True
    lifetime = tokens["expires_in"]
    obtained = tokens["obtained_at"]
    return (time.time() - obtained) > (lifetime - 60)


def ensure_tokens(config: OAuthConfig) -> dict:
    tokens = load_tokens(config)

    if tokens:
        if is_token_expired(tokens):
            print(f"Access token expired for {config.token_file}, refreshing...")
            try:
                tokens = refresh_access_token(config, tokens["refresh_token"])
                save_tokens(config, tokens)
                return tokens
            except Exception as e:
                print(f"Refresh failed: {e}")
        else:
            return tokens

    state = secrets.token_urlsafe(33)
    server = HTTPServer((config.host, config.port), OAuthHandler)
    server.state = state
    server.config = config
    url = get_auth_url(config, state)

    print("Opening Firefox private window for OAuth login...")
    open_firefox_private(url)
    print("Waiting for authorization...")

    server.handle_request()
    code = getattr(server, "auth_code", None)

    if not code:
        raise RuntimeError("Authorization failed, no code received")

    tokens = exchange_code_for_tokens(config, code)
    save_tokens(config, tokens)
    return tokens


def get_tokens(config: OAuthConfig) -> dict:
    return ensure_tokens(config)
