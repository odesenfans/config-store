import os
import unittest

from conflex.backends.yaml import YamlConfigLoader
from conflex.config_store import ConfigStore

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class YamlConfigLoaderTest(unittest.TestCase):
    def test_loader(self):
        loader = YamlConfigLoader(config_file_path=os.path.join(FIXTURES_DIR, "config_fixture.yaml"))
        config_dict = loader.load()
        self.assertEqual(3.141592, config_dict.app.VERSION)
        self.assertEqual("localhost", config_dict.db.HOST)
        self.assertEqual("admin", config_dict.db.USER)
        self.assertEqual("admin", config_dict.db.PASSWORD)

    def test_config_store(self):
        config_store = ConfigStore()
        config_store.add("base", YamlConfigLoader(config_file_path=os.path.join(FIXTURES_DIR, "config_fixture.yaml")))

        self.assertEqual(3.141592, config_store.app.VERSION)
        self.assertEqual("localhost", config_store.db.HOST)
        self.assertEqual("admin", config_store.db.USER)
        self.assertEqual("admin", config_store.db.PASSWORD)
