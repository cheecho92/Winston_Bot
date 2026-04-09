from winston_shared.twitch_calls import chat_post
from winston_shared.spotify_calls import check_queue, add_to_queue, get_song_info

# Handlers for the bots command list in the websocket_monitor.py file
def handle_lurk(poster, twitch_config, message):
    chat_post(twitch_config, message['commands']['lurk'].format(poster=poster))


def handle_ket(twitch_config, message):
    chat_post(twitch_config, message['commands']['ket'])


def handle_kappa(poster, twitch_config, message):
    if poster != "winstonkittybot":
        chat_post(twitch_config, message['commands']['kappa'])

def handle_praise(poster, text, twitch_config, message):
    if text == "good boy":
        chat_post(twitch_config, message['commands']['praise'].format(poster=poster))


def handle_song(poster, text, spotify_config, twitch_config, message):
    check_queue(poster, text, spotify_config, twitch_config, message)


def handle_next(poster, text, spotify_config, twitch_config, message):
    check_queue(poster, text, spotify_config, twitch_config, message)


def handle_discord(twitch_config, message):
    chat_post(twitch_config, message['commands']['discord'].format(discord_link=twitch_config.discord))


def handle_request(text, spotify_config, poster, twitch_config, message):
    try:
        song_uri, song_name, artist_name = get_song_info(text[35:], spotify_config, poster, twitch_config, message)
        add_to_queue(song_uri, song_name, artist_name, spotify_config, poster, twitch_config, message)
    except ValueError:
        raise