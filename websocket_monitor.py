#!/usr/bin/env python3.13
import websockets
import os
import json
from winston_shared.twitch_calls import eventsub_handler, parse_payload, chat_post, ban_user
from handler_functions import handle_praise, handle_discord, handle_kappa, handle_ket, handle_lurk, handle_next, handle_request, handle_song
from dotenv import load_dotenv

load_dotenv()

# async function to loop through twitch events
async def listen_twitch(bot, spotify):
    async with websockets.connect("wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=30") as ws:
        print("Connected to Twitch EventSub WebSocket")

        command_dict = {
            "!lurk": lambda poster, text, message: handle_lurk(poster, bot, message),
            "ket": lambda poster, text, message: handle_ket(bot, message),
            "kappa": lambda poster, text, message: handle_kappa(poster, bot, message),
            "!song": lambda poster, text, message: handle_song(poster, text, spotify, bot, message),
            "!next": lambda poster, text, message: handle_next(poster, text, spotify, bot, message),
            "!discord": lambda poster, text, message: handle_discord(bot, message),
            "!sr": lambda poster, text, message: handle_request(text, spotify, bot, poster, message),
            "good": lambda poster, text, message: handle_praise(poster, text, bot, message),
        }

        with open(os.getenv("BANNED_PHRASES_FILE")) as f:
            banned_phrases = [line.rstrip() for line in f]

        with open(os.getenv("MESSAGE_FILE")) as f:
            message = json.load(f)

        async for event in ws:

            payload = eventsub_handler(bot, event)

            try:
                event_type, follower, poster, text = parse_payload(payload)
            except KeyError:
                continue

            if event_type == "channel.follow":
                chat_post(bot, message['commands']['follow'].format(follower=follower))

            elif event_type == "channel.suspicious_user.message":
                ban_user(poster, bot, message)

            elif poster and text:

                command = text.split()[0]

                if text in banned_phrases:
                    ban_user(poster, bot, message)

                elif command in command_dict:
                    try:
                        command_dict[command](poster, text, message)
                    except ValueError:
                        continue