from typing import Callable, Iterable


def reduce[T](func: Callable[[T, T], T], iterable: Iterable[T], initial: T) -> T:
    """
    Reduce the iterable into a single value using the function and the initial value.
    """
    value = initial
    for item in iterable:
        value = func(value, item)
    return value
