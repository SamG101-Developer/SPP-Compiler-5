none_type = type(None)
from enum import Enum


def fast_deepcopy[T](value: T) -> T:
    """
    Perform a fast deepcopy of a generic object, by copying all data members and
    recursively copying all nested objects.

    Types that still need implementing:
    * slice
    *

    :param value: The object to be copied.
    :return: The copied object.
    """

    if isinstance(value, (int, float, str, bool, bytes, complex, range, type, none_type, Enum)):
        # If the value is a primitive type, copy it directly.
        return value

    elif isinstance(value, list):
        # If the value is a list, create a new list and copy each element.
        return [fast_deepcopy(item) for item in value]

    elif isinstance(value, dict):
        # If the value is a dictionary, create a new dictionary and copy each key-value pair.
        return {key: fast_deepcopy(val) for key, val in value.items()}

    elif isinstance(value, tuple):
        # If the value is a tuple, create a new tuple and copy each element.
        return tuple(fast_deepcopy(item) for item in value)

    elif isinstance(value, set):
        # If the value is a set, create a new set and copy each element.
        return {fast_deepcopy(item) for item in value}

    elif isinstance(value, frozenset):
        # If the value is a frozenset, create a new frozenset and copy each element.
        return frozenset(fast_deepcopy(item) for item in value)

    elif isinstance(value, memoryview):
        # If the value is a memoryview, create a new memoryview and copy each element.
        return memoryview(value.tobytes())

    elif hasattr(value, "__deepcopy__"):
        # If the value has a __deepcopy__ method, call it.
        return value.__deepcopy__()

    elif hasattr(value, "__slots__"):
        # If the value has __slots__, create a new instance and copy each slot.
        out = type(value)()
        for name in value.__slots__:
            setattr(out, name, fast_deepcopy(getattr(value, name)))
        return out

    elif hasattr(value, "__dict__"):
        # If the value has its own __dict__, recursively copy it.
        out = type(value)()
        for name, attr in value.__dict__.items():
            setattr(out, name, fast_deepcopy(attr))
        return out

    else:
        raise TypeError(f"Unsupported type: {type(value)}")


__all__ = ["fast_deepcopy"]
