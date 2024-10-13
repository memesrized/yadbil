import asyncio
import json
import os
from typing import Any, Dict, Union

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    Channel,
    Chat,
    User,
)

from yadbil.data.source.telegram.scraping.config import Config


load_dotenv()


class TelegramInfoFetcher:
    def __init__(self):
        self.api_id = os.getenv("API_ID")
        self.api_hash = os.getenv("API_HASH")
        self.phone_number = os.getenv("PHONE_NUMBER")
        self.client = None

    async def __aenter__(self):
        if not all([self.api_id, self.api_hash, self.phone_number]):
            raise ValueError("Missing API credentials. Please check your .env file.")
        self.client = TelegramClient("session", self.api_id, self.api_hash)
        await self.client.start(phone=self.phone_number)
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


async def main():
    config = Config()
    res = []
    async with TelegramInfoFetcher() as fetcher:
        # Example usage with different types of identifiers
        identifiers = ["@" + x for x in config.channels]

        for identifier in identifiers:
            info = await fetcher.get_entity_info(identifier)
            res.append(info)

    config.channels_info_output_dir.mkdir(parents=True, exist_ok=True)
    with open(config.channels_info_output_dir / "channels_meta.json", "w") as file:
        json.dump(res, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
