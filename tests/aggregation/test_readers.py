import unittest
from tests.aggregation import FixturePaths
from odk_aggregation_tool.aggregation import readers
from collections import OrderedDict


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
        input_dict = OrderedDict([
            ('k1', 'v1'),
            ('k2', OrderedDict([
                ('k3', 'v3'),
                ('k4', None)
            ])),
            ('k5', [
                OrderedDict([('k6', 6), ('k7', 7)]),
                OrderedDict([
                    ('k8', 'v8'),
                    ('k9', OrderedDict([('k10', 10)]))]),
                OrderedDict([
                    ('k12', [
                        OrderedDict([('k13', '13')]),
                        OrderedDict([('k14', 14)])
                     ])
                ])]
             )
        ])
        expected = OrderedDict([
            ('k1', 'v1'), ('k3', 'v3'), ('k4', None), ('k6', 6), ('k7', 7),
            ('k8', 'v8'), ('k10', 10), ('k13', '13'), ('k14', 14)])
        observed = readers.flatten_dict_leaf_nodes(input_dict)
        self.assertDictEqual(OrderedDict(expected), observed)

    def test_read_xlsform_definitions_handles_bad_xlsx_file(self):
        """Should not choke on invalid XLSX files."""
        logger_name = "odk_aggregation_tool.aggregation.readers"
        with self.assertLogs(logger=logger_name, level="INFO") as logs:
            list(readers.read_xlsform_definitions(
                root_dir=self.fixtures.files["xlsform_phony"]))
        self.assertIn("invalid XLSX", logs.output[0])

    def test_read_xlsform_definitions_handles_non_xlsform_xlsx_files(self):
        # TODO: add test fixture and test for this
        pass
