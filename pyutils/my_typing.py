from typing import Protocol, NewType, Union, ByteString, SupportsBytes, SupportsInt, Any, get_args, runtime_checkable


@runtime_checkable
class SupportsStr(Protocol):
    def __str__(self) -> str:
        pass


_byte_like_union = Union[ByteString, SupportsBytes]
_int_like_union = Union[int, SupportsInt]
_str_like_union = Union[str, SupportsStr]

ByteLike = NewType('ByteLike', _byte_like_union)
IntLike = NewType('IntLike', _int_like_union)
StrLike = NewType('StrLike', _str_like_union)


def is_byte_like(value: Any) -> bool:
    """
    Test whether a value is byte-like.

    :param value: A value to be tested.
    :return: Whether the value is byte-like.
    """

    return isinstance(value, get_args(_byte_like_union))


def is_int_like(value: Any) -> bool:
    """
    Test whether a value is int-like.

    :param value: A value to be tested.
    :return: Whether the value is int-like.
    """

    return isinstance(value, get_args(_int_like_union))


def is_str_like(value: Any) -> bool:
    """
    Test whether a value is str-like.

    :param value: A value to be tested.
    :return: Whether the value is str-like.
    """

    return isinstance(value, get_args(_str_like_union))
