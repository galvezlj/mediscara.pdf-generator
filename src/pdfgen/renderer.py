from reportlab.platypus import SimpleDocTemplate

from .pdf.objects import PDF, Renderable


def render(file_name:str, pdf: PDF):
    doc = SimpleDocTemplate(file_name,
                            pagesize=pdf.sheet.size_tuple,
                            leftMargin=pdf.sheet.margin.left,
                            rightMargin=pdf.sheet.margin.right,
                            topMargin=pdf.sheet.margin.top,
                            bottomMargin=pdf.sheet.margin.bottom
                            )

    content = []

    for element in pdf.content:
        assert isinstance(element, Renderable)

        element.generate(content)

    doc.build(content)
