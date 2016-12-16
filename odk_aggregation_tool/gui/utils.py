import os

WRAP_CHARS = "\" \r\n\t"


def not_empty(variable_name, path):
    if len(path) == 0:
        valid = False
        msg = "{0} is empty. Please either:\n" \
              "- Enter the path, or\n" \
              "- Select the path using the 'Browse...' button."
        msg = msg.format(variable_name)
    else:
        valid = True
        msg = None
    return valid, msg


def folder_exists(variable_name, path):
    if os.path.isdir(path):
        valid = True
        msg = None
    else:
        valid = False
        msg = "{0} does not correspond to an existing directory.\n" \
              "Please check the path and try again."
        msg = msg.format(variable_name)
    return valid, msg


def clean_path(path):
    if path is None:
        path = ""
    else:
        if len(path) > 0:
            path = os.path.normpath(path.strip("\" \r\n\t"))
    return path


def validations(variable_name, cleaned_path):
    yield not_empty(variable_name=variable_name, path=cleaned_path)
    yield folder_exists(variable_name=variable_name, path=cleaned_path)


def validate_path(variable_name, path):
    """
    Check if the input path is valid, and raise ValueError(s) if not.

    Parameters.
    :param variable_name: str. Name of variable to state in error messages.
    :param path: str. Path to check.
    :return: str. valid path to do further work with.
    """
    cleaned_path = clean_path(path=path)
    kw = {"variable_name": variable_name, "path": cleaned_path}
    checks = [(not_empty, kw), (folder_exists, kw)]
    for func, kwargs in checks:
        valid, message = func(**kwargs)
        if not valid:
            raise ValueError("Input Error.\n\n{0}".format(message))
    return cleaned_path


def format_output(header, content):
    """
    Formatted the result header and content, separated by double newlines.
    """
    if content is not None:
        if type(content) == str:
            content = [content]
        return "\n\n".join([header, *content])
    else:
        return header
