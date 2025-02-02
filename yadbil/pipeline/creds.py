import os

from dotenv import load_dotenv


load_dotenv()


class TelegramCreds:
    def __init__(self):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone_number = os.getenv("TELEGRAM_PHONE_NUMBER")


class OpenAICreds:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")


class PineconeCreds:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")


CREDS = [TelegramCreds, OpenAICreds]
