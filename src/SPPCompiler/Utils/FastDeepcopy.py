from enum import Enum
from fastenum import Enum as FastEnum


def fast_deepcopy[T](value: T) -> T:
    """
    Pattern-matching implementation of fast_deepcopy.

    :param value: The object to be copied.
    :return: The copied object.
    """

    match value:
        case None | int() | float() | str() | bool() | bytes() | complex() | range() | type() | Enum() | FastEnum():
            # If the value is a primitive type, copy it directly.
            return value

        case list():
            # If the value is a list, create a new list and copy each element.
            return [fast_deepcopy(item) for item in value]

        case dict():
            # If the value is a dictionary, create a new dictionary and copy each key-value pair.
            return {key: fast_deepcopy(val) for key, val in value.items()}

        case tuple():
            # If the value is a tuple, create a new tuple and copy each element.
            return tuple(fast_deepcopy(item) for item in value)

        case set():
            # If the value is a set, create a new set and copy each element.
            return {fast_deepcopy(item) for item in value}

        case frozenset():
            # If the value is a frozenset, create a new frozenset and copy each element.
            return frozenset(fast_deepcopy(item) for item in value)

        case memoryview():
            # If the value is a memoryview, create a new memoryview and copy each element.
            return memoryview(value.tobytes())

        case _ if hasattr(value, "__deepcopy__"):
            # If the value has a __deepcopy__ method, call it.
            return value.__deepcopy__()

        case _ if hasattr(value, "__slots__"):
            # If the value has __slots__, create a new instance and copy each slot.
            out = type(value)()
            for name in value.__slots__:
                setattr(out, name, fast_deepcopy(getattr(value, name)))
            return out

        case _ if hasattr(value, "__dict__"):
            # If the value has its own __dict__, recursively copy it.
            out = type(value)()
            for name, attr in value.__dict__.items():
                setattr(out, name, fast_deepcopy(attr))
            return out

        case _:
            raise TypeError(f"Unsupported type: {type(value)}")


__all__ = ["fast_deepcopy"]
