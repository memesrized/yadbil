import asyncio
import time
from pathlib import Path

from tqdm import tqdm

from yadbil.data.mining.telegram.utils.base import TelegramAsync
from yadbil.data.mining.telegram.utils.io import save_messages_to_file
from yadbil.data.mining.telegram.utils.message_processing import MessageProcessor
from yadbil.data.mining.telegram.utils.telegram_client import (
    TelegramMessageFetcher,
    TelegramMessageFetcherSync,
)
from yadbil.utils.logger import get_logger


logger = get_logger(__name__)


class TelegramScraper(TelegramAsync):
    def __init__(
        self,
        creds,
        channels,
        output_dir,
        save_to_disk=True,
        batch_size=100,
        retry_limit=3,
    ):
        self.creds = creds
        self.channels = channels or []
        self.save_to_disk = save_to_disk
        self.batch_size = batch_size
        self.output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
        self.retry_limit = retry_limit

    async def process_channel(self, parser: TelegramMessageFetcher, channel: str) -> dict:
        try:
            message_batch = []
            message_count = 0
            pbar = tqdm(desc=f"Processing {channel}", unit=" messages")

            async for message in parser.iter_channel_messages(channel):
                processed_message = MessageProcessor(message).process()
                message_batch.append(processed_message)
                message_count += 1
                pbar.update(1)

                if self.save_to_disk and len(message_batch) >= self.batch_size:
                    await save_messages_to_file(channel, message_batch, self.output_dir)
                    message_batch.clear()

            # Save any remaining messages
            if self.save_to_disk and message_batch:
                await save_messages_to_file(channel, message_batch, self.output_dir)

            pbar.close()
            logger.info(f"Processed {message_count} messages from {channel}")
            logger.info(f"Output folder: {self.output_dir / channel}")
        except Exception as e:
            logger.error(f"Error processing messages from channel {channel}: {str(e)}")

    async def retry_process_channel(self, parser: TelegramMessageFetcher, channel: str) -> dict:
        retries = 0
        while retries < self.retry_limit:
            try:
                return await self.process_channel(parser, channel)
            except Exception as e:
                retries += 1
                logger.error(f"Retry {retries}/{self.retry_limit} for channel {channel} due to error: {str(e)}")
                await asyncio.sleep(2**retries)  # Exponential backoff
        return []

    async def _run(self) -> None:
        if not self.creds:
            logger.error("Please ensure API_ID, API_HASH, and PHONE_NUMBER are set in your .env file.")
            return

        if not self.channels:
            logger.error("No channels to parse. Please add channels to parse_telegram.json.")
            return

        async with TelegramMessageFetcher(self.creds) as parser:
            tasks = [self.retry_process_channel(parser, channel) for channel in self.channels]
            # TODO: return results optionally
            await asyncio.gather(*tasks)


class TelegramScraperSync:
    def __init__(
        self,
        creds,
        channels=None,
        output_dir=None,
        save_to_disk=True,
        batch_size=100,
        retry_limit=3,
    ):
        self.creds = creds
        self.channels = channels or []
        self.save_to_disk = save_to_disk
        self.batch_size = batch_size
        self.output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
        self.retry_limit = retry_limit

    def process_channel(self, parser: TelegramMessageFetcherSync, channel: str) -> dict:
        try:
            message_batch = []
            message_count = 0
            pbar = tqdm(desc=f"Processing {channel}", unit=" messages")

            for message in parser.iter_channel_messages(channel):
                processed_message = MessageProcessor(message).process()
                message_batch.append(processed_message)
                message_count += 1
                pbar.update(1)

                if self.save_to_disk and len(message_batch) >= self.batch_size:
                    save_messages_to_file(channel, message_batch, self.output_dir)
                    message_batch.clear()

            if self.save_to_disk and message_batch:
                save_messages_to_file(channel, message_batch, self.output_dir)

            pbar.close()
            logger.info(f"Processed {message_count} messages from {channel}")
            logger.info(f"Output folder: {self.output_dir / channel}")

        except Exception as e:
            logger.error(f"Error processing messages from channel {channel}: {str(e)}")

    def retry_process_channel(self, parser: TelegramMessageFetcherSync, channel: str) -> dict:
        retries = 0
        while retries < self.retry_limit:
            try:
                return self.process_channel(parser, channel)
            except Exception as e:
                retries += 1
                logger.error(f"Retry {retries}/{self.retry_limit} for channel {channel} due to error: {str(e)}")
                time.sleep(2**retries)  # Exponential backoff
        return []

    def run(self) -> None:
        if not self.creds:
            logger.error("Please ensure API_ID, API_HASH, and PHONE_NUMBER are set in your .env file.")
            return

        if not self.channels:
            logger.error("No channels to parse. Please add channels to parse_telegram.json.")
            return

        with TelegramMessageFetcherSync(self.creds) as parser:
            for channel in self.channels:
                self.retry_process_channel(parser, channel)


if __name__ == "__main__":
    from yadbil.pipeline.config import PipelineConfig
    from yadbil.pipeline.creds import TelegramCreds

    config = PipelineConfig()
    creds = TelegramCreds()

    scraper = TelegramScraper(creds=creds, **config["TelegramScraper"])
    scraper.run()
