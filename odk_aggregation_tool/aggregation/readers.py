import os
import xlrd
from xlrd import XLRDError
from xlrd.book import Book
from collections import OrderedDict
from typing import Iterable
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel("INFO")


def read_xml_files(root_dir: str) -> Iterable[str]:
    """Read instance XML files found recursively in root_dir."""
    for entry in os.scandir(path=root_dir):
        if entry.is_dir():
            yield from read_xml_files(root_dir=entry.path)
        elif entry.name.endswith(".xml"):
            with open(entry.path, mode='r', encoding="UTF-8") as f:
                xml_file = f.read()
            yield xml_file


def read_xlsform_definitions(root_dir: str) -> Iterable[str]:
    """Read XLSX files found recursively in root_dir"""
    error_text = "Encountered an error while trying to read the XLSX file " \
                 "at the following path, and did not read from it: {0}.\n" \
                 "Error message was: {1}\n"
    for entry in os.scandir(path=root_dir):
        if entry.is_dir():
            yield from read_xlsform_definitions(root_dir=entry.path)
        elif entry.name.endswith(".xlsx"):
            try:
                workbook = xlrd.open_workbook(filename=entry.path)
                form_def = read_xlsform_data(workbook=workbook)
            except XLRDError as xle:
                logger.info(error_text.format(entry.path, str(xle)))
                continue
            except ValueError as ve:
                logger.info(error_text.format(entry.path, str(ve)))
                continue
            else:
                yield form_def


def read_xlsform_data(workbook: Book) -> OrderedDict:
    """Return XLSForm definition data read from an XLRD Workbook."""
    sheets = {x.name for x in workbook.sheets()}
    required = {"survey", "choices", "settings"}
    if not required.issubset(sheets):
        raise ValueError(
            "The required sheets for an XLSForm definition ({0}) were not "
            "found in the workbook sheets ({1}).".format(required, sheets))
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
    return form_def


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


def flatten_dict_leaf_nodes(dict_in: OrderedDict,
                            dict_out: OrderedDict = None) -> OrderedDict:
    """Flatten nested leaves of and/or a list of OrderedDict into one level."""
    if dict_out is None:
        dict_out = OrderedDict()
    for k, v in dict_in.items():
        if isinstance(v, OrderedDict):
            flatten_dict_leaf_nodes(v, dict_out)
        elif isinstance(v, list):
            for i in v:
                flatten_dict_leaf_nodes(i, dict_out)
        else:
            dict_out[k] = v
    return dict_out
