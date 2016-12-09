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
