import abc
from conflex.config_dict import ConfigDict


class ConfigLoader(abc.ABC):
    """
    Base class for configuration loaders. Configuration loaders are used to load a configuration dictionary from
    any type of configuration input (files, environment variables and so on).
    """

    @abc.abstractmethod
    def load(self) -> ConfigDict:
        """
        Loads the configuration and returns it as a ConfigDict object.
        :return: A ConfigDict object that represents the configuration.
        """
        ...
