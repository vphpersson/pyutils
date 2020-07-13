from sys import stdout, stdin
from struct import pack as struct_pack, unpack as struct_unpack
from typing import Union, Optional

NUM_MESSAGE_LENGTH_SPECIFIER_BYTES = 4


def _make_outgoing_message_bytes(message_bytes: bytes) -> bytes:
    """
    Format the an outgoing message's bytes.

    The message bytes are preceded by bytes indicating the length of the message.

    :param message_bytes: Unformatted message bytes.
    :return: Formatted message bytes.
    """

    return struct_pack('=I', len(message_bytes)) + message_bytes


def _write_message_bytes(message_bytes: bytes) -> int:
    write_return_value: int = stdout.buffer.write(message_bytes)
    stdout.buffer.flush()
    return write_return_value


def write_message(message: Union[bytes, str], encoding: str = 'utf-8') -> int:
    """
    Write a message to be read by the browser extension to stdout.

    :param message: The message to be written, as bytes or a string.
    :param encoding: The encoding to be used in case the message is a string.
    :return: The number of bytes written.
    """

    return _write_message_bytes(
        message_bytes=_make_outgoing_message_bytes(
            message_bytes=message.encode(encoding=encoding) if isinstance(message, str) else message
        )
    )


def read_message() -> Optional[bytes]:
    """
    Read a message passed by the browser extension from stdin.

    :return: The bytes constituting the message passed by the browser extension.
    """

    message_length_bytes: bytes = stdin.buffer.read(NUM_MESSAGE_LENGTH_SPECIFIER_BYTES)
    if not message_length_bytes:
        return None

    return stdin.buffer.read(struct_unpack('=I', message_length_bytes)[0])
