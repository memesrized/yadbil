import functools
import time
from typing import Any, Callable, Optional, Tuple, Type

from yadbil.utils.logger import get_logger


logger = get_logger(__name__)


def retry_with_backoff(
    retries: int = 3,
    backoff_factor: float = 2.0,
    initial_delay: float = 30.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator that retries a function with exponential backoff.

    Args:
        retries: Maximum number of retries
        backoff_factor: Multiplier for delay between retries
        initial_delay: Initial delay in seconds
        exceptions: Tuple of exceptions to catch and retry
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception: Optional[Exception] = None

            for attempt in range(retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.debug(f"Function {func.__name__} succeeded after {attempt} retries")
                    return result
                except exceptions as e:
                    last_exception = e
                    if attempt == retries:
                        logger.error(f"Function {func.__name__} failed after {retries} retries with error: {str(e)}")
                        raise last_exception

                    logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt + 1}/{retries + 1}. "
                        f"Retrying in {delay:.2f}s. Error: {str(e)}"
                    )
                    time.sleep(delay)
                    delay *= backoff_factor

            if last_exception:
                raise last_exception

        return wrapper

    return decorator
