#!/usr/bin/env python3.13
import asyncio
import os
import importlib.util
from dotenv import load_dotenv
from winston_shared.auth import handle_tokens
from websocket_monitor import listen_twitch

load_dotenv()

config_path = os.getenv('STREAMER_CONFIG')
spec = importlib.util.spec_from_file_location("streamer_config", config_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

bot = module.bot
broadcaster = module.broadcaster
spotify = module.spotify

async def main():
    handle_tokens(bot)
    handle_tokens(broadcaster)
    handle_tokens(spotify)
    await listen_twitch(bot, spotify)

if __name__ == "__main__":
    asyncio.run(main())