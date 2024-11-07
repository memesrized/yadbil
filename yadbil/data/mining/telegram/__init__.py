from yadbil.data.mining.telegram.channels_info import (
    TelegramChannelInfoParser,
    TelegramChannelInfoParserSync,
)
from yadbil.data.mining.telegram.processing import TelegramDataProcessor
from yadbil.data.mining.telegram.scraping import TelegramScraper, TelegramScraperSync


TELEGRAM_STEPS = [
    TelegramScraper,
    TelegramChannelInfoParser,
    TelegramDataProcessor,
    TelegramChannelInfoParserSync,
    TelegramScraperSync,
]
