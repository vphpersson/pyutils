from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace as ArgparseNamespace
from typing import Type, cast


class TypedNamespaceNameError(LookupError):
    def __init__(self, name: str):
        super().__init__(f'Name {name} not in typed namespace.')
        self.name = name


class _NamespaceMemberVerifier(type):
    def __setattr__(self, key, value):
        if key not in self.__annotations__:
            raise TypedNamespaceNameError(name=key)
        return super().__setattr__(key, value)


class _TypedArgparseNamespace(ArgparseNamespace, metaclass=_NamespaceMemberVerifier):
    pass


class TypedArgumentParser(ABC, ArgumentParser):

    @abstractmethod
    class Namespace:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.Namespace = cast(
            Type[ArgparseNamespace],
            type(
                self.Namespace.__name__,
                (_TypedArgparseNamespace,),
                {'__annotations__': self.Namespace.__annotations__}
            )
        )

    def parse_args(self, *args, **kwargs) -> Type[ArgparseNamespace]:
        return super().parse_args(*args, namespace=self.Namespace, **kwargs)
