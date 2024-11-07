from yadbil.data.mining.telegram.channels_info import TelegramChannelInfoParserSync
from yadbil.data.mining.telegram.processing import TelegramDataProcessor
from yadbil.data.mining.telegram.scraping import TelegramScraperSync
from yadbil.pipeline.config import PipelineConfig
from yadbil.pipeline.creds import TelegramCreds
from yadbil.pipeline.pipeline import Pipeline


creds = TelegramCreds()
config = PipelineConfig()

pipe = Pipeline(
    [
        TelegramChannelInfoParserSync(
            channels=config["TelegramChannelInfoParser"]["channels"],
            output_dir=config["TelegramChannelInfoParser"]["output_dir"],
            creds=creds,
        ),
        TelegramScraperSync(
            creds=creds,
            channels=config["TelegramScraper"]["channels"],
            output_dir=config["TelegramScraper"]["output_dir"],
        ),
        TelegramDataProcessor(
            channels_info_dir=config["TelegramDataProcessor"]["channels_info_dir"],
            output_dir=config["TelegramDataProcessor"]["output_dir"],
            input_dir=config["TelegramDataProcessor"]["input_dir"],
        ),
    ]
)

pipe.run()
