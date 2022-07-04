"""Main module of the package"""

import argparse
import logging
import sys
from argparse import FileType
from os import path

import io

from . import __version__
from .yaml import parse
from .renderer import render

INPUT_FILE = "input_file"
OUTPUT_FILE = "output_file"


def parse_args(args):
    """Parses the command line arguments"""
    arg_parser = argparse.ArgumentParser(description="This script generates a PDF document based on a .yaml file")

    # version
    arg_parser.add_argument('--version', action='version', version=f"pdfgen: {__version__}")

    # input file
    arg_parser.add_argument(INPUT_FILE,
                            type=FileType('r'),
                            help="The path of the specification.yaml file"
                            )

    # output file
    arg_parser.add_argument('-o', '--output',
                            dest=OUTPUT_FILE,
                            type=str,
                            help="The path of the output file"
                            )

    return arg_parser.parse_args(args)

def generate(input_file: str or io.TextIOWrapper, output_file: str):
    """Generate the PDF document"""
    logging.info("Generating file '%s'", output_file)
    pdf = parse(input_file)
    if render(output_file, pdf):
        logging.info("Document successfully rendered")


def main(args):
    """Main entry point of the package"""
    opts = vars(parse_args(args))

    input_file = opts.get(INPUT_FILE)
    output_file = opts.get(OUTPUT_FILE)

    if output_file is None:
        assert isinstance(input_file, io.TextIOWrapper)

        directory, _ = path.split(input_file.name)

        output_file = f"{directory}/generated.pdf"

    generate(input_file, output_file)


if __name__ == '__main__':
    main(sys.argv)
