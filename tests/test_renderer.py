from pdfgen.renderer import render
from pdfgen.yaml import parse


def test_render():
    pdf = parse("yaml/spec.yaml")
    render("generated/dump.pdf", pdf)


if __name__ == '__main__':
    test_render()
