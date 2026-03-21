#!/usr/bin/env python3.13
import asyncio
from websocket_monitor import listen_twitch
from auth import handle_tokens, spotify, twitch

async def main():
    handle_tokens(twitch)
    handle_tokens(spotify)
    await listen_twitch()

if __name__ == "__main__":
    asyncio.run(main())