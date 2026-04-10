#!/usr/bin/env python3.13
import asyncio
import os
import importlib.util
from winston_shared.auth import handle_tokens
from websocket_monitor import listen_twitch

config_path = os.getenv('STREAMER_CONFIG')
spec = importlib.util.spec_from_file_location("streamer_config", config_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
streamer = module.cheehco

async def main():
    handle_tokens(streamer)
    await listen_twitch()

if __name__ == "__main__":
    asyncio.run(main())