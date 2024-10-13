import asyncio
import logging

from tqdm import tqdm

from yadbil.data.source.telegram.scraping.config import Config
from yadbil.data.source.telegram.scraping.message_processing import MessageProcessor
from yadbil.data.source.telegram.scraping.telegram_client import TelegramParser
from yadbil.data.source.telegram.scraping.utils import save_messages_to_file


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def process_channel(parser, channel, config):
    try:
        message_batch = []
        message_count = 0
        pbar = tqdm(desc=f"Processing {channel}", unit=" messages")

        async for message in parser.iter_channel_messages(channel):
            processed_message = MessageProcessor(message).process()
            message_batch.append(processed_message)
            message_count += 1
            pbar.update(1)

            if len(message_batch) >= config.batch_size:
                await save_messages_to_file(channel, message_batch, config.output_dir)
                message_batch.clear()

        # Save any remaining messages
        if message_batch:
            await save_messages_to_file(channel, message_batch, config.output_dir)

        pbar.close()
        logger.info(f"Processed {message_count} messages from {channel}")
        logger.info(f"Output folder: {config.output_dir}")

    except Exception as e:
        logger.error(f"Error processing messages from channel {channel}: {str(e)}")


async def retry_process_channel(parser, channel, config):
    retries = 0
    while retries < config.retry_limit:
        try:
            await process_channel(parser, channel, config)
            break
        except Exception as e:
            retries += 1
            logger.error(f"Retry {retries}/{config.retry_limit} for channel {channel} due to error: {str(e)}")
            await asyncio.sleep(2**retries)  # Exponential backoff


async def main():
    # TODO: remove this config passing through
    config = Config()
    if not config.api_id or not config.api_hash or not config.phone_number:
        logger.error("Please ensure API_ID, API_HASH, and PHONE_NUMBER are set in your .env file.")
        return

    if not config.channels:
        logger.error("No channels to parse. Please add channels to parse_telegram.json.")
        return

    async with TelegramParser(config) as parser:
        tasks = [retry_process_channel(parser, channel, config) for channel in config.channels]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
