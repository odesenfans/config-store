import os
from typing import Callable, Optional

from conflex.config_dict import ConfigDict
from conflex.config_loader import ConfigLoader


class EnvConfigLoader(ConfigLoader):
    """
    Environment variable configuration loader. Loads configuration from environment variables.
    """

    def __init__(
        self,
        prefix: str,
        separator: Optional[str] = None,
        cast_values: bool = True,
        path_formatter: Callable[[str], str] = lambda s: s.lower(),
        key_formatter: Callable[[str], str] = lambda s: s.upper(),
    ):
        """
        Instantiates the environment configuration loader.

        :param prefix: Environment variable prefix. The loader will only take into account the environment variables
                       that start with this prefix.
        :param separator: Optional separator. If specified, the loader will split variables names with this separator
                          and create a hierarchy. See the documentation of `load` for more information.
        :param cast_values: Whether the loader should attempt to cast values to the appropriate types. For example,
                            cast 1 to int or "false" to the False boolean value. The only supported conversion types
                            are boolean, floating-point numbers and integers.
        :param path_formatter: Formatting function to apply to "path" parts of the environment variable names.
                               The default is to set them to lowercase.
        :param key_formatter: Formatting function to apply to "path" parts of the environment variable names.
                              The default is to set them to uppercase.
        """
        self.prefix = prefix
        self.separator = separator
        self.cast_values = cast_values
        self.path_formatter = path_formatter
        self.key_formatter = key_formatter

    def load(self) -> ConfigDict:
        """
        Loads the configuration from environment variables.

        The usual pattern for environment variables is <prefix><path-1><sep>...<path-N><sep><key>.
        For example, an environment variable `CONF__API__VERSION` has the following characteristics:
        * prefix: "CONF__"
        * separator: "__"
        * path: "api"
        * key: "VERSION".

        Following the usual convention, such a variable would be loaded as `config_dict.api.VERSION`.
        The conversion to upper/lower case can be controlled with the `path_formatter`/`key_formatter` arguments of
        the constructor.

        :return: The environment configuration as a ConfigDict object.
        """
        config_dict = ConfigDict()

        for k, v in os.environ.items():
            if k.startswith(self.prefix):
                k = k[len(self.prefix) :]
                paths = k.split(self.separator) if self.separator else [k]

                d = config_dict
                for path in paths[:-1]:
                    formatted_path = self.path_formatter(path)
                    if formatted_path not in d:
                        d[formatted_path] = ConfigDict()
                    d = d[formatted_path]

                config_name = self.key_formatter(paths[-1])
                d[config_name] = v

        if self.cast_values:
            config_dict.cast_values()

        return config_dict

    def __repr__(self):
        return f"Environment config loader - prefix: '{self.prefix}' / separator '{self.separator}'"
