#!/usr/bin/env python3.13
from auth import OAuthConfig, get_tokens
import os

def main():
    twitch_config = OAuthConfig(
        client_id=os.getenv("TWITCH_CLIENT_ID"),
        client_secret=os.getenv("TWITCH_SECRET"),
        auth_url="https://id.twitch.tv/oauth2/authorize",
        token_url="https://id.twitch.tv/oauth2/token",
        redirect_uri="http://localhost:3000",
        scopes=["user:read:chat", "user:write:chat"],
        token_file="twitch_tokens.json",
        host="localhost",
        port=3000,
        content_type="text/html",
        success_message=b"Twitch auth complete! You can close this tab.",
        error_message=b"Twitch auth failed."
    )

    youtube_config = OAuthConfig(
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_SECRET"),
        auth_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        redirect_uri="http://localhost:4000",
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],
        token_file="youtube_tokens.json",
        host="localhost",
        port=4000,
        content_type="application/json",
        success_message=b'{"status":"ok","message":"YouTube auth complete!"}',
        error_message=b'{"status":"error","message":"YouTube auth failed"}'
    )

    twitch_tokens = get_tokens(twitch_config)
    print("Twitch access token:", twitch_tokens["access_token"])

    youtube_tokens = get_tokens(youtube_config)
    print("YouTube access token:", youtube_tokens["access_token"])

if __name__ == "__main__":
    main()
