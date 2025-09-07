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
    scopes=['user-modify-playback-state user-read-currently-playing'],
    token_file="spotify_tokens.json",
    host="127.0.0.1",
    port=4000,
    content_type="application/x-www-form-urlencoded",
    success_message=b'{"status":"ok","message":"spotify auth complete!"}',
    error_message=b'{"status":"error","message":"spotify auth failed"}'
)


twitch_tokens = get_tokens(twitch_config)
spotify_tokens = get_tokens(spotify_config)


# return twitch headers and refresh access token
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


# return headers and refresh access token
def get_spotify_headers():
    spotify_tokens = get_tokens(spotify_config)
    access_token = spotify_tokens["access_token"]

    spotify_headers = {
    'Authorization': f"Bearer {access_token}",
    'Content-Type': 'application/json',
    }
    return spotify_headers

def disply_current_song():
    r = requests.get(
    f"https://api.spotify.com/v1/me/player/queue",
    headers=get_spotify_headers(),
    )
    r.raise_for_status()
    response = r.json()
    song_name = response['currently_playing']['name']
    artist_name = response['currently_playing']['album']['artists'][0]['name']
    return song_name, artist_name


# used to prevent duplicate requests
def disply_next_song():
    r = requests.get(
        f"https://api.spotify.com/v1/me/player/queue",
        headers=get_spotify_headers(),
    )
    r.raise_for_status()
    response = r.json()
    song_name = response['queue'][0]['name']
    artist_name = response['queue'][0]['album']['artists'][0]['name']
    print(song_name, artist_name)
    return song_name, artist_name


# parse spotify request song id
def get_song(id):
    r = requests.get(
        f"https://api.spotify.com/v1/tracks/{id}",
        headers=get_spotify_headers(),
    )
    # Return status of post
    r.raise_for_status()
    response = r.json()
    song_uri = response["uri"]
    artist_dict = response["album"]["artists"]
    artist_name = artist_dict[0]["name"]
    song_name = response["name"]
    return song_uri, song_name, artist_name



# Add song to current queue
def add_to_queue(song_uri):
    r = requests.post(
    f"https://api.spotify.com/v1/me/player/queue?uri={song_uri}",
    headers=get_spotify_headers(),
    )
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

                if text.lower() == "!lurk":
                    chat_post(f"@{poster}, you're leaving me alone with my thoughts D:")

                elif text.lower() == "ket":
                    chat_post(f"meow")

                elif text.lower()[:3] == "!sr":
                    song_id = text[4:]
                    try:
                        song_id = song_id.split('https://open.spotify.com/track/')[1]
                        song_info= get_song(song_id)
                        song_uri = song_info[0]
                        song_name = song_info[1]
                        artist_name = song_info[2]

                        try:
                            add_to_queue(song_uri)
                            chat_post(f"@{poster}, {song_name} by {artist_name} has been added to the queue.")
                        except:
                            chat_post(f"@{poster}, I couldn't add the song. Please ask the dumbass what he broke.")

                    except:
                        chat_post(f"@{poster}, please don't fuck with me.")

                elif text.lower() == "!song":
                    current_song = disply_current_song()
                    chat_post(f"@{poster}, the current song is '{current_song[0]}' by {current_song[1]}.")

                elif text.lower() == "!next":
                    next_song = disply_next_song()
                    chat_post(f"@{poster}, the next song is '{next_song[0]}' by {next_song[1]}.")









async def main():
    await listen_twitch()


if __name__ == "__main__":
    asyncio.run(main())