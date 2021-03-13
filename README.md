# ConFlex

A flexible configuration manager for Python applications.

## Features

This library aims at being a one-stop shop for configuration management.

Features:

* Attribute-based access to configuration variables.
* Use any source format for configurations: this library can handle environment variables, YAML files, INI files, etc.
  All formats can be used together in the same project.
* Config merging: Merge configurations from different sources based on a user-defined ranking.
* Lazy loading: Configurations are not loaded at import time, making it possible to load only parts of the configuration
  for specific use cases.

## Getting started

Let's say that you have a `config.yaml` configuration file at the root of your project that looks like this:

```yaml
# config.yaml
api:
  DISPLAY_VERSION: 1.0.0

db:
  HOST: localhost
  USER: postgres
  PASSWORD: postgres

flask:
  DEBUG: False
```

Create a `config.py` file at the root of your project.

```python
# config.py
from conflex import ConfigStore
from conflex.backends.yaml import YamlConfigLoader

config_store = ConfigStore()
config_store.add(namespace="base", loader=YamlConfigLoader("config.yaml"))
```

You can now import your configuration from any project file:
```python
from config import config_store

display_version = config_store.api.DISPLAY_VERSION  # will fetch "1.0.0"
```

## Multiple configurations

This library handles configuration merging by default.
Let's say that you have a `config-override.yaml` file that redefines some variables for your specific project:

```yaml
# config-override.yaml
db:
  HOST: my-remote-db.hostname.com
  USER: user
  PASSWORD: super-secure-password
```

To merge the two configurations, you only need to add another loader to your `config.py` file:

```python
config_store = ConfigStore()
config_store.add(namespace="base", loader=YamlConfigLoader("config.yaml"))
config_store.add(namespace="override", loader=YamlConfigLoader("config-override.yaml"))
```

Note that the order is important: loaders are added from lower to higher ranking.
Variables set in the "base" configuration that are also defined in the "override" file will be set to the values
defined in the latter file. For example:

```python
db_host = config_store.db.HOST  # Will now return "my-remote-db.hostname.com" instead of "localhost"
```

What if you want to access the value of one specific configuration file?
That's what the `namespace` parameter is for.
You can access the values of a specific configuration file by using the following syntax:

```python
base_db_host = config_store["base"].db.HOST # Will fetch "localhost"
```

## Lazy loading

Configurations are not loaded immediately when calling the `ConfigStore.add` method.
Configuration values are loaded when either:

* the user makes an access to the merged config (`config_store.db.HOST`)
* the user accesses the config by its namespace (`config_store["base"].db.HOST`).

The second case can be useful for cases where you need to access parts of the configuration to load the rest,
for example when fetching secrets.
In the following example, only the base config file will be loaded.
It does not matter that the `secrets.yaml` does not exist.

```python
config_store = ConfigStore()
config_store.add(namespace="base", loader=YamlConfigLoader("config.yaml"))
config_store.add(namespace="secrets", loader=YamlConfigLoader("secrets.yaml"))
```

```python
# fetch_secrets.py

from config import config_store

vault_name = config_store["base"].secrets.VAULT_NAME
... # Fetch secrets.yaml from your key vault
```

## Typical use cases

### Base config, secrets and override by environment variables

A lot of applications have at least 3 layers of configuration:

* A base configuration file with static configuration options (also called "sane" defaults)
* A file containing secrets such as passwords, SSH keys etc.
* An override of all configuration/secret values by environment variables.

The following example loads the base configuration, overrides values specified in the secrets file and allows
the user to override any configuration option by specifying environment variables prefixed by `CONFIG__`.

Example, if your base config contains the following key:
```yaml
db:
  HOST: localhost
```

You can override it by specifying an environment variable named `CONFIG__DB__HOST`.

```python
from conflex import ConfigStore
from conflex.backends.env import EnvConfigLoader
from conflex.backends.yaml import YamlConfigLoader

config_store = ConfigStore()
config_store.add("base", YamlConfigLoader(config_file_path="base-config.yaml"))
config_store.add("secrets", YamlConfigLoader(config_file_path="secrets.yaml"))
config_store.add("env", EnvConfigLoader(prefix="CONFIG__", separator="__"))
```

## Configuration style

By default, `config-store` encourages the user to define his configuration variables with lowercase paths / namespaces
and uppercase names.
For example, if you want to store the version of your API in a config store, the call to this variable should look
like `config_store.api.VERSION`.
Using uppercase strings for configuration names allows to disambiguate between actual configuration and intermediate
configuration dictionaries.
Depending on the loader, this convention is used by default (ex: `EnvConfigLoader`) or must be respected
by the user when defining configuration files (ex: `YamlConfigLoader`).
Note that the user is free to choose another convention by using the loader path/key formatter arguments.

## Future work

This project intends to be as extensible as possible.
All the following features can be implemented by anyone.
If you are interested in contributing, clone the repository and submit a PR!

### Support for more file formats

* INI
* JSON

### Support for command-line arguments

ConFlex already supports overriding config file values by environment variables using the `EnvConfigLoader`.


### Support for dynamic configurations

Some configurations can be reloaded during the lifetime of the application.
Such configurations could be supported by adding a reload mechanism to the library.