from typing import List, Union, Dict, Iterable
from collections import OrderedDict, namedtuple, Counter
from datetime import datetime
from odk_aggregation_tool.aggregation import readers
import xmltodict
from copy import copy
import logging
import os

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
ListODict = List[OrderedDict]
DictODict = Dict[str, OrderedDict]


type_map = namedtuple('TypeMap', ['xlsform_type', 'stata_type', 'stata_fmt'])
# TODO: consider inspecting data to get a more accurate type for str and int.
# This would benefit the .dta file size, as well as remove the need for
# current assumptions around select items being always coded with integers.
type_mappings = [
    type_map('start',        'str26',    '%26s'),
    type_map('end',          'str26',    '%26s'),
    type_map('deviceid',     'str17',    '%17s'),
    type_map('date',         'int',      '%tdnn/dd/CCYY'),
    type_map('text',         'str2045',  '%30s'),
    type_map('integer',      'int',      '%10.0g')
]


def variable_type(var_name: str, stata_type: str) -> OrderedDict:
    """Prepare a Stata XML variable type (type) element."""
    return OrderedDict([
        ('@varname', var_name),
        ('#text', stata_type)
    ])


def variable_name(var_name: str) -> OrderedDict:
    """Prepare a Stata XML variable name (variable) element."""
    return OrderedDict([
        ('@varname', var_name)
    ])


def variable_format(var_name: str, stata_fmt: str) -> OrderedDict:
    """Prepare a Stata XML variable format (fmt) element."""
    return OrderedDict([
        ('@varname', var_name),
        ('#text', stata_fmt)
    ])


def value_label_map(var_name: str, choices_name: str) -> OrderedDict:
    """Prepare a Stata XML value label map (lblname) element."""
    return OrderedDict([
        ('@varname', var_name),
        ('#text', choices_name)
    ])


def variable_label(var_name: str, description: str) -> OrderedDict:
    """Prepare a Stata XML variable label (vlabel) element."""
    return OrderedDict([
        ('@varname', var_name),
        ('#text', description)
    ])


def value_label(label_value: str, label_text: str) -> OrderedDict:
    """Prepare a Stata XML value label (label) element."""
    return OrderedDict([
        ('@value', str(int(label_value))),
        ('#text', label_text)
    ])


def value_label_collection(val_lab_name: str, choices: ListODict,
                           label_column: str) -> OrderedDict:
    """Prepare a Stata XML value label (vallab) collection of labels (label)."""
    choice_list = [value_label(x['name'], x[label_column]) for x in choices]
    return OrderedDict([
        ('@name', val_lab_name),
        ('label', choice_list)
    ])


def observation_value(var_name: str, var_value: str) -> OrderedDict:
    """"Prepare a Stata XML observation value (v) element."""
    return OrderedDict([
        ('@varname', var_name.replace('@', '')),
        ('#text', var_value)
    ])


def compose_xml(var_types: ListODict, var_names: ListODict,
                var_formats: ListODict, var_labels: ListODict,
                var_vallabel_map: ListODict, value_labels: ListODict,
                observations: ListODict, nvar: str, nobs: str) -> OrderedDict:
    """Prepare a final Stata XML document."""
    return OrderedDict([
        ('dta', OrderedDict([
            ('header', OrderedDict([
                ('ds_format', '113'),
                ('byteorder', 'LOHI'),
                ('filetype', '1'),
                ('nvar', nvar),
                ('nobs', nobs),
                ('data_label', 'ODK data from Python'),
                ('time_stamp', datetime.now().strftime("%d %b %Y %H:%M"))
            ])),
            ('descriptors', OrderedDict([
                ('typelist', OrderedDict([
                    ('type', var_types)
                ])),
                ('varlist', OrderedDict([
                    ('variable', var_names)
                ])),
                ('srtlist', None),
                ('fmtlist', OrderedDict([
                    ('fmt', var_formats)
                ])),
                ('lbllist', OrderedDict([
                    ('lblname', var_vallabel_map)
                ]))
            ])),
            ('variable_labels', [
                OrderedDict([
                    ('vlabel', var_labels)
                ]),
            ]),
            ('expansion', None),
            ('data', [
                OrderedDict([
                    ('o', observations)
                ])
            ]),
            ('value_labels', OrderedDict([
                ('vallab', value_labels)
            ]))
        ]))
    ])


def to_stata_xml(xlsform_path: str, instances_path: str) -> Dict[str, str]:
    """Return Stata XML documents for all discovered XLSForms and XML data."""
    form_defs = collate_xlsforms_by_form_id(xlsform_path=xlsform_path)
    raw_data = collate_xform_instances(instances_path=instances_path)
    instances = remove_duplicate_instances(instances=raw_data)

    stata_docs = dict()
    for form_id, form_def in form_defs.items():
        stata_metadata = prepare_xlsform_metadata(
            form_id=form_id, form_def=form_def)
        xform_instances = [x for x in instances if x["@id"] == form_id]
        variable_names = [x["@varname"] for x in stata_metadata["var_names"]]
        nvar = str(len(variable_names))
        logger.info("Collecting data for {0} "
                    "variables for form_id: {1}".format(nvar, form_id))
        observations = prepare_observations(
            xform_instances=xform_instances, variable_names=variable_names)
        nobs = str(len(observations))
        logger.info("Collected data for {0} "
                    "observations for form_id: {1}".format(nobs, form_id))
        stata_doc = compose_xml(
            observations=observations, nvar=nvar, nobs=nobs, **stata_metadata)
        stata_docs[form_id] = xmltodict.unparse(stata_doc)

    return stata_docs


def collate_xlsforms_by_form_id(xlsform_path: str) -> DictODict:
    """Return discovered form def metadata, from last of sorted versions."""
    logger.info("Looking for XLSForms to read.")
    read_xlsforms = list(
        readers.read_xlsform_definitions(root_dir=xlsform_path))
    unique_form_ids = sorted(
        set(x["@settings"]["form_id"] for x in read_xlsforms))
    if len(unique_form_ids) == 0:
        logger.warning("No XLSForms were read from the specified path. "
                       "Please check it and try again.")
    else:
        logger.info("The following XLSForm form_ids were read: "
                    "{0}.".format(unique_form_ids))

    form_dict = OrderedDict()
    for form_id in unique_form_ids:
        form_defs = [x for x in read_xlsforms
                     if x["@settings"]["form_id"] == form_id]
        sorted_form_defs = sorted(
            form_defs, key=lambda x: x["@settings"]["version"])
        master_form_def = OrderedDict()

        for xlsform in sorted_form_defs:
            if master_form_def.get("@settings") is None:
                master_form_def["@settings"] = xlsform["@settings"]
            for k, v in xlsform.items():
                if v.get("type") not in ["begin group", "end group", None]:
                    master_form_def[k] = v
        form_dict[form_id] = master_form_def
    return form_dict


def prepare_xlsform_metadata(form_id: str, form_def: OrderedDict) -> DictODict:
    """Return Stata metadata for the default language for each form item."""
    metadata = dict(
        var_types=list(), var_names=list(), var_formats=list(),
        var_labels=list(), var_vallabel_map=list(), value_labels=list())
    form_def_items = copy(form_def)
    form_def_items.pop("@settings")
    form_default_lang = form_def["@settings"].get("default_language")
    logger.info("Using default language: {0}, for metadata "
                "with form_id: {1}".format(form_default_lang, form_id))
    form_def_items = add_source_file_field(
        form_id=form_id, form_def_items=form_def_items)

    choices_added = list()
    for k, v in form_def_items.items():
        var_type = v.get('type', '')
        if v.get("readonly") == "yes" and k.startswith("nl_") \
                and var_type == "text":
            logger.info("Skipped adding metadata for an variable assumed to "
                        "be a labelling variable (type=text, readonly, and "
                        "name starts with 'nl_'). "
                        "Form_id: {0}, variable name: {1}".format(form_id, k))
            continue
        label_column = maybe_language_column(
            metadata_name='label', language_name=form_default_lang)
        if var_type.startswith('select'):
            choice_list = v.get('choices', [])
            if choice_data_type_is_integer(choice_list=choice_list):
                choices_name = var_type.split(' ')[1]
                metadata["var_vallabel_map"].append(value_label_map(
                    var_name=k, choices_name=choices_name))
                if choices_name not in choices_added:
                    metadata["value_labels"].append(value_label_collection(
                        val_lab_name=choices_name, choices=choice_list,
                        label_column=label_column))
                    choices_added.append(choices_name)
                var_type = 'integer'
            else:
                var_type = 'text'
        type_mapping = next(
            (x for x in type_mappings if x.xlsform_type == var_type), '')
        metadata["var_names"].append(variable_name(var_name=k))
        metadata["var_types"].append(variable_type(
            var_name=k, stata_type=type_mapping.stata_type))
        metadata["var_formats"].append(variable_format(
            var_name=k, stata_fmt=type_mapping.stata_fmt))
        label_column_value = v.get(label_column)
        metadata["var_labels"].append(variable_label(
            var_name=k, description=v.get(
                'name_description', label_column_value)))
    return metadata


def add_source_file_field(
        form_id: str, form_def_items: OrderedDict) -> OrderedDict:
    if "_source_file" not in form_def_items:
        form_def_items["_source_file"] = OrderedDict([
            ("name", "_source_file"), ("type", "text"),
            ("name_description", "Path to file that the data was read from.")])
        logger.info("Added '_source_file' field to metadata "
                    "for form_id: {0}.".format(form_id))
    else:
        logger.info("Field for '_source_file' not added, one exists "
                    "already for form_id: {0}".format(form_id))
    return form_def_items


def maybe_language_column(metadata_name: str,
                          language_name: Union[str, None]) -> str:
    """Return a language-specific column name if the language isn't None."""
    maybe_lang = ''
    if language_name is not None:
        maybe_lang = '::{0}'.format(language_name)
    return '{0}{1}'.format(metadata_name, maybe_lang)


def collate_xform_instances(instances_path: str) -> ListODict:
    """Return collated (parsed and flattened) XForm data."""
    read_instances = list(readers.read_xml_files(root_dir=instances_path))
    parsed = []
    for xml_data, file_path in read_instances:
        parsed_data = xmltodict.parse(xml_input=xml_data)
        parsed_data["_source_file"] = os.path.normpath(file_path)
        parsed_data["_source_xml"] = xml_data
        parsed.append(parsed_data)
    flattened = [readers.flatten_dict_leaf_nodes(x) for x in parsed]
    return flattened


def prepare_observations(xform_instances: ListODict,
                         variable_names: List) -> ListODict:
    """Return a list of observation values filtered for the named variables."""
    observations = list()
    for instance in xform_instances:
        var_values = list()
        for k, v in instance.items():
            if k in variable_names:
                var_values.append(observation_value(var_name=k, var_value=v))
        observations.append(OrderedDict([('v', var_values)]))
    return observations


def write_stata_docs(stata_docs: Dict[str, str], output_path: str) -> None:
    """Assuming the form_id is a valid basename, write the Stata docs out."""
    for form_id, document in stata_docs.items():
        write_path = os.path.join(output_path, '{0}.xml'.format(form_id))
        with open(write_path, mode='w', encoding="UTF-8") as out_doc:
            out_doc.write(document)
        logger.info("Wrote form data for form_id: {0}, to a file at: "
                    " {1}.".format(form_id, write_path))


def choice_data_type_is_integer(choice_list: List[Dict]) -> bool:
    """Inspect choice list values to select an appropriate data type."""
    for choice in choice_list:
        try:
            choice["name"] = int(choice["name"])
        except ValueError:
            logger.warning("Found non-integer value in choice list: "
                           "{0}, value: {1}. All values in this choice "
                           "list will be output as text.".format(
                            choice["list_name"], choice["name"]))
            return False
    return True


def remove_duplicate_instances(instances: ListODict) -> ListODict:
    """Remove duplicate instances, logging a warning if so."""
    counts = Counter(x.get("_source_xml") for x in instances)
    dupes = {k: v for k, v in counts.items() if v != 1}
    for k, v in dupes.items():
        dupe_values = [x for x in instances if x.get("_source_xml") == k]
        dupe_paths = list()
        for i, dupe in enumerate(dupe_values):
            dupe_paths.append(dupe.get("_source_file"))
            if i > 0:
                instances.remove(dupe)
        log_msg = "Found duplicate XML files. Only data from the first " \
                  "file listed below will be included in the output. \n" \
                  "Count: {0},\n" \
                  "Source files:\n{1}".format(v, '\n'.join(dupe_paths))
        logger.warning(log_msg)
    return instances
