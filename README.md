This is going to be a quick and dirty README for now.

# Classes 

*Config* - a dataclass to hold information for authentication

*RedirectHandler* - info to handle REST method on temp HTTP server


# Authentication

oAuth is handled by auth.py. It uses the dataclass data to create the oAuth link, and stands up a temp local HTTP server to handle the redirect URL and retrieve the code needed for the final POST call. Finally, the handle_tokens function is called. This will check to see if an existing json file with token information is available. If it is not, it will proceed with the POST to the twitch token uri, and use the response to generate the token. 

I included the api_call function here. This functions purpose is to wrap any method with error handling for any 401 responses. If a 401 is generated, the function will call handle_tokens and use the refresh code to update the token json.


# Method Files

There are two method files. twitch_calls.py and spotify_calls.py. These contain all functions needed to handle any twitch and spotify API interaction.

# Websocket connection

websocket_monitor.py contains the build of the logic for this bot. It connections to twitchs event subscriptions using pythons websocket library. After listen_twitch is called the websocket connection is formed with async for a consistent monitor. The payload is extracted from events, parsed for data needed, and fed to the connections logic. 
