from typing import Dict, Any, Pattern
from re import compile as re_compile, sub as re_sub, escape as re_escape

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


def text_align_delimiter(text: str, delimiter: str = ': ', put_non_match_after_delimiter: bool = True) -> str:
    """
    Align a multi-line text around a delimiter.

    :param text: The text to be aligned.
    :param delimiter: The delimiter to align around.
    :param put_non_match_after_delimiter: Whether lines in the text not having the delimiter should be put after the
        alignment position.
    :return: The input text aligned around the specified delimiter.
    """

    max_delimiter_pos: int = max(
        line.find(delimiter)
        for line in text.splitlines()
    )

    return '\n'.join(
        (
            (line[:delimiter_pos].rjust(max_delimiter_pos) + line[delimiter_pos:])
            if (delimiter_pos := line.find(delimiter)) != -1 else (
                (' ' * (max_delimiter_pos + len(delimiter)) + line) if (line and put_non_match_after_delimiter) else line
            )
        )
        for line in text.splitlines()
    )


def expand_var(
    string: str,
    expand_map: Dict[str, Any],
    var_char: str = '%',
    exception_on_unexpanded: bool = False
) -> str:
    """
    Expand the variables in a string given a map.

    If an encountered variable name is not in provided map, the function can either ignore it, leaving
    the variable reference in-place, or raise an exception.

    Each encountered variable name is transformed to lowercase prior to the lookup in `expand_map`, thus all lookup
    keys (variable names) in `expand_map` should lowercase.

    :param string: The string to be expanded.
    :param expand_map: A name-to-value map of variable names and their corresponding values.
    :param var_char: A character that surrounds the variable names.
    :param exception_on_unexpanded: Raise an exception if an variable name in the string is not in the map.
    :return: The variable-expanded string.
    """

    var_char: str = re_escape(var_char)
    var_pattern: Pattern = re_compile(f'{var_char}(?P<variable_name>[^%]+){var_char}')

    search_start_offset = 0
    while match := var_pattern.search(string=string, pos=search_start_offset):
        var_pos_start, var_pos_end = match.span(0)

        variable_name: str = match.groupdict()['variable_name'].lower()
        if variable_name in expand_map:
            expanded_head: str = string[:var_pos_start] + str(expand_map[variable_name])
            string: str = expanded_head + string[var_pos_end:]
            search_start_offset: int = len(expanded_head)
        elif exception_on_unexpanded:
            raise KeyError(f'The variable name {variable_name} is not in the expand map.')
        else:
            search_start_offset: int = var_pos_end

    return string
