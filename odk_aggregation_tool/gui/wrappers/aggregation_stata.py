from odk_aggregation_tool.gui import utils
from odk_aggregation_tool.gui.log_capturing_handler import CapturingHandler
import logging
from odk_aggregation_tool.aggregation import to_stata_xml
import os


def wrapper(xlsforms_path, xforms_path, output_path):
    """Run the Aggregation to Stata task and return any result messages."""
    try:
        valid_xlsform_path = utils.validate_path(
            "XLSForm definitions path", xlsforms_path)
        valid_xforms_path = utils.validate_path(
            "XForm data path", xforms_path)
        valid_output_path = utils.validate_path(
            "Output path", output_path)

        header = "Aggregation to Stata XML task was run. Output below."
        stata_log = logging.getLogger(
            "odk_aggregation_tool.aggregation.readers")
        stata_log.setLevel("DEBUG")
        stata_capture = CapturingHandler(logger=stata_log, name="stata_capture")
        reader_log = logging.getLogger(
            "odk_aggregation_tool.aggregation.to_stata_xml")
        reader_log.setLevel("DEBUG")
        reader_capture = CapturingHandler(
            logger=reader_log, name="reader_capture")

        stata_docs = to_stata_xml.to_stata_xml(
            xlsform_path=valid_xlsform_path, instances_path=valid_xforms_path)
        write_stata_docs(stata_docs=stata_docs, output_path=valid_output_path)
        content = reader_capture.watcher.output + stata_capture.watcher.output

    except Exception as e:
        header = "Aggregation to Stata XML task not run. Error(s) below."
        content = str(e)
    result = utils.format_output(header=header, content=content)
    return result


def write_stata_docs(stata_docs, output_path):
    """Assuming the form_id is a valid basename, write the Stata docs out."""
    for form_id, document in stata_docs.items():
        write_path = os.path.join(output_path, '{0}.xml'.format(form_id))
        with open(write_path, mode='w', encoding="UTF-8") as out_doc:
            out_doc.write(document)
