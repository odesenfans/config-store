import os
import unittest
from unittest import mock

from conflex.backends.env import EnvConfigLoader


class EnvConfigLoaderTest(unittest.TestCase):
    @mock.patch.dict(os.environ, {"CONF__DB_HOST": "localhost", "CONF__USER": "Claude", "CONF__PASSWORD": "hairdryer"})
    def test_prefix(self):
        loader = EnvConfigLoader(prefix="CONF__")
        config_dict = loader.load()

        self.assertEqual("localhost", config_dict["DB_HOST"])
        self.assertEqual("Claude", config_dict["USER"])
        self.assertEqual("hairdryer", config_dict["PASSWORD"])

    @mock.patch.dict(
        os.environ,
        {
            "CONF__DB_HOST": "localhost",
            "CONF__USER": "Claude",
            "CONF__API_CORE_MEMORY": "128M",
            "CONF__API_CORE_VERSION": "1.2.3",
        },
    )
    def test_separator(self):
        loader = EnvConfigLoader(prefix="CONF__", separator="_")
        config_dict = loader.load()

        self.assertEqual("localhost", config_dict.db.HOST)
        self.assertEqual("Claude", config_dict.USER)
        self.assertEqual("128M", config_dict.api.core.MEMORY)
        self.assertEqual("1.2.3", config_dict.api.core.VERSION)

    @mock.patch.dict(
        os.environ, {"CONF__INT": "42", "CONF__FALSE": "false", "CONF__TRUE": "TRUE", "CONF__FLOAT": "1.4142"}
    )
    def test_cast_values(self):
        loader = EnvConfigLoader(prefix="CONF__", separator="_")
        config_dict = loader.load()

        self.assertEqual(42, config_dict.INT)
        self.assertEqual(False, config_dict.FALSE)
        self.assertEqual(True, config_dict.TRUE)
        self.assertEqual(1.4142, config_dict.FLOAT)
