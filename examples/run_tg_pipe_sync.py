from yadbil.data.mining.telegram.channels_info import TelegramChannelInfoParserSync
from yadbil.data.mining.telegram.config import TelegramParserConfig
from yadbil.data.mining.telegram.processing import TelegramDataProcessor
from yadbil.data.mining.telegram.scraping import TelegramScraperSync
from yadbil.pipeline.creds import TelegramCreds
from yadbil.pipeline.pipeline import Pipeline


creds = TelegramCreds()
config = TelegramParserConfig()

pipe = Pipeline(
    [
        TelegramChannelInfoParserSync(
            channels=config.channels,
            output_dir=config.channels_info_output_dir,
            creds=creds,
        ),
        TelegramScraperSync(
            creds=creds,
            channels=config.channels,
            output_dir=config.output_dir,
        ),
        TelegramDataProcessor(
            channels_info_dir=config.channels_info_output_dir,
            output_dir=config.cleaned_data_output_dir,
            input_dir=config.output_dir,
        ),
    ]
)

pipe.run()
