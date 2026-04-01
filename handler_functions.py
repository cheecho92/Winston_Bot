from twitch_calls import chat_post
from spotify_calls import check_queue, add_to_queue, get_song_info

# Handlers for the bots command list in the websocket_monitor.py file
def handle_lurk(poster, twitch_config):
    chat_post(twitch_config, f"@{poster}... Fine. I didn't want you here anyway... BigSad")


def handle_ket(twitch_config):
    chat_post(twitch_config, "meow")


def handle_kappa(poster, twitch_config):
    if poster != "winstonkittybot":
        chat_post(twitch_config, "Kappa")

def handle_praise(poster, text, twitch_config):
    if text == "good boy":
        chat_post(twitch_config, f"@{poster} thank meow veowy mooch :3")


def handle_song(poster, text, spotify_config, twitch_config):
    check_queue(poster, text, spotify_config, twitch_config)


def handle_next(poster, text, spotify_config, twitch_config):
    check_queue(poster, text, spotify_config, twitch_config)


def handle_discord(twitch_config):
    chat_post(twitch_config, f"Join the stream discord: {twitch_config.discord} ")


def handle_request(text, spotify_config, poster, twitch_config):
    try:
        song_uri, song_name, artist_name = get_song_info(text[35:], spotify_config, poster, twitch_config)
        add_to_queue(song_uri, song_name, artist_name, spotify_config, poster, twitch_config)
    except ValueError:
        raise