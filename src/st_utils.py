# TODO: make height based on data length
def tg_html(channel_id, post_id):
    telegram_html = (
        '<script async src="https://telegram.org/js/telegram-widget.js?22"'
        f' data-telegram-post="{channel_id}/{post_id}" data-width="100%"></script>'
    )
    return f"<body>{telegram_html}</body>"
