import asyncio
import json

from yadbil.data.mining.telegram.utils.base import TelegramAsync
from yadbil.data.mining.telegram.utils.telegram_client import (
    TelegramInfoFetcher,
    TelegramInfoFetcherSync,
)


class TelegramChannelInfoParser(TelegramAsync):
    def __init__(self, channels, output_dir, creds):
        self.channels = channels
        self.output_dir = output_dir
        self.res = []
        self.creds = creds

    async def _run(self):
        async with TelegramInfoFetcher(self.creds) as fetcher:
            # TODO: double check if this needed
            identifiers = ["@" + x for x in self.channels]

            tasks = [fetcher.get_entity_info(identifier) for identifier in identifiers]
            self.res = await asyncio.gather(*tasks)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_dir / "channels_meta.json", "w") as file:
            json.dump(self.res, file, ensure_ascii=False, indent=4)

    # def run(self):
    #     asyncio.run(self._run())


class TelegramChannelInfoParserSync:
    def __init__(self, channels, output_dir, creds):
        self.channels = channels
        self.output_dir = output_dir
        self.res = []
        self.creds = creds

    def run(self):
        with TelegramInfoFetcherSync(self.creds) as fetcher:
            identifiers = ["@" + x for x in self.channels]
            for identifier in identifiers:
                # Ensure get_entity_info_sync exists and is synchronous
                self.res.append(fetcher.get_entity_info_sync(identifier))

        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_dir / "channels_meta.json", "w") as file:
            json.dump(self.res, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    from yadbil.data.mining.telegram.config import TelegramParserConfig
    from yadbil.pipeline.creds import TelegramCreds

    config = TelegramParserConfig()
    creds = TelegramCreds()
    fetcher = TelegramChannelInfoParser(
        channels=config.channels,
        output_dir=config.channels_info_output_dir,
        creds=creds,
    )
    fetcher.run()
