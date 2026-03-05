"""
Retry Handler

Decorator for handling transient errors with exponential backoff.
"""

import time
import logging
from functools import wraps
from typing import Callable, Type, Optional

logger = logging.getLogger(__name__)


class TransientError(Exception):
    """Exception for transient/retryable errors"""
    pass


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (TransientError,),
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exceptions: Tuple of exception types to retry
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt, re-raise
                        logger.error(
                            f'{func.__name__} failed after {max_attempts} attempts: {e}'
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    
                    logger.warning(
                        f'{func.__name__} attempt {attempt + 1} failed: {e}. '
                        f'Retrying in {delay}s...'
                    )
                    
                    time.sleep(delay)
                except Exception as e:
                    # Non-retryable error
                    logger.error(f'{func.__name__} failed with non-retryable error: {e}')
                    raise
            
            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator
