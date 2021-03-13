from copy import deepcopy
from typing import Any
from typing import Dict, Mapping, TypeVar, Union

T = TypeVar("T", bound=Dict[str, Any])


def merge_configs(
    base_config: T, new_config_layer: Mapping[str, Any], path_from_root: str = "$.", inplace: bool = False
) -> T:
    """
    Merges two dictionaries recursively.

    In case of conflict, updates the values in base_config by the ones provided in new_config_layer.
    The returned object is of the same type as base_config, allowing to use subclasses of dict for specific
    use cases.
    This function is based on a (very) similar function in the contracts codebase.

    :param base_config: Base config dictionary.
    :param new_config_layer: New config dictionary.
    :param path_from_root: Current path inside the dictionary. Used for logging of errors as this function is recursive.
    :param inplace: Whether the base_config dictionary should be updated in place.
    :return: The merged configuration dictionary. This object is of the same type as base_config and is actually
             the same object as base_config if the inplace flag is set to True.
    """
    dict_type = type(base_config)
    new_config = base_config if inplace else deepcopy(base_config)

    for k, v in new_config_layer.items():
        if isinstance(v, dict):
            if k not in new_config:
                new_config[k] = dict_type()
            elif not isinstance(new_config[k], dict):
                raise Exception(
                    f"Invalid config merge at node {path_from_root}{k}. Base layer is not a dict, but "
                    f"was overwritten by a dictionary."
                )
            new_config[k] = merge_configs(
                dict_type(**new_config[k]), v, path_from_root=path_from_root + k + ".", inplace=True
            )

        else:
            if k in new_config and isinstance(new_config[k], dict):
                raise Exception(
                    f"Invalid config merge at node {path_from_root}{k}. Base layer is a dict, but "
                    f"was overwritten by a non-dictionary."
                )
            else:
                new_config[k] = new_config_layer[k]

    return new_config


def convert_to_bool(value_str: str) -> bool:
    """
    Converts string values to their boolean equivalents.
    :param value_str: Value string.
    :return: The boolean value represented by `value_str`, if any.
    :raise: A ValueError if it is not possible to convert the value string to bool.
    """
    conversion_dict = {"true": True, "t": True, "y": True, "false": False, "f": False, "n": False}
    try:
        return conversion_dict[value_str.lower()]
    except KeyError as e:
        raise ValueError(f"Not a boolean value: {value_str}") from e


def convert_str_value(value_str: str) -> Union[str, int, float, bool]:
    """
    Attempts to convert a string value to the most logical type.

    Supported types are bool, float and int.

    :param value_str: Value to convert, in string format.
    :return: The value in its real type, or as a string if no conversion is possible.
    """
    try:
        return convert_to_bool(value_str)
    except ValueError:
        pass

    try:
        return float(value_str)
    except ValueError:
        pass

    try:
        return int(value_str)
    except ValueError:
        return value_str


class ConfigDict(dict):
    """
    Dictionary that allows access to its values by attribute for convenience.
    """

    def __getattr__(self, item: str) -> Any:
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError(f"No such configuration variable or namespace: '{item}'") from e

    def cast_values(self) -> None:
        """
        Attempts to convert the leaf values of the dictionary to their real type.
        """
        for k, v in self.items():
            if isinstance(v, ConfigDict):
                v.cast_values()
            elif isinstance(v, str):
                self[k] = convert_str_value(v)
