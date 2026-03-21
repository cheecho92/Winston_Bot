#!/usr/bin/env python3.13
import json
import requests
import os
import string
import secrets
import subprocess
from urllib.parse import urlencode
from auth_handler import RedirectHandler
from http.server import HTTPServer
from auth_dataclass import Config
from dotenv import load_dotenv


# Load the env variables
load_dotenv()

# Generates a randomized state string
def random_string_generator():
    alphabet = string.ascii_letters + string.digits
    state_string = ''.join(secrets.choice(alphabet) for i in range(33))
    return state_string


# Open a private browser session for the OAuth session
def open_private_browser(url):
    subprocess.Popen(['waterfox', '--private-window', url])


# Generates a temp local webserver to handle redirect uris using HTTPServer and auth_handler
# Might want to revisit to apply a nonce
def retrieve_redirect_code(uri, host, port, state):
    server = HTTPServer((host, port), RedirectHandler)
    server.state = state
    open_private_browser(uri)
    server.handle_request()
    code = server.code
    server.server_close()
    print("Server is closed.")
    return code


# Use the Config dataclass to create the auth and token links cleanly
# Might want to revisit to apply a nonce
def url_parser(config, uri, state):
    params = {
        "response_type": "code",
        "client_id": config.client_id,
        "redirect_uri": config.redirect_uri,
        "scope": " ".join(config.scopes),
        "state": state,
    }
    return f"{uri}?{urlencode(params)}"


# Read the token JSON file as dict
def load_tokens(config):
    with open(config.token_file, "r") as f:
        tokens = json.load(f)
    return tokens


# Save POST response to a JSON file
def save_tokens(name, request_response):
    with open(f"{name}_token.json", "w") as f:
        json.dump(request_response, f, indent=4)


# Generate the headers based on config profile
def generate_headers(config):
    if config.name == "twitch":
        params = {
        'Authorization': f"Bearer {config.access_token}",
        'Client-Id': config.client_id,
        'Content-Type': 'application/json'
        }
    else:
        params = {
        'Authorization': f"Bearer {config.access_token}",
        'Content-Type': 'application/json'
        }
    
    return params
    

# Handles the initial token generation and refresh tokens depending on if the code argument is passed.
def handle_tokens(config):
    if os.path.exists(config.token_file):
        tokens = load_tokens(config)

        params = {
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"]
        }
    else:
        state_string = random_string_generator()
        auth_uri = url_parser(config, config.auth_uri, state_string)
        code = retrieve_redirect_code(auth_uri, config.host, config.port, state_string)

        params = {
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": config.redirect_uri,
        }

    encoded_params = urlencode(params)
    req = requests.post(config.token_uri, headers=config.content_type, data=encoded_params)
    req.raise_for_status()
    response = req.json()

    if "refresh_token" not in response:
        response["refresh_token"] = tokens["refresh_token"]

    save_tokens(config.name, response)  
    config.access_token = response["access_token"]
    config.refresh_token = response["refresh_token"]
    config.headers = generate_headers(config)
    return config


# Wrapper for REST methods in the API file that checks for API request errors
def api_call(config, method, url, **kwargs):
    req = method(url, **kwargs)
    if req.status_code == 401:
        handle_tokens(config)
        kwargs['headers'] = config.headers
        req = method(url, **kwargs)
    req.raise_for_status()
    return req


# Twitch dataclass info
twitch = Config(
    name = "twitch",
    client_id = os.getenv("TWITCH_CLIENT_ID"),
    client_secret = os.getenv("TWITCH_SECRET"),
    auth_uri = "https://id.twitch.tv/oauth2/authorize",
    token_uri = "https://id.twitch.tv/oauth2/token",
    scopes = ['user:write:chat','user:bot','channel:bot', 'user:read:chat','moderator:read:followers', 'moderator:manage:banned_users','moderator:read:suspicious_users'],
    api_uri = "https://api.twitch.tv/helix/",
    channel = os.getenv("CHEECHO_ID"),
    bot = os.getenv("BOT_ID"),
    token_file = "twitch_token.json",
    content_type = {'Content-Type': "application/x-www-form-urlencoded"}
)

# Spotify dataclass info
spotify = Config(
    name = "spotify",
    client_id = os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret = os.getenv("SPOTIFY_SECRET"),
    auth_uri = "https://accounts.spotify.com/authorize",
    token_uri = "https://accounts.spotify.com/api/token",
    scopes = ['user-modify-playback-state user-read-currently-playing user-read-playback-state'],
    api_uri = "https://api.spotify.com/v1/",
    token_file = "spotify_token.json",
    host = "127.0.0.1",
    port = 4000,
    redirect_uri = "http://127.0.0.1:4000",
    content_type = {"Content-Type": "application/x-www-form-urlencoded"}
)