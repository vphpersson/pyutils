from typing import Protocol, NewType, Union, ByteString, SupportsBytes, SupportsInt


class SupportsStr(Protocol):
    def __str__(self) -> str:
        pass


ByteLike = NewType('ByteLike', Union[ByteString, SupportsBytes])
IntLike = NewType('IntLike', Union[int, SupportsInt])
StrLike = NewType('StrLike', Union[str, SupportsStr])
