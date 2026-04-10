from winston_shared.twitch_calls import chat_post
from winston_shared.spotify_calls import check_queue, add_to_queue, get_song_info

# Handlers for the bots command list in the websocket_monitor.py file
def handle_lurk(poster, streamer, message):
    chat_post(streamer, message['commands']['lurk'].format(poster=poster))


def handle_ket(streamer, message):
    chat_post(streamer, message['commands']['ket'])


def handle_kappa(poster, streamer, message):
    if poster != "winstonkittybot":
        chat_post(streamer, message['commands']['kappa'])


def handle_praise(poster, text, streamer, message):
    if text == "good boy":
        chat_post(streamer, message['commands']['praise'].format(poster=poster))


def handle_song(poster, text, streamer, message):
    check_queue(poster, text, streamer, message)


def handle_next(poster, text, streamer, message):
    check_queue(poster, text, streamer, message)


def handle_discord(streamer, message):
    chat_post(streamer, message['commands']['discord'].format(discord_link=streamer.discord))


def handle_request(text, streamer, poster, message):
    try:
        song_uri, song_name, artist_name = get_song_info(text[35:], poster, streamer, message)
        add_to_queue(song_uri, song_name, artist_name, poster, streamer, message)
    except ValueError:
        raise