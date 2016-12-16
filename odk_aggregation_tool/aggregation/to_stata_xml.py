from typing import List, Union, Dict
from collections import OrderedDict, namedtuple
from datetime import datetime
from odk_aggregation_tool.aggregation import readers
import xmltodict
from operator import eq
from copy import copy
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
ODictList = List[OrderedDict]
ODictDict = Dict[str, OrderedDict]


type_map = namedtuple('TypeMap', ['xlsform_type', 'stata_type', 'stata_fmt'])
# TODO: consider inspecting data to get a more accurate type for str and int.
# This would benefit the .dta file size, as well as remove the need for
# current assumptions around select items being always coded with integers.
type_mappings = [
    type_map('start',     'str26',    '%26s'),
    type_map('end',       'str26',    '%26s'),
    type_map('deviceid',  'str17',    '%17s'),
    type_map('date',      'int',      '%tdnn/dd/CCYY'),
    type_map('text',      'str2045',  '%30s'),
    type_map('integer',   'int',      '%10.0g'),
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


def value_label_collection(val_lab_name: str, choices: ODictList,
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


def compose_xml(var_types: ODictList, var_names: ODictList,
                var_formats: ODictList, var_labels: ODictList,
                var_vallabel_map: ODictList, value_labels: ODictList,
                observations: ODictList, nvar: str, nobs: str) -> OrderedDict:
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
    read_instances = list(readers.read_xml_files(root_dir=instances_path))
    parsed = [xmltodict.parse(x) for x in read_instances]
    flattened = [readers.flatten_dict_leaf_nodes(x) for x in parsed]

    stata_docs = dict()
    for form_id, form_def in form_defs.items():
        stata_metadata = prepare_xlsform_metadata(form_def=form_def)
        xform_instances = [x for x in flattened if eq(x["@id"], form_id)]
        variable_names = [x["@varname"] for x in stata_metadata["var_names"]]
        nvar = str(len(variable_names))
        logger.info("Collecting data for {0} "
                    "variables for form: {1}".format(nvar, form_id))
        observations = prepare_xform_data(
            xform_instances=xform_instances, variable_names=variable_names)
        nobs = str(len(observations))
        logger.info("Collected data for {0} "
                    "observations for form: {1}".format(nobs, form_id))
        stata_doc = compose_xml(
            observations=observations, nvar=nvar, nobs=nobs, **stata_metadata)
        stata_docs[form_id] = xmltodict.unparse(stata_doc)

    return stata_docs


def collate_xlsforms_by_form_id(xlsform_path: str) -> ODictDict:
    """Return discovered form def metadata, from last of sorted versions."""
    logger.info("Reading XLSForms.")
    read_xlsforms = list(
        readers.read_xlsform_definitions(root_dir=xlsform_path))
    unique_form_ids = set(x["@settings"]["form_id"] for x in read_xlsforms)
    logger.info("Found the following XLSForms: {0}".format(unique_form_ids))

    form_dict = dict()
    for form_id in unique_form_ids:
        form_defs = [x for x in read_xlsforms
                     if eq(x["@settings"]["form_id"], form_id)]
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

        logging.info("Default language for form {0}: {1}".format(
            form_id, master_form_def["@settings"].get("default_language")))
    return form_dict


def prepare_xlsform_metadata(form_def: OrderedDict) -> ODictDict:
    """Return Stata metadata for the default language for each form item."""
    metadata = dict(
        var_types=list(), var_names=list(), var_formats=list(),
        var_labels=list(), var_vallabel_map=list(), value_labels=list())
    form_def_items = copy(form_def)
    form_def_items.pop("@settings")
    form_default_lang = form_def["@settings"].get("default_language")

    choices_added = list()
    for k, v in form_def_items.items():
        var_type = v.get('type', '')
        label_column = maybe_language_column(
            metadata_name='label', language_name=form_default_lang)
        if var_type.startswith('select'):
            choices_name = var_type.split(' ')[1]
            metadata["var_vallabel_map"].append(value_label_map(
                var_name=k, choices_name=choices_name))
            if choices_name not in choices_added:
                metadata["value_labels"].append(value_label_collection(
                    val_lab_name=choices_name, choices=v.get('choices', []),
                    label_column=label_column))
                choices_added.append(choices_name)
            var_type = 'integer'
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


def maybe_language_column(metadata_name: str,
                          language_name: Union[str, None]) -> str:
    """Return a language-specific column name if the language isn't None."""
    maybe_lang = ''
    if language_name is not None:
        maybe_lang = '::{0}'.format(language_name)
    return '{0}{1}'.format(metadata_name, maybe_lang)


def prepare_xform_data(xform_instances: ODictList,
                       variable_names: List) -> ODictList:
    """Return a list of observation values filtered for the named variables."""
    observations = list()
    for instance in xform_instances:
        var_values = list()
        for k, v in instance.items():
            if k in variable_names:
                var_values.append(observation_value(var_name=k, var_value=v))
        observations.append(OrderedDict([('v', var_values)]))
    return observations
