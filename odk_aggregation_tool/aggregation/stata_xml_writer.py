from typing import List
from collections import OrderedDict, namedtuple
from datetime import datetime
from odk_aggregation_tool.aggregation import readers
import xmltodict
from operator import eq

ODictList = List[OrderedDict]


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


def compose_xml(variable_types: ODictList,
                variable_names: ODictList,
                variable_formats: ODictList,
                value_label_maps: ODictList,
                variable_labels: ODictList,
                value_labels: ODictList,
                observation_values: ODictList) -> OrderedDict:
    """Prepare a final Stata XML document."""
    return OrderedDict([
        ('dta', OrderedDict([
            ('header', OrderedDict([
                ('ds_format', '113'),
                ('byteorder', 'LOHI'),
                ('filetype', '1'),
                ('nvar', str(len(variable_names))),
                ('nobs', str(len(observation_values))),
                ('data_label', 'Data from Python'),
                ('time_stamp', datetime.now().strftime("%d %b %Y %H:%M"))
            ])),
            ('descriptors', OrderedDict([
                ('typelist', OrderedDict([
                    ('type', variable_types)
                ])),
                ('varlist', OrderedDict([
                    ('variable', variable_names)
                ])),
                ('srtlist', None),
                ('fmtlist', OrderedDict([
                    ('fmt', variable_formats)
                ])),
                ('lbllist', OrderedDict([
                    ('lblname', value_label_maps)
                ]))
            ])),
            ('variable_labels', [
                OrderedDict([
                    ('vlabel', variable_labels)
                ]),
            ]),
            ('expansion', None),
            ('data', [
                OrderedDict([
                    ('o', observation_values)
                ])
            ]),
            ('value_labels', OrderedDict([
                ('vallab', value_labels)
            ]))
        ]))
    ])


def to_stata_xml(xlsform_path, instances_path):
    """
    Build a Stata XML document from the XLSForms and instance XML data.

    :param xlsform_path: where the XLSForm files are kept.
    :param instances_path: where the instance XML files are kept.
    :return Stata XML document, for writing to a file or further processing
    """
    form_defs = collate_xlsforms_by_form_id(xlsform_path=xlsform_path)
    for form in form_defs:
        form["metadata"] = prepare_xlsform_metadata(form_def=form)

    read_instances = list(readers.read_xml_files(root_dir=instances_path))

    parsed = [xmltodict.parse(x) for x in read_instances]
    flattened = [readers.flatten_dict_leaf_nodes(x) for x in parsed]
    observations = list()
    for instance in flattened:
        var_values = list()
        for k, v in instance.items():
            if k in [x['@varname'] for x in var_list]:
                var_values.append(observation_value(var_name=k, var_value=v))
        observations.append(OrderedDict([('v', var_values)]))

    final_doc = compose_xml(
        type_list, var_list, fmt_list, lbl_list, variable_labels,
        value_labels, observations)

    xml_document = xmltodict.unparse(final_doc)
    return xml_document


def collate_xlsforms_by_form_id(xlsform_path):

    read_xlsforms = list(
        readers.read_xlsform_definitions(root_dir=xlsform_path))
    unique_form_ids = set(x["@settings"]["form_id"] for x in read_xlsforms)
    form_dict = dict()
    for form_id in unique_form_ids:
        form_defs = [x for x in read_xlsforms
                     if eq(x["@settings"]["form_id"], form_id)]
        sorted_form_defs = sorted(form_defs, key=lambda x: x['@settings']['version'])
        master_form_def = OrderedDict()
        for xlsform in sorted_form_defs:
            for k, v in xlsform.items():
                v['default_language'] = xlsform['@settings']['default_language']
                if v.get('type') not in ['begin group', 'end group', None]:
                    master_form_def[k] = v
        form_dict[form_id] = master_form_def

    return form_dict


def prepare_xlsform_metadata(form_def):

    metadata = dict(var_types=list(), var_names=list(), var_formats=list(),
                    var_choices=list(), var_labels=list(), value_labels=list())

    for k, v in form_def.items():
        var_type = v.get('type', '')
        label_column = maybe_default_language(
            metadata_name='label', variable_dict=v)
        if var_type.startswith('select'):
            choices_name = var_type.split(' ')[1]
            metadata["var_choices"].append(value_label_map(
                var_name=k, choices_name=choices_name))
            metadata["value_labels"].append(value_label_collection(
                val_lab_name=choices_name, choices=v.get('choices', []),
                label_column=label_column))
            var_type = 'integer'
        type_mapping = next(
            (x for x in type_mappings if x.xlsform_type == var_type), '')
        metadata["var_names"].append(variable_name(var_name=k))
        metadata["var_types"].append(variable_type(
            var_name=k, stata_type=type_mapping.stata_type))
        metadata["var_formats"].append(variable_format(
            var_name=k, stata_fmt=type_mapping.stata_fmt))
        v.get('default_language', '')
        metadata["var_labels"].append(variable_label(
            var_name=k, description=v.get('name_description', label_column)))
    return metadata


def maybe_default_language(metadata_name, variable_dict):
    default_lang = variable_dict.get('default_language', None)
    maybe_lang = ''
    if default_lang is not None:
        '::{0}'.format(default_lang)
    return '{0}{1}'.format(metadata_name, maybe_lang)
