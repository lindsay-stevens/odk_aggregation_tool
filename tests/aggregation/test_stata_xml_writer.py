import unittest
from tests.aggregation import FixturePaths
from odk_aggregation_tool.aggregation import stata_xml_writer
import os


class TestStataXMLWriter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fixtures = FixturePaths()
        cls.instances_root = cls.fixtures.files['instances']
        cls.xlsform_root = cls.fixtures.files['xlsforms']

    def test_to_stata_xml(self):
        xml_document = stata_xml_writer.to_stata_xml(
            xlsform_path=self.xlsform_root, instances_path=self.instances_root)

        #output_path = os.path.join(self.fixtures.here, 'test.xml')
        #with open(output_path, 'w') as out_doc:
        #    out_doc.write(xml_document)
        # xmluse path , doctype(dta)

    def test_collate_xlsforms_by_form_id_produces_2_form_defs(self):
        forms = stata_xml_writer.collate_xlsforms_by_form_id(
            xlsform_path=self.xlsform_root)
        self.assertEqual({"Q1302_BEHAVE", "R1302_BEHAVE"}, set(forms))

    def test_prepare_xlsform_metadata_populates_metadata(self):
        xlsform = stata_xml_writer.collate_xlsforms_by_form_id(
            xlsform_path=self.fixtures.files["simplest_xlsform"])
        observed = stata_xml_writer.prepare_xlsform_metadata(
            form_def=xlsform["simplest_xlsform"])
        self.assertEqual(
            {"value_labels", "var_choices", "var_formats", "var_labels",
             "var_names", "var_types"}, set(observed))

        # TODO: finish these unit tests for processing by form_id
