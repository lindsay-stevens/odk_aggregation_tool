import unittest
from tests.aggregation import FixturePaths
from odk_aggregation_tool.aggregation import to_stata_xml
from odk_aggregation_tool.gui.log_capturing_handler import CapturingHandler
from operator import eq
import logging


class TestStataXMLWriter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fixtures = FixturePaths()
        cls.instances_root = cls.fixtures.files['instances']
        cls.xlsform_root = cls.fixtures.files['xlsforms']

    def test_collate_xlsforms_by_form_id_produces_2_form_defs(self):
        """Should discover the two form defs and return separate metadata."""
        forms = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=self.xlsform_root)
        self.assertEqual({"Q1302_BEHAVE", "R1302_BEHAVE"}, set(forms))

    def test_collate_xlsforms_by_form_id_most_recent_def_version_int(self):
        """Should return most recent definitions when version id is an int."""
        forms = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=self.fixtures.files["xlsform_version_ids_int"])
        expected = "Do you like writing tests?"
        observed = [v["label"] for k, v in
                    forms["xlsform"].items() if eq(k, "var_c2")][0]
        self.assertEqual(expected, observed)

    def test_collate_xlsforms_by_form_id_most_recent_def_version_str(self):
        """Should return most recent definitions when version id is a str."""
        forms = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=self.fixtures.files["xlsform_version_ids_str"])
        expected = "Do you like writing tests?"
        observed = [v["label"] for k, v in
                    forms["xlsform"].items() if eq(k, "var_c2")][0]
        self.assertEqual(expected, observed)

    def test_prepare_xlsform_metadata_simple_populates_metadata(self):
        """Should populate all required metadata fields."""
        xlsform = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=self.fixtures.files["xlsform_simplest"])
        observed = to_stata_xml.prepare_xlsform_metadata(
            form_def=xlsform["xlsform"], form_id="xlsform")
        self.assertEqual(
            {"var_types", "var_names", "var_formats", "var_labels",
             "var_vallabel_map", "value_labels"}, set(observed))
        for k, v in observed.items():
            self.assertTrue(len(v) > 0)

    def test_prepare_xlsform_metadata_returns_unique_vallab_defs(self):
        """Should emit unique value label definitions only once."""
        xlsform = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=self.fixtures.files["xlsform_unique_vallab"])
        observed = to_stata_xml.prepare_xlsform_metadata(
            form_def=xlsform["xlsform"], form_id="xlsform")
        all_names = [x["@name"] for x in observed["value_labels"]]
        unique_names = list(set(all_names))
        self.assertListEqual(all_names, unique_names)

    def test_prepare_xlsform_metadata_uses_default_language_var_labels(self):
        """Should emit metadata for the form's specified default language."""
        xlsform = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=self.fixtures.files["xlsform_multi_language"])
        observed = to_stata_xml.prepare_xlsform_metadata(
            form_def=xlsform["xlsform"], form_id="xlsform")
        var_labels = {x["#text"] for x in observed["var_labels"]}
        expected = "Do you like writing tests?"
        self.assertIn(expected, var_labels)

    def test_prepare_xlsform_metadata_uses_default_language_value_labels(self):
        """Should emit metadata for the form's specified default language."""
        xlsform = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=self.fixtures.files["xlsform_multi_language"])
        observed = to_stata_xml.prepare_xlsform_metadata(
            form_def=xlsform["xlsform"], form_id="xlsform")
        vallabel_yes = [x["label"] for x in observed["value_labels"]][0][0]
        expected = {"@value": '1', "#text": "Yes"}
        self.assertDictEqual(expected, vallabel_yes)

    def test_choice_data_type_is_integer_integer(self):
        """Should be true if all values are, or coerce-able to, an int."""
        choices = [{"name": 1.0}, {"name": 2}, {"name": 3.}, {"name": 5000}]
        for x in choices:
            x["list_name"] = "test"
        observed = to_stata_xml.choice_data_type_is_integer(choice_list=choices)
        self.assertTrue(observed)

    def test_choice_data_type_is_integer_non_integer(self):
        """Should be false if any values not, or un-coerce-able to, an int."""
        choices = [{"name": 1.0}, {"name": "Yes"}]
        for x in choices:
            x["list_name"] = "test"
        observed = to_stata_xml.choice_data_type_is_integer(choice_list=choices)
        self.assertFalse(observed)

    def test_choice_data_type_is_integer_empty_list(self):
        """Should be true if the list is empty; the values could be int."""
        choices = []
        observed = to_stata_xml.choice_data_type_is_integer(choice_list=choices)
        self.assertTrue(observed)

    def test_prepare_xlsform_metadata_uses_text_for_nonint_choice_list(self):
        """Should include non-int choice list variables as text."""
        xlsform = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=self.fixtures.files["xlsform_with_nonint_choices"])
        logger_name = "odk_aggregation_tool.aggregation"
        with self.assertLogs(logger=logger_name, level="WARNING"):
            observed = to_stata_xml.prepare_xlsform_metadata(
                form_def=xlsform["xlsform"], form_id="xlsform")
        self.assertTrue(len(observed["value_labels"]) == 1)
        variable_names = [x["@varname"] for x in observed["var_names"]]
        self.assertTrue("var_c2" in variable_names)

    def test_instance_data_contains_duplicates_no_dupes(self):
        """Should be true if observations contain no duplicate instance IDs."""
        xforms_path = self.fixtures.files["instances"]
        instances = to_stata_xml.collate_xform_instances(
            instances_path=xforms_path)
        logger_name = "odk_aggregation_tool.aggregation"
        agg_logs = logging.getLogger(logger_name)
        agg_logs.parent = None
        agg_capture = CapturingHandler(logger=agg_logs, name="test_dupes")
        observed = to_stata_xml.remove_duplicate_instances(
            instances=instances)
        self.assertEqual(0, len(agg_capture.watcher.output))
        self.assertEqual(15, len(instances))
        self.assertEqual(15, len(observed))

    def test_instance_data_contains_duplicates_with_dupes(self):
        """Should be false if observations contain no duplicate instance IDs."""
        xforms_path = self.fixtures.files["instances_duplicates"]
        instances = to_stata_xml.collate_xform_instances(
            instances_path=xforms_path)
        self.assertEqual(6, len(instances))
        logger_name = "odk_aggregation_tool.aggregation"
        with self.assertLogs(logger=logger_name, level="WARNING") as logs:
            observed = to_stata_xml.remove_duplicate_instances(
                instances=instances)
        self.assertIn("Found duplicate", logs.output[0])
        self.assertEqual(4, len(observed))

    def test_tidy_form_def_includes_unknown_variables(self):
        """Should include unknown variables with data that aren't in XLSForm."""
        xlsform_path = self.fixtures.files["xlsform_unknown_variable"]
        instances_path = xlsform_path
        form_def = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=xlsform_path)["xlsform"]
        raw_data = to_stata_xml.collate_xform_instances(
            instances_path=instances_path)
        xform_data, unknown_vars = to_stata_xml.prepare_xform_data(
            xform_instances=raw_data, form_def=form_def)
        form_def = to_stata_xml.tidy_form_def(
            form_id="xlsform", form_def=form_def, unknown_vars=unknown_vars)
        self.assertIn("var_e", form_def)
        self.assertIn("version", form_def)
        self.assertNotIn("extra", form_def)
        self.assertNotIn("settings", form_def)

    def test_tidy_form_def_cleans_invalid_names_in_unknown_variables(self):
        """Should remove invalid Stata identifier characters from varnames."""
        xlsform_path = self.fixtures.files["xlsform_unknown_variable"]
        instances_path = xlsform_path
        form_def = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=xlsform_path)["xlsform"]
        raw_data = to_stata_xml.collate_xform_instances(
            instances_path=instances_path)
        xform_data, unknown_vars = to_stata_xml.prepare_xform_data(
            xform_instances=raw_data, form_def=form_def)
        form_def = to_stata_xml.tidy_form_def(
            form_id="xlsform", form_def=form_def, unknown_vars=unknown_vars)
        self.assertIn("id", form_def)

    def test_prepare_xform_data_handles_date_conversion(self):
        """Should convert ISO date to Stata elapsed date."""
        xlsform_path = self.fixtures.files["xlsform_date_variable"]
        instances_path = xlsform_path
        form_def = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=xlsform_path)["xlsform"]
        raw_data = to_stata_xml.collate_xform_instances(
            instances_path=instances_path)
        xform_data, unknown_vars = to_stata_xml.prepare_xform_data(
            xform_instances=raw_data, form_def=form_def)
        var_ds = [x.get("var_d") for x in xform_data]
        self.assertEqual("-5392", var_ds[0])
        self.assertEqual("18494", var_ds[1])

    def test_prepare_observations_includes_id_and_version_values(self):
        """Should include form_id and form_version in observation data."""
        xlsform_path = self.fixtures.files["xlsform_unknown_variable"]
        instances_path = xlsform_path
        form_def = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=xlsform_path)["xlsform"]
        raw_data = to_stata_xml.collate_xform_instances(
            instances_path=instances_path)
        xform_data, unknown_vars = to_stata_xml.prepare_xform_data(
            xform_instances=raw_data, form_def=form_def)
        form_def = to_stata_xml.tidy_form_def(
            form_id="xlsform", form_def=form_def, unknown_vars=unknown_vars)
        observations = to_stata_xml.prepare_observations(
            xform_data=xform_data, form_def=form_def)
        output_keys = [x["@varname"] for x in observations[0]["v"]]
        self.assertIn("id", output_keys)
        self.assertIn("version", output_keys)

