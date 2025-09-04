#!/usr/bin/env python3.13
import asyncio
import websockets
import json
import requests
import os
from dotenv import load_dotenv
#from oauth import get_tokens, CLIENT_ID, CHEECHO_ID, BOT_ID
from auth_module import OAuthConfig, get_tokens

# Twitch websocket uri and headers Constants
load_dotenv()
TWITCH_EVENTSUB_URL = "wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=30"
TWITCH_CLIENT_ID=os.getenv("TWITCH_CLIENT_ID")
TWITCH_SECRET=os.getenv("TWITCH_SECRET")
SPOTIFY_CLIENT_ID=os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET=os.getenv("SPOTIFY_SECRET")
BOT_ID=os.getenv("BOT_ID")
CHEECHO_ID=os.getenv("CHEECHO_ID")

twitch_config = OAuthConfig(
    client_id=TWITCH_CLIENT_ID,
    client_secret=TWITCH_SECRET,
    auth_url="https://id.twitch.tv/oauth2/authorize",
    token_url="https://id.twitch.tv/oauth2/token",
    redirect_uri="http://localhost:3000",
    scopes=['user:write:chat','user:bot','channel:bot', 'user:read:chat','channel:read:subscriptions'],
    token_file="twitch_tokens.json",
    host="localhost",
    port=3000,
    content_type="text/html",
    success_message=b"Twitch auth complete! You can close this tab.",
    error_message=b"Twitch auth failed."
)

spotify_config = OAuthConfig(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_SECRET,
    auth_url="https://accounts.spotify.com/authorize",
    token_url="https://accounts.spotify.com/api/token",
    redirect_uri="http://127.0.0.1:4000",
    scopes=[],
    token_file="spotify_tokens.json",
    host="127.0.0.1",
    port=4000,
    content_type="application/x-www-form-urlencoded",
    success_message=b'{"status":"ok","message":"spotify auth complete!"}',
    error_message=b'{"status":"error","message":"spotify auth failed"}'
)

twitch_tokens = get_tokens(twitch_config)
spotify_tokens = get_tokens(spotify_config)


# return headers and refresh access token
def get_twitch_headers():
    twitch_tokens = get_tokens(twitch_config)
    access_token = twitch_tokens["access_token"]

    twitch_headers = {
    'Authorization': f"Bearer {access_token}",
    "Client-Id": TWITCH_CLIENT_ID
    }
    return twitch_headers



# function for twitch chat API post
def chat_post(message):
    r = requests.post(
        "https://api.twitch.tv/helix/chat/messages",
        headers=get_twitch_headers(),
        data={
            "broadcaster_id": CHEECHO_ID,
            "sender_id": BOT_ID,
            "message": message,
        }
    )
    # Return status of post
    r.raise_for_status()


async def listen_twitch():
    async with websockets.connect(TWITCH_EVENTSUB_URL) as ws:
        print("Connected to Twitch EventSub WebSocket")

        # Listen to twitch websocket server
        async for message in ws:

            event = json.loads(message)
            session_id = event.get('payload', {}).get('session', {}).get('id')
            message_type = event["metadata"]["message_type"]
            message_id = event["metadata"]["message_id"]
            subscription_type = event.get("metadata", {}).get("subscription_type")

            # Connect to the websocket server by message type
            if message_type == "session_welcome":

                r = requests.post(
                "https://api.twitch.tv/helix/eventsub/subscriptions",
                headers=get_twitch_headers(),
                json={
                "type": "channel.chat.message",
                "version": "1",
                "condition": {
                    "broadcaster_user_id": CHEECHO_ID,
                    "user_id": BOT_ID,
                },
                "transport": {
                    "method": "websocket",
                    "session_id": session_id
                }
                }
                )
            # Monitor for chat messages
            elif subscription_type  == "channel.chat.message":
                text = event["payload"]["event"]["message"]["text"]
                poster = event["payload"]["event"]["chatter_user_name"]

                if text == "!test":
                    chat_post(f"@{poster}, thank you for sending a test chat.")


                print(json.dumps(event, indent=4))



async def main():
    await listen_twitch()


if __name__ == "__main__":
    asyncio.run(main())