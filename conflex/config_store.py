"""
Configuration management system.
"""

from functools import reduce
from typing import Any

from conflex.config_dict import ConfigDict, merge_configs
from conflex.config_loader import ConfigLoader
from conflex.exc import ConfigStoreException


class ConfigStore:
    """
    Class to load and store configurations from various sources.
    This class acts as the single entry point to configuration variables from applicative code.
    It provides access to different configurations, possibly of different formats, stores and provides the ability
    to either retrieve the configurations individually or merge them together.

    Individual configurations can be retrieved by indexing the config_store object:
    >>> config_store = ConfigStore()
    >>> config_store.add("secrets", YamlConfigLoader("secrets.yaml"))
    >>> db_host = config_store["secrets"].db.host

    The merged configuration is accessible by attributes:
    >>> my_config = config_store.db.host
    """

    def __init__(self):
        self.merged_config = None
        self.loaders = {}
        self.configs = {}

    def add(self, namespace: str, loader: ConfigLoader) -> None:
        """
        Adds a configuration source to the store.

        Configurations can be added as long as the config store is not in use.

        :param namespace: Configuration namespace.
        :param loader: Configuration loader. Used to load the configuration at runtime.
        :raise: A ConfigStoreException if the config store is already in use.
        """
        if self.merged_config is not None:
            raise ConfigStoreException("Cannot add new configurations after the first access to the config store.")
        if namespace in self.loaders:
            raise ConfigStoreException(
                f"A loader for configuration namespace '{namespace}' is already registered ({loader})."
            )

        self.loaders[namespace] = loader
        self.configs[namespace] = None

    def _load_all_configs(self) -> None:
        """
        Loads all configurations that were not yet loaded.
        """
        for namespace, config in self.configs.items():
            if config is None:
                self.configs[namespace] = self.loaders[namespace].load()

    def _merge_configs(self) -> ConfigDict:
        """
        Merges all the configurations in a single ConfigDict object. In case of conflict, the configurations that
        were added last take precedence.
        :return: The merged ConfigDict object.
        """
        self._load_all_configs()
        return reduce(merge_configs, (ConfigDict(), *self.configs.values()))

    def __getattr__(self, item: str) -> Any:
        if self.merged_config is None:
            self.merged_config = self._merge_configs()

        return getattr(self.merged_config, item)

    def __getitem__(self, namespace) -> ConfigDict:
        if self.configs[namespace] is None:
            self.configs[namespace] = self.loaders[namespace].load()

        return self.configs[namespace]
