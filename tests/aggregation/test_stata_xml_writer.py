import unittest
from tests.aggregation import FixturePaths
from odk_aggregation_tool.aggregation import to_stata_xml
from operator import eq


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
            form_def=xlsform["xlsform"])
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
            form_def=xlsform["xlsform"])
        all_names = [x["@name"] for x in observed["value_labels"]]
        unique_names = list(set(all_names))
        self.assertListEqual(all_names, unique_names)

    def test_prepare_xlsform_metadata_uses_default_language_var_labels(self):
        """Should emit metadata for the form's specified default language."""
        xlsform = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=self.fixtures.files["xlsform_multi_language"])
        observed = to_stata_xml.prepare_xlsform_metadata(
            form_def=xlsform["xlsform"])
        var_labels = {x["#text"] for x in observed["var_labels"]}
        expected = "Do you like writing tests?"
        self.assertIn(expected, var_labels)

    def test_prepare_xlsform_metadata_uses_default_language_value_labels(self):
        """Should emit metadata for the form's specified default language."""
        xlsform = to_stata_xml.collate_xlsforms_by_form_id(
            xlsform_path=self.fixtures.files["xlsform_multi_language"])
        observed = to_stata_xml.prepare_xlsform_metadata(
            form_def=xlsform["xlsform"])
        vallabel_yes = [x["label"] for x in observed["value_labels"]][0][0]
        expected = {"@value": '1', "#text": "Yes"}
        self.assertDictEqual(expected, vallabel_yes)
