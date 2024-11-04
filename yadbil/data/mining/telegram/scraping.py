import asyncio
import logging

from tqdm import tqdm

from yadbil.data.mining.telegram.config import TelegramParserConfig
from yadbil.data.mining.telegram.utils.io import save_messages_to_file
from yadbil.data.mining.telegram.utils.message_processing import MessageProcessor
from yadbil.data.mining.telegram.utils.telegram_client import TelegramParser


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TelegramScraper:
    def __init__(self):
        self.config = TelegramParserConfig()

    async def process_channel(self, parser: TelegramParser, channel: str) -> dict:
        try:
            message_batch = []
            message_count = 0
            pbar = tqdm(desc=f"Processing {channel}", unit=" messages")
            # results = []

            async for message in parser.iter_channel_messages(channel):
                processed_message = MessageProcessor(message).process()
                message_batch.append(processed_message)
                # results.append(processed_message)
                message_count += 1
                pbar.update(1)

                if self.config.save_to_disk and len(message_batch) >= self.config.batch_size:
                    await save_messages_to_file(channel, message_batch, self.config.output_dir)
                    message_batch.clear()

            # Save any remaining messages
            if self.config.save_to_disk and message_batch:
                await save_messages_to_file(channel, message_batch, self.config.output_dir)

            pbar.close()
            logger.info(f"Processed {message_count} messages from {channel}")
            logger.info(f"Output folder: {self.config.output_dir}")

            # return channel, results

        except Exception as e:
            logger.error(f"Error processing messages from channel {channel}: {str(e)}")
            # return []

    async def retry_process_channel(self, parser: TelegramParser, channel: str) -> dict:
        retries = 0
        while retries < self.config.retry_limit:
            try:
                return await self.process_channel(parser, channel)
            except Exception as e:
                retries += 1
                logger.error(f"Retry {retries}/{self.config.retry_limit} for channel {channel} due to error: {str(e)}")
                await asyncio.sleep(2**retries)  # Exponential backoff
        return []

    async def run(self) -> None:
        if not self.config.api_id or not self.config.api_hash or not self.config.phone_number:
            logger.error("Please ensure API_ID, API_HASH, and PHONE_NUMBER are set in your .env file.")
            return

        if not self.config.channels:
            logger.error("No channels to parse. Please add channels to parse_telegram.json.")
            return

        async with TelegramParser(self.config) as parser:
            tasks = [self.retry_process_channel(parser, channel) for channel in self.config.channels]
            # TODO: return results optionally
            await asyncio.gather(*tasks)
            # results = await asyncio.gather(*tasks)
            # return dict(results)


if __name__ == "__main__":
    scraper = TelegramScraper()
    a = asyncio.run(scraper.run())
    print(a.keys())
