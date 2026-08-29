import time
import logging
from functools import wraps


logger = logging.getLogger('partition')


class BenchmarkTags:
    def __init__(self, tags: str = " - "):
        self.tags = tags

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            ex_time = end_time - start_time
            h_time = ex_time / 60 / 60
            d_time = h_time / 24
            _args = ""
            if args:
                _args = f"[{args}]"
            _kwargs = ""
            if kwargs:
                _kwargs = f"[{kwargs}]"
            logger.info(f"[{func.__name__}][{self.tags}]{_args}{_kwargs} "
                        f"Execution time: {ex_time:.6f} seconds ({h_time:.2f} hours, {d_time:.2f} days)")
            return result
        return wrapper


def benchmark(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        ex_time = end_time - start_time
        h_time = ex_time / 60 / 60
        d_time = h_time / 24
        _args = ""
        if args:
            _args = f"[{args}]"
        _kwargs = ""
        if kwargs:
            _kwargs = f"[{kwargs}]"
        logger.info(f"[{func.__name__}]{_args}{_kwargs} Execution time: {ex_time:.6f} seconds ({h_time} hours, {d_time} days)")
        return result
    return wrapper

