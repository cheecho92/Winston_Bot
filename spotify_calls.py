#!/usr/bin/env python3.13
import requests
from twitch_calls import chat_post
from auth import api_call


# Retrieve the song link, name, and artist name
def get_song_info(track_id, config, poster, twitch_config):
    track_id = track_id.split("?")[0]
    try:
        req = api_call(
            config,
            requests.get,
            f"{config.api_uri}tracks/{track_id}",
            headers=config.headers
        )

        response = req.json()
        song_uri = response["uri"]
        artist_name = response['artists'][0]['name']
        song_name = response["name"]
        return song_uri, song_name, artist_name
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            chat_post(twitch_config, f"{poster}, please don't fuck with me. Use a valid spotify link.")
            raise ValueError("Invalid Spotify ID")
        else:
            raise


# Add song to the queue
def add_to_queue(song_uri, song_name, artist_name, spotify_config, poster, twitch_config):
    try:
        req = api_call(
            spotify_config,
            requests.post,
            f"{spotify_config.api_uri}me/player/queue?uri={song_uri}",
            headers=spotify_config.headers
        )
        message = f"@{poster}, {song_name} by {artist_name} has been added to the queue."
        chat_post(twitch_config, message)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            message = f"@{poster}, he doesn't want to listen to your music right now."
            chat_post(twitch_config, message)
        else:
            raise


# Display current song, or alert chatter than spotify isn't active
def check_queue(poster, text, config, twitch_config):
    req = api_call(
        config,
        requests.get,
        f"{config.api_uri}me/player/queue",
        headers=config.headers
    )
    response = req.json()

    if response['currently_playing']:
        if text == "!song":
            song_name = response['currently_playing']['name']
            artist_name = response['currently_playing']['album']['artists'][0]['name']
            message = f"@{poster}, the current song is '{song_name}' by {artist_name}."
            chat_post(twitch_config, message)
        elif text == "!next":
            try:
                song_name = response['queue'][0]['name']
                artist_name = response['queue'][0]['album']['artists'][0]['name']
                message = f"@{poster}, the next song is '{song_name}' by {artist_name}."
                chat_post(twitch_config, message)
            except IndexError:
                message = f"@{poster}, is the music in the room with us right now?"
                chat_post(twitch_config, message)
    else:
        message = f"@{poster}, is the music in the room with us right now?"
        chat_post(twitch_config, message)