from pdfgen.yaml import parse


def test_parse():
    p = parse("yaml/spec.yaml")
    print(p)


if __name__ == '__main__':
    test_parse()
