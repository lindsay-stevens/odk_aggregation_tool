import unittest
from tests.aggregation import FixturePaths
from odk_aggregation_tool.aggregation import readers


class TestODKInstanceAggregate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fixtures = FixturePaths()
        cls.instances_root = cls.fixtures.files['instances']
        cls.read_xml = list(readers.read_xml_files(root_dir=cls.instances_root))
        cls.xlsform_root = cls.fixtures.files['xlsforms']
        cls.read_xlsform = list(
            readers.read_xlsform_definitions(root_dir=cls.xlsform_root))

    def test_read_xml_files(self):
        """Should locate all 15 test xml files in the folder and zip files."""
        expected = 15
        observed = self.read_xml
        self.assertEqual(expected, len(observed))

    def test_read_xlsform_definitions(self):
        """Should return list of dicts containing xform definitions."""
        observed = self.read_xlsform
        self.assertEqual(observed[0]['start']['type'], 'start')
        self.assertEqual(observed[1]['@settings']['form_id'], 'R1302_BEHAVE')

    def test_flatten_dict_leaf_nodes(self):
        """Should return a single-level dict with the leaf node key/values"""
        input_dict = {
            'k1': 'v1',
            'k2': {'k3': 'v3', 'k4': None},
            'k5': [
                {'k6': 6, 'k7': 7},
                {'k8': 'v8', 'k9': {'k10': 10}},
                {'k12': [{'k13': '13'}, {'k14': 14}]}
            ]}
        expected = {'k1': 'v1', 'k3': 'v3', 'k4': None, 'k6': 6, 'k7': 7,
                    'k8': 'v8', 'k10': 10, 'k13': '13', 'k14': 14}
        observed = readers.flatten_dict_leaf_nodes(input_dict)
        self.assertDictEqual(expected, observed)
