from abc import ABC
from typing import Any


class ParsingError(Exception, ABC):
    def __init__(
        self,
        message_header: str,
        observed_value: Any,
        expected_value: Any,
        expected_label: str = 'Expected'
    ):
        super().__init__(
            f'{message_header} '
            f'Observed {observed_value}. '
            f'{expected_label} {expected_value}.'
        )
