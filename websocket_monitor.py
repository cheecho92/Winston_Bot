#!/usr/bin/env python3.13
import websockets
from twitch_calls import eventsub_handler, parse_payload, chat_post, ban_user
from spotify_calls import get_song_info, add_to_queue, check_queue
from auth import spotify, twitch


async def listen_twitch():
    async with websockets.connect("wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=30") as ws:
        print("Connected to Twitch EventSub WebSocket")

        with open('banned_phrases.txt') as f:
            banned_phrases = [line.rstrip() for line in f]

        # Listen to twitch websocket server
        async for event in ws:

            # handles session welcome and returns event payloads
            payload = eventsub_handler(twitch, event)

            # Parses information from event payload
            try:
                event_type, follower, poster, text = parse_payload(payload)
            except KeyError:
                continue

            if event_type == "channel.follow":
                chat_post(twitch, f"@{follower}, thanks for the follow!")

            elif poster and text:

                # Check if text is in banned phrases. Ban user if it is.
                if text in banned_phrases:
                    ban_user(poster, twitch)

                # responsd to lurk command
                elif text == "!lurk":
                    chat_post(twitch, f"@{poster}... Fine. I didn't want you here anyway... BigSad")

                # Meow
                elif text == "ket":
                    chat_post(twitch, "meow")

                # Handle song requests. The 35 slice removes https://open.spotify.com/track/ from the text
                elif text[:3] == "!sr":
                    try:
                        song_uri, song_name, artist_name = get_song_info(text[35:], spotify, poster, twitch)
                        add_to_queue(song_uri, song_name, artist_name, spotify, poster, twitch)
                    except ValueError:
                        continue

                # Check for current or next song
                elif text == "!song" or text == "!next":
                    check_queue(poster, text, spotify, twitch)