from odk_aggregation_tool.gui import utils
from odk_aggregation_tool.gui.log_capturing_handler import CapturingHandler
import logging
from odk_aggregation_tool.aggregation import to_stata_xml
import os
import traceback


def wrapper(xlsforms_path, xforms_path, output_path):
    """Run the Aggregation to Stata task and return any result messages."""
    agg_logger = logging.getLogger("odk_aggregation_tool.aggregation")
    agg_capture = CapturingHandler(logger=agg_logger, name="agg_capture")
    agg_logger.setLevel("DEBUG")
    agg_logger.parent = None  # Disables logger propagation to "root" stdout.
    try:
        valid_xlsform_path = utils.validate_path(
            "XLSForm definitions path", xlsforms_path)
        valid_xforms_path = utils.validate_path(
            "XForm data path", xforms_path)
        valid_output_path = utils.validate_path(
            "Output path", output_path)
        header = "Aggregation to Stata XML task was run. Output below."
        stata_docs = to_stata_xml.to_stata_xml(
            xlsform_path=valid_xlsform_path, instances_path=valid_xforms_path)
        to_stata_xml.write_stata_docs(
            stata_docs=stata_docs, output_path=valid_output_path)
        content = agg_capture.watcher.output
        result = utils.format_output(header=header, content=content)
        agg_logger.removeHandler(agg_capture)
        if len(result) > 2500:
            log_file = os.path.join(valid_output_path, 'log.txt')
            message = "A large amount of log data (over 2000 characters) " \
                      "was generated. A copy of the logs will be written " \
                      "to a file at: {0}".format(log_file)
            with open(log_file, mode="w", encoding="UTF-8") as log:
                log.write(result)
            result = "{0}\n\n{1}".format(message, result)
    except Exception as e:
        header = "Aggregation to Stata XML task not completed. Error(s) below."
        content = "{0}\n\n{1}".format(str(e), ''.join(traceback.format_exc()))
        result = utils.format_output(header=header, content=content)
    finally:
        # If not definitely removed, no messages will be shown on re-run,
        # because CapturingHandler won't attach if there's a duplicate name.
        agg_logger.removeHandler(agg_capture)
    return result
