#!/usr/bin/env python3.13
import websockets
from twitch_calls import eventsub_handler, parse_payload, chat_post, ban_user
from handler_functions import handle_praise, handle_discord, handle_kappa, handle_ket, handle_lurk, handle_next, handle_request, handle_song
from configs import twitch, spotify


# command dictionary. Passes poster and text through lambda to call them in the event loop
command_dict = {
    "!lurk": lambda poster, text: handle_lurk(poster, twitch),
    "ket": lambda poster, text: handle_ket(twitch),
    "kappa": lambda poster, text: handle_kappa(poster, twitch),
    "!song": lambda poster, text: handle_song(poster, text, spotify, twitch),
    "!next": lambda poster, text: handle_next(poster, text, spotify, twitch),
    "!discord": lambda poster, text: handle_discord(twitch),
    "!sr": lambda poster, text: handle_request(text, spotify, poster, twitch),
    "good": lambda poster, text: handle_praise(poster, text, twitch),
}

# async function to loop through twitch events
async def listen_twitch():
    async with websockets.connect("wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=30") as ws:
        print("Connected to Twitch EventSub WebSocket")

        with open('banned_phrases.txt') as f:
            banned_phrases = [line.rstrip() for line in f]

        # Listen to twitch websocket server
        async for event in ws:

            # handles session welcome and returns event payloads
            payload = eventsub_handler(twitch, event)

            # Parses information from event payload. Thanks followers or bans sus users
            try:
                event_type, follower, poster, text = parse_payload(payload)
            except KeyError:
                continue

            if event_type == "channel.follow":
                chat_post(twitch, f"@{follower}, thanks for the follow!")

            elif event_type == "channel.suspicious_user.message":
                ban_user(poster, twitch)

            elif poster and text:

                # parse command from text
                command = text.split()[0]

                # Check if text is in banned phrases. Ban user if it is.
                if text in banned_phrases:
                    ban_user(poster, twitch)

                # call the command list based on the first word in 'text.' Edge case is needed for !sr, as it must intake user text.
                elif command in command_dict:
                    try:
                        command_dict[command](poster, text)
                    except ValueError:
                        continue