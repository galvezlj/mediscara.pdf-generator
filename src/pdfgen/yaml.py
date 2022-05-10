import _io

import yaml


def parse(file: str or _io.TextIOWrapper):
    yaml_content = None
    if isinstance(file, str):
        with open(file, 'r') as f_open:
            yaml_content = yaml.safe_load(f_open)

    elif isinstance(file, _io.TextIOWrapper):
        yaml_content = yaml.safe_load(file)

    else:
        raise TypeError(f"Invalid file descriptor type: {type(file)}")
