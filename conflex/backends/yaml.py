from functools import reduce
from typing import Optional, cast

import yaml

from conflex.config_dict import ConfigDict, merge_configs
from conflex.config_loader import ConfigLoader
from conflex.exc import ConfigLoaderException


class YamlConfigLoader(ConfigLoader):
    """
    YAML configuration loader. Loads configuration from a YAML file.
    """

    def __init__(self, config_file_path: str, help_msg: Optional[str] = None):
        """
        Instantiates the YAML configuration loader.

        :param config_file_path: Path to the YAML file.
        :param help_msg: Optional help message to display if the file is not found.
        """
        self.config_file_path = config_file_path
        self.help_msg = help_msg

    def load(self) -> ConfigDict:
        """
        Loads the configuration from the YAML file.

        :return: The YAML file as a ConfigDict object.
        :raise: A ConfigLoaderException if the file does not exist.
        """
        config_file_path = self.config_file_path

        try:
            with open(config_file_path) as f:
                config = yaml.safe_load(f) or {}

        except (FileNotFoundError, PermissionError) as e:
            err_msg = f"'{config_file_path}': file not found."
            if self.help_msg:
                err_msg += "\n" + self.help_msg
            raise ConfigLoaderException(err_msg) from e

        except yaml.YAMLError as e:
            raise ConfigLoaderException(f"'{config_file_path}' is not a valid YAML file.") from e

        return cast(ConfigDict, reduce(merge_configs, (ConfigDict(), config)))

    def __repr__(self):
        return f"YAML config loader - config file: '{self.config_file_path}'"
