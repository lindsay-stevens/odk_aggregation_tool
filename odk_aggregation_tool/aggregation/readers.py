import os
import xlrd
from collections import OrderedDict


def read_xml_files(root_dir):
    """
    Read all XML files located in the root_dir and it's sub-folders.

    :param root_dir: Path to search in.
    :type root_dir: str
    :return: iterator of xml files.
    """
    for entry in os.scandir(path=root_dir):
        if entry.is_dir():
            yield from read_xml_files(root_dir=entry.path)
        elif entry.name.endswith(".xml"):
            with open(entry.path, mode='r') as f:
                xml_file = f.read()
            yield xml_file


def read_xlsform_definitions(root_dir):
    """
    Read survey definitions from all XLSX files located in the root_dir.

    :param root_dir: Path to search in.
    :type root_dir: str.
    :return: list of dicts containing XLSForm survey definitions with choices.
    """
    for entry in os.scandir(path=root_dir):
        if entry.is_dir():
            yield from read_xlsform_definitions(root_dir=entry.path)
        elif entry.name.endswith(".xlsx"):
            workbook = xlrd.open_workbook(filename=entry.path)
            survey = xlrd_sheet_to_list_of_dict(
                    workbook.sheet_by_name(sheet_name='survey'))
            choices = xlrd_sheet_to_list_of_dict(
                    workbook.sheet_by_name(sheet_name='choices'))
            settings = xlrd_sheet_to_list_of_dict(
                workbook.sheet_by_name(sheet_name='settings'))
            form_def = OrderedDict()
            form_def['@settings'] = settings[0]
            for item in survey:
                if item['type'].startswith('select'):
                    select_type, choice_name = item['type'].split(' ')
                    choice_list = [x for x in choices
                                   if x['list_name'] == choice_name]
                    item['choices'] = choice_list
                form_def[item['name']] = item
            yield form_def


def xlrd_sheet_to_list_of_dict(sheet):
    """
    Convert an xlrd sheet into a list of dicts.

    :param sheet: The xlrd sheet to process.
    :type sheet: xlrd.sheet.Sheet
    :return: list of dicts.
    """
    keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
    dict_list = []
    for row_index in range(1, sheet.nrows):
        d = {keys[col_index]: sheet.cell(row_index, col_index).value
             for col_index in range(sheet.ncols)}
        dict_list.append(d)
    return dict_list


def flatten_dict_leaf_nodes(dict_in, dict_out=None):
    """
    Flatten leaf nodes of a nested and/or list of dicts into a single dict.

    :param dict_in: Dictionary containing nested and/or list of dicts.
    :type dict_in: dict
    :param dict_out: Dictionary to add key/values to, a new dict is made
        and returned if this parameter is not provided.
    :type dict_out: dict
    :return: Single-level dictionary containing leaf node values.
    :rtype: dict
    """
    if dict_out is None:
        dict_out = OrderedDict()
    for k, v in dict_in.items():
        if isinstance(v, dict):
            flatten_dict_leaf_nodes(v, dict_out)
        elif isinstance(v, list):
            for i in v:
                flatten_dict_leaf_nodes(i, dict_out)
        else:
            dict_out[k] = v
    return dict_out
