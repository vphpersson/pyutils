from dataclasses import is_dataclass, fields, make_dataclass
from typing import Any, Dict, get_origin, get_args, Optional, List
from abc import ABC
from uuid import uuid4

from pyutils.my_string import to_snake_case, to_pascal_case


class JsonDataclass(ABC):

    @classmethod
    def from_json(cls, json_object: Dict[str, Any]):

        prepared_kwargs: Dict[str, Any] = {}

        for key, value in json_object.items():
            snake_cased_key: str = to_snake_case(string=key)
            annotated_value_type = cls.__annotations__[snake_cased_key]

            if is_dataclass(annotated_value_type) and issubclass(annotated_value_type, JsonDataclass):
                prepared_kwargs[snake_cased_key] = annotated_value_type.from_json(json_object=value)
            elif get_origin(annotated_value_type) is list:
                
                list_annotated_value_type = get_args(annotated_value_type)
                if len(list_annotated_value_type) != 1:
                    raise NotImplementedError

                list_annotated_value_type = list_annotated_value_type[0]

                if is_dataclass(list_annotated_value_type) and issubclass(list_annotated_value_type, JsonDataclass):
                    prepared_kwargs[snake_cased_key] = [
                        list_annotated_value_type.from_json(json_object=element_kwargs)
                        for element_kwargs in value
                    ]
                else:
                    prepared_kwargs[snake_cased_key] = value
            else:
                prepared_kwargs[snake_cased_key] = value

        return cls(**prepared_kwargs)


def dict_to_dataclass(obj, class_name: Optional[str] = None):

    if isinstance(obj, dict):
        return make_dataclass(
            cls_name=(class_name or str(uuid4()).split('-')[-1]).replace('-', ''),
            fields=[(to_snake_case(string=name), dict_to_dataclass(value, name)) for name, value in obj.items()]
        )
    elif isinstance(obj, (list, tuple)):
        type_set = set()
        for element in obj:
            res = dict_to_dataclass(element)
            type_set.add(
                tuple((field.name, field.type) for field in fields(res)) if is_dataclass(obj=res) else res
            )

        # if not type_set:
        return List[Any]
        # elif len(type_set) != 1:
        #     raise ValueError

        # return next(iter(type_set))

    elif isinstance(obj, (str, int, float)):
        return type(obj)
    elif obj is None:
        return Any
    else:
        raise ValueError


def dataclass_to_code(dataclass_class):
    """

    :param dataclass_class:
    :return:
    """

    return '\n'.join(dataclass_to_code(field.type) for field in fields(dataclass_class) if is_dataclass(field.type)) + '\n\n' + (

        f'@dataclass\n'
        f'class {to_pascal_case(string=dataclass_class.__name__)}:\n    '
        + ('\n    '.join(
            f'{to_snake_case(string=field.name)}: {(to_pascal_case(string=field.type.__name__) if is_dataclass(field.type) else field.type.__name__)  if isinstance(field.type, type) else field.type}'
            for field in fields(dataclass_class)
        ) or 'pass')
    )
