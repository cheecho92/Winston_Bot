from winston_shared.twitch_calls import chat_post
from winston_shared.spotify_calls import check_queue, add_to_queue, get_song_info

# Handlers for the bots command list in the websocket_monitor.py file
def handle_lurk(poster, bot, message):
    chat_post(bot, message['commands']['lurk'].format(poster=poster))


def handle_ket(bot, message):
    chat_post(bot, message['commands']['ket'])


def handle_kappa(poster, bot, message):
    if poster != "winstonkittybot":
        chat_post(bot, message['commands']['kappa'])


def handle_praise(poster, text, bot, message):
    if text == "good boy":
        chat_post(bot, message['commands']['praise'].format(poster=poster))


def handle_song(poster, text, spotify, bot, message):
    check_queue(poster, text, spotify, bot, message)


def handle_next(poster, text, spotify, bot, message):
    check_queue(poster, text, spotify, bot, message)


def handle_discord(bot, message):
    chat_post(bot, message['commands']['discord'].format(discord_link=bot.discord))


def handle_request(text, spotify, bot, poster, message):
    try:
        song_uri, song_name, artist_name = get_song_info(text[35:], poster, spotify, bot, message)
        add_to_queue(song_uri, song_name, artist_name, poster, spotify, bot, message)
    except ValueError:
        raise