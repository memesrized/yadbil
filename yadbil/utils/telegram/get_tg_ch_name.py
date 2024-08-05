import asyncio

from telethon import TelegramClient


async def get_channel_name(channel_id, api_id, api_hash):
    async with TelegramClient("session_name", api_id, api_hash) as client:
        channel = await client.get_entity(channel_id)
        return channel.title  # This is the channel name


channel_id = 1150855655  # Replace with your actual channel ID
channel_name = asyncio.run(get_channel_name(channel_id))
print(channel_name)
