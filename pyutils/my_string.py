from re import compile as re_compile

_CAMEL_CASED_LETTER_PATTERN = re_compile(pattern=r'(?<=.)((?<=[a-z])[A-Z]|[A-Z](?=[a-z]))')


def to_snake_case(string: str) -> str:
    """
    Convert a string into a snake-cased representation.

    :param string: A camel-, Pascal-, or kebab-cased string.
    :return: A snake-cased representation of the provided string.
    """

    return _CAMEL_CASED_LETTER_PATTERN.sub(repl=lambda match: f'_{match.group(0)}', string=string) \
        .replace('-', '_') \
        .lower()
