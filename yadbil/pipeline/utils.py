from yadbil.data.mining.telegram import TELEGRAM_STEPS
from yadbil.data.processing import TEXT_STEPS
from yadbil.pipeline.creds import CREDS
from yadbil.search import SEARCH_STEPS


ALL_STEPS = [*TELEGRAM_STEPS, *TEXT_STEPS, *SEARCH_STEPS]

STEPS_MAPPING = {step.__name__: step for step in ALL_STEPS}
CREDS_MAPPING = {creds.__name__: creds for creds in CREDS}
