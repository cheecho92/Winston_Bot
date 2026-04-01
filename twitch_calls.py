#!/usr/bin/env python3.13
import requests
import json
from auth import api_call


EVENTSUB_TYPES = [
    {'type': 'channel.chat.message', 'version': '1', 'condition_key': 'user_id'},
    {'type': 'channel.follow', 'version': '2', 'condition_key': 'moderator_user_id'},
    {'type': 'channel.suspicious_user.message', 'version': '1', 'condition_key': 'moderator_user_id'},
]

# List comprehension to build event subs dicts
def build_eventsubs(config, session_id):
    return [{
        'type': sub['type'],
        'version': sub['version'],
        'condition': {
            'broadcaster_user_id': config.channel,
            sub['condition_key']: config.bot
        },
        'transport': {
            'method': 'websocket',
            'session_id': session_id
        }
    } for sub in EVENTSUB_TYPES]


# Gather the user information for broadcaster and poster
def get_user_info(poster, config):
    req = api_call(
        config, requests.get,
        f"{config.api_uri}users?login={poster}&login={config.channel_name}",
        headers=config.headers
    )
    
    response = req.json()

    if len(response['data']) == 1:
        return
    
    users = {u['login']: u for u in response['data']}
    broadcaster = users[config.channel_name]
    user = users[poster]

    broadcaster_display_name = broadcaster['display_name']
    user_id = user['id']
    user_display_name = user['display_name']
    return broadcaster_display_name, user_id, user_display_name


# function for twitch chat API post
def chat_post(config, message):
    api_call(
        config,
        requests.post,
        f"{config.api_uri}chat/messages",
        headers=config.headers,
        json={"broadcaster_id": config.channel, "sender_id": config.bot, "message": message}
    )


# Ban user. Intercept 400 (user cannot be banned) and 409 (someone else is banning the user) errors
def ban_user(poster, config):
    user_info = get_user_info(poster, config)

    # The streamer tried to ban themselves.
    if user_info is None:
        chat_post(config, "Very funny. You're hilarious.")
        return
    else:
        broadcaster_display_name, user_id, user_display_name = user_info
        
    try:
        req = api_call(
            config,
            requests.post,
            f"{config.api_uri}moderation/bans?broadcaster_id={config.channel}&moderator_id={config.bot}",
            headers=config.headers,
            json={'data': {'user_id': user_id}}
        )

        chat_post(config, f"{user_display_name} get shit on you bot betch.")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            chat_post(config, f"Oi, @{broadcaster_display_name}. I can't ban this @{user_display_name} bitch.")
        elif e.response.status_code == 409:
            chat_post(config, f"@{broadcaster_display_name}, someone beat me to destroying @{user_display_name} >:|")
        else:
            raise


# monitor events and return their payload. This will handle the welcome message to subscribe to listed events.
'''
Might want to add a handle to check the message_id field. This could stop processing duplicate messages?

Can maybe use the return value to check through the payload dict for the "type" using payload.values()?
'''
def eventsub_handler(config, event):
    event = json.loads(event)
    payload = event['payload']

    if 'session' in payload:
        session_id = payload['session']['id']
        for sub in build_eventsubs(config, session_id):
            api_call(
                config,
                requests.post,
                f"{config.api_uri}eventsub/subscriptions",
                headers=config.headers,
                json=sub
            )
    return event['payload']


# Parse through returned eventsub_handler payload. Drop the parse if session_keepalive
def parse_payload(payload):
    if 'event' not in payload:
        raise KeyError(("No event in payload. Continuing."))
    event_type = payload['subscription']['type']

    if event_type == "channel.follow":
        follower = payload['event']['user_name']
        return event_type, follower, None, None
    
    if event_type == "channel.suspicious_user.message":
        poster = payload['event']['user_name']
        return event_type, None, poster, None
    
    poster = payload['event']['chatter_user_name']
    text = payload ['event']['message']['text']
    if "https://open.spotify.com/track" not in text:
        text = text.lower()
    return event_type, None, poster, text