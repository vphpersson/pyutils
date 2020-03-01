from typing import Type, Set, Union, Optional, List
from argparse import Action, ArgumentParser, Namespace, FileType
from io import TextIOWrapper


def make_action_class(collection_name: str) -> Type[Action]:
    """
    Create an `argparse.Action` class that stores entries in a certain attribute in the `argparse` namespace.

    Supports entries in the form of strings and `argparse.FileType` file wrappers.

    :param collection_name: The name of the attribute in `argparse` namespace that is to store the entries.
    :return: A dynamically created custom `argparse.Action` class.
    """

    # NOTE: The name will not be unique.
    action_class = type(f'{collection_name}Action', (Action,), dict())

    def __call__(
        self,
        _: ArgumentParser,
        namespace: Namespace,
        values: Union[List[str], List[TextIOWrapper]],
        __: Optional[str] = None
    ) -> None:

        collected_set: Set[str] = getattr(namespace, collection_name, set())

        if isinstance(self.type, FileType):
            value_files: List[TextIOWrapper] = values
            values_to_be_added = (
                value.strip()
                for value_file in value_files
                for value in value_file.read().splitlines()
            )
        else:
            values_to_be_added = values

        collected_set.update(values_to_be_added)

        setattr(namespace, self.dest, values)
        setattr(namespace, collection_name, collected_set)

    setattr(action_class, '__call__', __call__)

    return action_class
