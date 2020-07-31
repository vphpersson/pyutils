from re import compile as re_compile, sub as re_sub

_CAMEL_CASED_LETTER_PATTERN = re_compile(pattern=r'(?<=.)((?<=[a-z])[A-Z]|[A-Z](?=[a-z]))')

_SNAKE_KEBAB_CASED_LETTER_PATTERN = re_compile(pattern=r'[-_]([A-Za-z])')


def uppercase_first_character(string: str) -> str:
    """

    :param string:
    :return:
    """

    return re_sub(pattern=r'^.', repl=lambda match: match.group(0).capitalize(), string=string)


def lowercase_first_character(string: str) -> str:
    """

    :param string:
    :return:
    """

    return re_sub(pattern=r'^.', repl=lambda match: match.group(0).lower(), string=string)


def to_snake_case(string: str) -> str:
    """
    Convert a string into a snake-cased representation.

    :param string: A camel-, Pascal-, or kebab-cased string.
    :return: A snake-cased representation of the provided string.
    """

    return _CAMEL_CASED_LETTER_PATTERN.sub(repl=lambda match: f'_{match.group(0)}', string=string.replace('-', '')) \
        .replace('-', '_') \
        .lower()


def to_pascal_case(string: str) -> str:
    """
    Convert a string into a Pascal-cased representation.

    :param string: A camel-, snake-, or kebab-cased string.
    :return: A Pascal-cased representation of the provided string.
    """

    return uppercase_first_character(
        string=_SNAKE_KEBAB_CASED_LETTER_PATTERN.sub(repl=lambda match: match.group(1).upper(), string=string)
    )


def to_camel_case(string: str) -> str:
    """
    Convert a string into a camel-cased representation.

    :param string: A Pascal-, kebab-, or snake-cased string.
    :return: A camel-cased representation of the provided string.
    """

    return lowercase_first_character(
        string=_SNAKE_KEBAB_CASED_LETTER_PATTERN.sub(repl=lambda match: match.group(1).upper(), string=string)
    )


def underline(string: str, underline_character: str = '=') -> str:
    """
    Underline a string with a sequence of character equal to the string's length.

    :param string: A string to be underlined.
    :param underline_character: The character which will compose the underline.
    :return: The input string underlined with the specified charater.
    """

    return f'{string}\n{len(string) * underline_character}'
