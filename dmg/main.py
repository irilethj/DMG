import functools
import time
from typing import Callable


def cache_result(func: Callable[[int], int]) -> Callable[[int], int]:
    cache: dict[int, int] = {}

    @functools.wraps(func)
    def wrapper(*args: int, **kwargs: int) -> int:
        if args:
            key: int = args[0]
        elif "user_id" in kwargs:
            key = kwargs["user_id"]
        else:
            raise ValueError("Must provide user_id")
        if key in cache:
            print(f"взят из кеша {cache[key]}")
            return cache[key]
        cache[key] = func(*args, **kwargs)
        print(f"взят из базы {cache[key]}")
        return cache[key]

    return wrapper


@cache_result
def get_user_data(user_id: int) -> int:
    time.sleep(2)
    return user_id
