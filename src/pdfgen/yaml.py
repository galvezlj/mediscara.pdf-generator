import _io

import yaml

from .pdf.objects import PDF


def parse(file: str or _io.TextIOWrapper):
    """Parses the file and generates a PDF object from it
    :param file: the input file. Can be a string of the file path or an already opened file stream
    :returns: a PDF object
    :raises TypeError: if the input is neither a file nor a file path string
    """
    if isinstance(file, str):
        with open(file, 'r') as f_open:
            yaml_content = yaml.safe_load(f_open)

    elif isinstance(file, _io.TextIOWrapper):
        yaml_content = yaml.safe_load(file)

    else:
        raise TypeError(f"Invalid file descriptor type: {type(file)}")

    return PDF.from_yaml(yaml_content)


