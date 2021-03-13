import unittest

from conflex.config_store import ConfigDict, merge_configs


class ConfigMergeTest(unittest.TestCase):
    def test_merge_non_overlapping_dicts(self):
        dict1 = {"a": {"x": 1, "y": 2}}
        dict2 = {"b": {"abc": 1, "xyz": 2}}

        merged_dict = merge_configs(dict1, dict2)

        self.assertEqual(merged_dict["a"], dict1["a"])
        self.assertEqual(merged_dict["b"], dict2["b"])

    def test_merge_overlapping_dicts(self):
        dict1 = {"a": {"x": 1, "y": 2}}
        dict2 = {"a": {"x": 42, "z": 3}}

        merged_dict = merge_configs(dict1, dict2)

        self.assertEqual(dict2["a"]["x"], merged_dict["a"]["x"])
        self.assertEqual(dict1["a"]["y"], merged_dict["a"]["y"])
        self.assertEqual(dict2["a"]["z"], merged_dict["a"]["z"])

    def test_merge_conflicting_types(self):
        dict1 = {"a": {"x": 1, "y": 2}}
        dict2 = {"a": {"x": {"y": "z"}}}

        self.assertRaises(Exception, merge_configs, dict1, dict2)
        self.assertRaises(Exception, merge_configs, dict2, dict1)

    def test_merge_no_inplace_modification(self):
        """
        Tests that the original dictionaries are not modified when setting the `inplace` flag to False.
        """
        dict1 = {"a": {"x": 1, "y": 2}}
        dict2 = {"b": {"abc": 1, "xyz": 2}}

        dict1_copy = dict1.copy()
        dict2_copy = dict2.copy()

        merged_dict = merge_configs(dict1_copy, dict2_copy, inplace=False)

        self.assertEqual(merged_dict["a"], dict1["a"])
        self.assertEqual(merged_dict["b"], dict2["b"])
        self.assertEqual(dict1_copy, dict1)
        self.assertEqual(dict2_copy, dict2)

    def test_merge_inplace(self):
        """
        Tests that:
        * the base dictionary is modified
        * the second dictionary is left intact
        when setting the `inplace` flag to True.
        """
        dict1 = {"a": {"x": 1, "y": 2}}
        dict2 = {"b": {"abc": 1, "xyz": 2}}

        dict1_copy = dict1.copy()
        dict2_copy = dict2.copy()

        merged_dict = merge_configs(dict1_copy, dict2_copy, inplace=True)

        self.assertEqual(merged_dict["a"], dict1["a"])
        self.assertEqual(merged_dict["b"], dict2["b"])
        self.assertEqual(merged_dict, dict1_copy)
        self.assertEqual(dict2_copy, dict2)

    def test_config_dict_attribute_lookup(self):
        value = "i-am-a-config-value-and-i-dance-dance-dance"
        dict1 = ConfigDict()
        dict2 = {"a": value}

        merged_dict = merge_configs(dict1, dict2)
        self.assertEqual(value, merged_dict.a)

    def test_config_dict_deep_attribute_lookup(self):
        value = "we are inside a dream within a dream within a Python unit test"
        dict1 = ConfigDict()
        dict2 = {"a": {"b": {"c": {"d": value}}}}

        merged_dict = merge_configs(dict1, dict2)
        self.assertEqual(value, merged_dict.a.b.c.d)
