import io
import logging
from os import getcwd
import sys
import re

from yaml import safe_load

from .pdf.objects import PDF


def init(yaml_path: str):
    """Loads the yaml file"""
    try:
        with open(yaml_path, "r", encoding="utf-8") as file:
            init.yaml_raw = file.read()

    except FileNotFoundError:
        logging.fatal("Yam`l file not found at: %s.", yaml_path)
        logging.fatal("Current working directory is: %s", getcwd())
        sys.exit(1)


def load_variables(variables: dict) -> dict:
    """Loads the variable dictionary back into the raw file"""

    if not hasattr(init, "yaml_raw"):
        logging.warning(
            "%s: yaml file not loaded, please use the %s method first",
            load_variables.__name__,
            init.__name__,
        )
        return None

    string = init.yaml_raw

    for name, value in variables.items():
        name_str = f"<{name}>"

        previous_string = string

        string = re.sub(name_str, value, string)

        if string == previous_string:
            logging.warning("Variable '%s' not found in yaml file", name)

    matches = has_variables(string)

    if matches:
        # the list is not None, not all variables were filled
        for match in matches:
            logging.warning("Variable '%s' was not overridden", match)

    return safe_load(string)  # convert the string back to dict


def has_variables(string: str = ""):
    """Checks if the yaml file has variables with the <variable> syntax"""

    if not string:
        if not hasattr(init, "yaml_raw"):
            logging.warning(
                "%s: yaml file not loaded, please use the %s method first",
                load_variables.__name__,
                init.__name__,
            )
            return False

        string = init.yaml_raw

    re_pattern = r"<\w+>"

    return re.findall(re_pattern, string)


def check_yaml_syntax():
    """Checks if the syntax of the variables (if any) are correct in the yaml file"""

    if not hasattr(init, "yaml_raw"):
        logging.warning(
            "%s: yaml file not loaded, please use the %s method first",
            load_variables.__name__,
            init.__name__,
        )
        return

    re_pattern = r"<\w+^>"

    errors = re.findall(pattern=re_pattern, string=init.yaml_raw)

    if errors:
        for error in errors:
            logging.warning("Syntax error in variable: %s", str(error))

    else:
        logging.info("Yaml variable syntax is correct")


def parse(file: str or io.TextIOWrapper):
    """Parses the file and generates a PDF object from it
    :param file: the input file. Can be a string of the file path or an already opened file stream
    :returns: a PDF object
    :raises TypeError: if the input is neither a file nor a file path string
    """
    if isinstance(file, str):
        with open(file, "r", encoding="utf-8") as f_open:
            yaml_content = safe_load(f_open)

    elif isinstance(file, io.TextIOWrapper):
        yaml_content = safe_load(file)

    else:
        raise TypeError(f"Invalid file descriptor type: {type(file)}")

    return PDF.from_yaml(yaml_content)
