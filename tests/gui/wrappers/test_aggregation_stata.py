from tests.aggregation import FixturePaths
from odk_aggregation_tool.gui.wrappers import aggregation_stata
import unittest
from unittest.mock import MagicMock, patch


class TestAggregateStata(unittest.TestCase):

    def setUp(self):
        self.fixtures = FixturePaths()

    def test_run_generate_images_captures_normal_logs(self):
        """Should capture normal info logs."""
        xlsforms_path = self.fixtures.files["xlsforms"]
        xforms_path = self.fixtures.files["instances"]
        output_path = self.fixtures.dir

        mock_write = 'odk_aggregation_tool.aggregation' \
                     '.to_stata_xml.write_stata_docs'
        with patch(mock_write, MagicMock()):
            observed = aggregation_stata.wrapper(
                xlsforms_path=xlsforms_path, xforms_path=xforms_path,
                output_path=output_path)
        expected = "Collecting data for"
        self.assertIn(expected, observed)
