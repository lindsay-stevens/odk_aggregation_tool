import odk_aggregation_tool


class Preferences:
    """Preferences for the GUI."""
    str_version = str(odk_aggregation_tool.__version__)
    app_title = ' '.join(["ODK Tools GUI", str_version])
    label_width = 25
    textbox_width = 85
    output_height = 25
    dir_browse = {'mustexist': True}
    generic_pre_msg = "{0} task initiated, please wait...\n\n"
    font = ('Arial', 8)
