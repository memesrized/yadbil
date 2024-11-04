from typing import Any, AsyncIterator

from telethon import TelegramClient


class TelegramParser:
    def __init__(self, config):
        self.client = None
        self._config = config

    async def __aenter__(self):
        self.client = TelegramClient("session", self._config.api_id, self._config.api_hash)
        await self.client.start(phone=self._config.phone_number)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()

    async def iter_channel_messages(self, channel: str, limit: int = None) -> AsyncIterator[Any]:
        """
        Iterate over messages from a specified channel.

        Args:
            channel (str): The channel username or ID.
            limit (int, optional): The maximum number of messages to retrieve. Defaults to None (all messages).

        Yields:
            Any: Telethon message objects.
        """
        try:
            async for message in self.client.iter_messages(channel, limit=limit):
                yield message
        except Exception as e:
            raise Exception(f"Error retrieving messages from channel {channel}: {str(e)}")
