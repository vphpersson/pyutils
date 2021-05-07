#!/usr/bin/env python

from typing import Type
from json import load
from sys import stderr

from pyutils.cli import MakeDataclassArgumentParser
from pyutils.my_dataclasses import dataclass_to_code, dict_to_dataclass


def main():
    args: Type[MakeDataclassArgumentParser.Namespace] = MakeDataclassArgumentParser().parse_args()

    json_data = load(fp=args.input_file)

    if isinstance(json_data, list):
        print('The input data is a list; using the first element.', file=stderr)

        if json_data:
            print('The input data is an empty list.', file=stderr)
            exit(1)

        json_data = json_data[0]

    if not isinstance(json_data, dict):
        print(f'The input data is not a JSON object, but {type(json_data)}', file=stderr)
        exit(1)

    print(
        dataclass_to_code(
            dataclass_class=dict_to_dataclass(
                obj=json_data,
                class_name=args.class_name
            )
        )
    )


if __name__ == '__main__':
    main()
