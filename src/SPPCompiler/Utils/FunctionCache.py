"""
This module provides a modified version of functools.cache and functools.cache_property. It allows for the tracking of
all functions decorated wth these 2 decorators, such that the caches can all be cleared from one point in the program. A
registry is used to track all caches.
"""

from __future__ import annotations

import functools
from typing import Callable


class FunctionCache:
    """
    A class that provides a cache for functions and properties.
    """

    _cache: list[Callable] = []
    _cache_property: list[functools.cached_property] = []

    @staticmethod
    def cache[T](function: Callable[[...], T]) -> Callable[[...], T]:
        cached_function = functools.cache(function)
        FunctionCache._cache.append(cached_function)
        return cached_function

    @staticmethod
    def cache_property[T](function: Callable[[...], T]) -> functools.cached_property:
        cached_function = functools.cached_property(function)
        FunctionCache._cache_property.append(cached_function)
        return cached_function

    @staticmethod
    def clear_all_caches() -> None:
        """
        Clear all caches.
        """
        for cache in FunctionCache._cache:
            cache.cache_clear()

        for cache_property in FunctionCache._cache_property:
            del cache_property
