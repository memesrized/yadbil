from typing import Any, AsyncIterator, Dict, Iterator, Union

from telethon import TelegramClient
from telethon.sync import TelegramClient as SyncTelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    Channel,
    Chat,
    User,
)


# TODO: change config to parameters
class TelegramMessageFetcher:
    def __init__(self, creds):
        self.client = None
        self.creds = creds

    async def __aenter__(self):
        self.client = TelegramClient("session", self.creds.api_id, self.creds.api_hash)
        await self.client.start(phone=self.creds.phone_number)
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


# TODO: change config to parameters
class TelegramInfoFetcher:
    def __init__(self, creds):
        self.creds = creds
        self.client = None

    async def __aenter__(self):
        if not all([self.creds.api_id, self.creds.api_hash, self.creds.phone_number]):
            raise ValueError("Missing API credentials. Please check your .env file.")
        self.client = TelegramClient("session", self.creds.api_id, self.creds.api_hash)
        await self.client.start(phone=self.creds.phone_number)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()

    async def get_entity_info(self, identifier: Union[int, str]) -> Dict[str, Any]:
        try:
            entity = await self.client.get_entity(identifier)

            if isinstance(entity, Channel):
                full_entity = await self.client(GetFullChannelRequest(entity))
                return self._format_channel_info(full_entity)
            elif isinstance(entity, User):
                full_entity = await self.client(GetFullUserRequest(entity))
                return self._format_user_info(full_entity)
            elif isinstance(entity, Chat):
                full_entity = await self.client(GetFullChatRequest(entity.id))
                return self._format_chat_info(full_entity)
            else:
                return {"error": f"Unknown entity type: {type(entity)}"}
        except ValueError as e:
            return {"error": f"Entity not found: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def _format_channel_info(self, full_channel) -> Dict[str, Any]:
        channel = full_channel.chats[0]
        return {
            "type": "Supergroup" if channel.megagroup else "Channel",
            "id": channel.id,
            "title": channel.title,
            "username": channel.username,
            "description": full_channel.full_chat.about,
            "member_count": full_channel.full_chat.participants_count,
            "is_verified": channel.verified,
            "is_restricted": channel.restricted,
            "is_scam": channel.scam,
            "is_fake": channel.fake,
        }

    def _format_user_info(self, full_user) -> Dict[str, Any]:
        user = full_user.users[0]
        return {
            "type": "User",
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "phone": user.phone,
            "bio": full_user.full_user.about,
            "is_bot": user.bot,
            "is_verified": user.verified,
            "is_restricted": user.restricted,
            "is_scam": user.scam,
            "is_fake": user.fake,
        }

    def _format_chat_info(self, full_chat) -> Dict[str, Any]:
        chat = full_chat.chats[0]
        return {
            "type": "Group Chat",
            "id": chat.id,
            "title": chat.title,
            "member_count": full_chat.full_chat.participants_count,
        }


# TODO: make it work in jupyter
class TelegramMessageFetcherSync:
    def __init__(self, creds):
        self.client = None
        self.creds = creds

    def __enter__(self):
        self.client = SyncTelegramClient("session", self.creds.api_id, self.creds.api_hash)
        self.client.start(phone=self.creds.phone_number)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.disconnect()

    def iter_channel_messages(self, channel: str, limit: int = None) -> Iterator[Any]:
        """
        Iterate over messages from a specified channel.

        Args:
            channel (str): The channel username or ID.
            limit (int, optional): The maximum number of messages to retrieve. Defaults to None (all messages).

        Yields:
            Any: Telethon message objects.
        """
        try:
            for message in self.client.iter_messages(channel, limit=limit):
                yield message
        except Exception as e:
            raise Exception(f"Error retrieving messages from channel {channel}: {str(e)}")


# TODO: make it work in jupyter
class TelegramInfoFetcherSync:
    def __init__(self, creds):
        self.creds = creds
        self.client = None

    def __enter__(self):
        if not all([self.creds.api_id, self.creds.api_hash, self.creds.phone_number]):
            raise ValueError("Missing API credentials. Please check your .env file.")
        self.client = SyncTelegramClient("session", self.creds.api_id, self.creds.api_hash)
        self.client.start(phone=self.creds.phone_number)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.disconnect()

    # TODO: it has no difference with the async version
    def get_entity_info_sync(self, identifier: Union[int, str]) -> Dict[str, Any]:
        """Synchronous version of get_entity_info"""
        try:
            entity = self.client.get_entity(identifier)

            if isinstance(entity, Channel):
                # TODO: it seems that GetFullChannelRequest and all other classes below
                # should be converted to sync version for proper run
                # there is a script in telethon.sync that can be used to convert async to sync
                # it doesn't work in jupyter
                full_entity = self.client(GetFullChannelRequest(entity))
                return self._format_channel_info(full_entity)
            elif isinstance(entity, User):
                full_entity = self.client(GetFullUserRequest(entity))
                return self._format_user_info(full_entity)
            elif isinstance(entity, Chat):
                full_entity = self.client(GetFullChatRequest(entity.id))
                return self._format_chat_info(full_entity)
            else:
                return {"error": f"Unknown entity type: {type(entity)}"}
        except ValueError as e:
            return {"error": f"Entity not found: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def get_entity_info(self, identifier: Union[int, str]) -> Dict[str, Any]:
        try:
            entity = self.client.get_entity(identifier)

            if isinstance(entity, Channel):
                full_entity = self.client(GetFullChannelRequest(entity))
                return self._format_channel_info(full_entity)
            elif isinstance(entity, User):
                full_entity = self.client(GetFullUserRequest(entity))
                return self._format_user_info(full_entity)
            elif isinstance(entity, Chat):
                full_entity = self.client(GetFullChatRequest(entity.id))
                return self._format_chat_info(full_entity)
            else:
                return {"error": f"Unknown entity type: {type(entity)}"}
        except ValueError as e:
            return {"error": f"Entity not found: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    def _format_channel_info(self, full_channel) -> Dict[str, Any]:
        channel = full_channel.chats[0]
        return {
            "type": "Supergroup" if channel.megagroup else "Channel",
            "id": channel.id,
            "title": channel.title,
            "username": channel.username,
            "description": full_channel.full_chat.about,
            "member_count": full_channel.full_chat.participants_count,
            "is_verified": channel.verified,
            "is_restricted": channel.restricted,
            "is_scam": channel.scam,
            "is_fake": channel.fake,
        }

    def _format_user_info(self, full_user) -> Dict[str, Any]:
        user = full_user.users[0]
        return {
            "type": "User",
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "phone": user.phone,
            "bio": full_user.full_user.about,
            "is_bot": user.bot,
            "is_verified": user.verified,
            "is_restricted": user.restricted,
            "is_scam": user.scam,
            "is_fake": user.fake,
        }

    def _format_chat_info(self, full_chat) -> Dict[str, Any]:
        chat = full_chat.chats[0]
        return {
            "type": "Group Chat",
            "id": chat.id,
            "title": chat.title,
            "member_count": full_chat.full_chat.participants_count,
        }
