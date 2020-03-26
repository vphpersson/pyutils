from dataclasses import is_dataclass
from typing import Any, Dict, get_origin, get_args
from abc import ABC

from pyutils.my_string import to_snake_case


class JsonDataclass(ABC):

    @classmethod
    def from_json(cls, **kwargs: Dict[str, Any]):

        prepared_kwargs: Dict[str, Any] = {}

        for key, value in kwargs.items():
            snake_cased_key: str = to_snake_case(key)
            annotated_value_type = cls.__annotations__[snake_cased_key]

            if is_dataclass(annotated_value_type) and issubclass(annotated_value_type, JsonDataclass):
                prepared_kwargs[snake_cased_key] = annotated_value_type.from_json(**value)
            elif get_origin(annotated_value_type) is list:
                # TODO: What about a list of lists, und so weiter...?
                list_annotated_value_type = get_args(annotated_value_type)
                if len(list_annotated_value_type) != 1:
                    raise NotImplementedError
                list_annotated_value_type = list_annotated_value_type[0]

                if is_dataclass(list_annotated_value_type) and issubclass(list_annotated_value_type, JsonDataclass):
                    prepared_kwargs[snake_cased_key] = [
                        list_annotated_value_type.from_json(**element_kwargs)
                        for element_kwargs in value
                    ]
                else:
                    prepared_kwargs[snake_cased_key] = value
            else:
                prepared_kwargs[snake_cased_key] = value

        return cls(**prepared_kwargs)
