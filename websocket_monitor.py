#!/usr/bin/env python3.13
import websockets
import os
import json
import importlib.util
from winston_shared.twitch_calls import eventsub_handler, parse_payload, chat_post, ban_user
from handler_functions import handle_praise, handle_discord, handle_kappa, handle_ket, handle_lurk, handle_next, handle_request, handle_song

# Import streamer config profile from winston_shared
config_path = os.getenv('STREAMER_CONFIG')
spec = importlib.util.spec_from_file_location("streamer_config", config_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
streamer = module.cheehco


# command dictionary. Passes poster, text, and custom messages through lambda to call them in the event loop
command_dict = {
    "!lurk": lambda poster, text, message: handle_lurk(poster, streamer, message),
    "ket": lambda poster, text, message: handle_ket(streamer, message),
    "kappa": lambda poster, text, message: handle_kappa(poster, streamer, message),
    "!song": lambda poster, text, message: handle_song(poster, text, streamer, message),
    "!next": lambda poster, text, message: handle_next(poster, text, streamer, message),
    "!discord": lambda poster, text, message: handle_discord(streamer, message),
    "!sr": lambda poster, text, message: handle_request(text, streamer, poster, message),
    "good": lambda poster, text, message: handle_praise(poster, text, streamer, message),
}

# async function to loop through twitch events
async def listen_twitch():
    async with websockets.connect("wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=30") as ws:
        print("Connected to Twitch EventSub WebSocket")

        with open('banned_phrases.txt') as f:
            banned_phrases = [line.rstrip() for line in f]

        with open(os.getenv("MESSAGE_FILE")) as f:
            message = json.load(f)

        # Listen to twitch websocket server
        async for event in ws:

            # handles session welcome and returns event payloads
            payload = eventsub_handler(streamer, event)

            # Parses information from event payload. Thanks followers or bans sus users
            try:
                event_type, follower, poster, text = parse_payload(payload)
            except KeyError:
                continue

            if event_type == "channel.follow":
                chat_post(streamer, message['commands']['follow'].format(follower=follower))

            elif event_type == "channel.suspicious_user.message":
                ban_user(poster, streamer, message)

            elif poster and text:

                # parse command from text
                command = text.split()[0]

                # Check if text is in banned phrases. Ban user if it is.
                if text in banned_phrases:
                    ban_user(poster, streamer, message)

                # call the command list based on the first word in 'text.' Edge case is needed for !sr, as it must intake user text.
                elif command in command_dict:
                    try:
                        command_dict[command](poster, text, message)
                    except ValueError:
                        continue