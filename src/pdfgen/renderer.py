import logging

from reportlab.platypus import SimpleDocTemplate

from .pdf.objects import PDF


def render(file_name: str, pdf: PDF) -> bool:
    """Renders the PDF document and saves it to the given location

    The rendering is done using reportlab's platypus module
    """
    doc = SimpleDocTemplate(
        file_name,
        pagesize=pdf.sheet.size_tuple,
        leftMargin=pdf.sheet.margin.left,
        rightMargin=pdf.sheet.margin.right,
        topMargin=pdf.sheet.margin.top,
        bottomMargin=pdf.sheet.margin.bottom,
    )

    content = pdf.render()

    try:
        doc.build(content)
        return True

    except PermissionError:
        logging.error(
            "Could not open the output file, maybe it is open in another window?"
        )

    except Exception as error:  # pylint: disable=broad-except
        logging.fatal("One of the resources could not be loaded: %s", error)

    return False
