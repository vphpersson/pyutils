from argparse import FileType, ArgumentDefaultsHelpFormatter
from sys import stdin

from pyutils.argparse.typed_argument_parser import TypedArgumentParser


class MakeDataclassArgumentParser(TypedArgumentParser):

    class Namespace:
        input_file: FileType
        class_name: str

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **(
                dict(
                    description='Turn a JSON object into a Python `dataclass` definition.',
                    formatter_class=ArgumentDefaultsHelpFormatter
                ) | kwargs
            )
        )

        self.add_argument(
            'input_file',
            type=FileType('r'),
            help='A file from which to read a JSON object',
            default=stdin,
            nargs='?'
        )

        self.add_argument(
            '--class-name',
            type=str,
            help='The name of the dataclass to be produced.',
            default='A'
        )
