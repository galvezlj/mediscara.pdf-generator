import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, List, Tuple

from dacite import from_dict
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A2 as RL_A2
from reportlab.lib.pagesizes import A3 as RL_A3
from reportlab.lib.pagesizes import A4 as RL_A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Image as RL_Image
from reportlab.platypus import PageBreak as RL_PageBreak
from reportlab.platypus import Paragraph as RL_Paragraph, Spacer
from reportlab.platypus import Table as RL_Table


@dataclass
class PDFObject(ABC):
    """Base class of every object on a pdf page"""
    key: ClassVar[str]

    class Alignment(Enum):
        """Enum class storing information about horizontal alignment"""
        LEFT = 'left'
        RIGHT = 'right'
        CENTER = 'center'

    @classmethod
    @abstractmethod
    def from_yaml(cls, yaml_like: dict):
        """Attempts to load the object from a yaml-like structured dictionary object"""
        pass


@dataclass
class Margin(PDFObject):
    """This class stores the global margins on a page"""
    key = 'margin'

    left: int = field(default=16)
    right: int = field(default=16)
    top: int = field(default=16)
    bottom: int = field(default=16)

    @classmethod
    def from_yaml(cls, yaml_like: dict):
        pass


@dataclass
class Sheet(PDFObject):
    """This class describes the sheet properties of a pdf document"""
    key = 'sheet'

    class Size(Enum):
        """Enum class for masking the actual reportlab values to a readable value"""
        A4 = RL_A4
        A3 = RL_A3
        A2 = RL_A2

    margin: Margin = field(default=Margin())
    size: str = field(default='A4')
    font: str = field(default='Times-Roman')

    @classmethod
    def from_yaml(cls, yaml_like: dict):
        return from_dict(data_class=cls, data=yaml_like)

    @property
    def size_tuple(self) -> Tuple[float, float]:
        """Returns the raw size value as a tuple of floats"""
        for element in Sheet.Size:
            if element.name == self.size:
                return element.value


@dataclass
class Renderable(PDFObject, ABC):
    """Base class for all renderable PDF objects"""

    parent: PDFObject = field(default=None)
    
    space_before: int = field(default=4)
    space_after: int = field(default=4)

    def render(self, flowable_list: List):
        if isinstance(self.parent, PDF):
            flowable_list.append(Spacer(width=0, height=self.space_before))

            self.generate(flowable_list)

            flowable_list.append(Spacer(width=0, height=self.space_after))

        else:
            self.generate(flowable_list)

    @abstractmethod
    def generate(self, flowable_list: List):
        """Appends the object as a flowable to the page's flowable list"""
        pass


@dataclass
class Paragraph(Renderable):
    """A paragraph is a simple PDF element that stores text"""
    key = 'paragraph'

    font: ClassVar[str] = field(default="Times-Roman")

    alignment: str = field(default=PDFObject.Alignment.LEFT.value)
    size: int = field(default=12)

    text: str = field(default="")

    def __post_init__(self):
        self.space_before = self.size // 3  # set default margins

    @classmethod
    def from_yaml(cls, yaml_like: dict):
        return from_dict(data_class=cls, data=yaml_like)

    def generate(self, flowable_list: List):
        # create the paragraph style
        style = ParagraphStyle(name=self.alignment,
                               alignment=self.rl_alignment,
                               fontSize=self.size,
                               fontName=Paragraph.font
                               )
        flowable_list.append(RL_Paragraph(self.text, style))

    @property
    def rl_alignment(self):
        """Returns the reportlab equivalent of the alignment value"""
        if self.alignment == Paragraph.Alignment.LEFT.value:
            return TA_LEFT

        if self.alignment == Paragraph.Alignment.CENTER.value:
            return TA_CENTER

        if self.alignment == Paragraph.Alignment.RIGHT.value:
            return TA_RIGHT


@dataclass
class Table(Renderable):
    """"""
    key = 'table'
    font: ClassVar[str] = field(default="Times-Roman")

    @dataclass
    class Row:
        resource: str = field(default='')

    @dataclass
    class Cell(PDFObject):
        key = 'cell'

        text: str = field(default="")
        background_color: str = field(default="0xFFFFFF")

        @classmethod
        def from_yaml(cls, yaml_like: dict):
            return from_dict(data_class=cls, data=yaml_like)

    border: bool = field(default=False)
    header: bool = field(default=False)  # if true, the first row is the header
    rows: List = field(default_factory=list)
    grid: bool = field(default=False)

    @classmethod
    def from_yaml(cls, yaml_like: dict):
        result = from_dict(data_class=cls, data=yaml_like)  # get the non-nested fields
        result.rows = []  # override rows

        rows = yaml_like.get('rows')

        assert isinstance(rows, list)

        for row in rows:  # get the dictionary of a row
            assert isinstance(row, dict)
            cols = row.get('row')  # get the list of dictionaries from the row

            assert isinstance(cols, list)
            r = list()

            for col in cols:
                assert isinstance(col, dict)
                resource = col.get(Table.Cell.key)

                if resource is not None:
                    cell = Table.Cell.from_yaml(resource)
                    cell.parent = result
                    r.append(cell)
                    continue

                resource = col.get(Image.key)

                if resource is not None:
                    assert isinstance(resource, dict)
                    img = Image.from_yaml(resource)
                    img.parent = result
                    img.generate(r)
                    continue

            result.rows.append(r)

        return result

    def generate(self, flowable_list: List):
        table_data = list()
        background_colors = list()

        for i, row in enumerate(self.rows):
            background_colors.append(list())
            table_data.append(list())
            for cell in row:
                if isinstance(cell, Table.Cell):
                    background_colors[i].append(cell.background_color)
                    table_data[i].append(cell.text)

                else:
                    table_data[i].append(cell)

        t = RL_Table(table_data)

        style_args = [("FONTNAME", (0, 0), (-1, -1), self.font)]

        # set background colors
        for i, row in enumerate(background_colors):
            for j, color in enumerate(row):
                if color != "0xFFFFFF":
                    style_args.append(("BACKGROUND", (j, i), (j, i), HexColor(color)))

        if self.header:
            style_args.append(("LINEBELOW", (0, 0), (-1, 0), 1, colors.black))  # add a line below the first row
            style_args.append(("BACKGROUND", (0, 0), (-1, -0), colors.lightgrey))  # add grey background

        if self.grid:
            style_args.append(("GRID", (0, 0), (-1, -1), 0.25, colors.grey))

        if self.border:
            style_args.append(('BOX', (0, 0), (-1, -1), 0.5, colors.black))

        t.setStyle(style_args)

        flowable_list.append(t)


@dataclass
class Image(Renderable):
    """Class to store and display images"""
    key = 'image'

    resource: str = field(default="")
    alignment: str = field(default=PDFObject.Alignment.LEFT.value)
    width: int = field(default=1*inch)
    height: int = field(default=1*inch)

    @classmethod
    def from_yaml(cls, yaml_like: dict):
        return from_dict(data_class=cls, data=yaml_like)

    def generate(self, flowable_list: List):
        img = RL_Image(self.resource, self.width, self.height)
        img.hAlign = self.alignment.upper()

        flowable_list.append(img)


@dataclass
class PageBreak(Renderable):
    key = 'page_break'

    @classmethod
    def from_yaml(cls, yaml_like: dict):
        return cls()

    def generate(self, flowable_list: List):
        flowable_list.append(RL_PageBreak())


@dataclass
class PDF(PDFObject):
    """Container class to organize all PDF objects into one structure"""
    key = 'pdf'

    sheet: Sheet = field(default=Sheet())

    content: List = field(default_factory=list)

    @classmethod
    def from_yaml(cls, yaml_like: dict):
        root = yaml_like.get(cls.key)

        if root is None:
            logging.error(f"The root element should be '{cls.key}' in the spec file")
            return None

        result = cls()

        assert isinstance(root, dict)
        for key, value in root.items():
            # retrieve the keys
            # there should be only
            #   - sheet
            #   - content
            #
            if key == cls.sheet.key:
                result.sheet = Sheet.from_yaml(value)

            elif key == 'content':
                assert isinstance(value, list)  # content must be a list of dicts

                for dictionary in value:

                    # region Paragraph
                    element = dictionary.get(Paragraph.key)

                    if element is not None:
                        p = Paragraph.from_yaml(element)
                        p.parent = result
                        result.content.append(p)
                        continue

                    # endregion

                    # region Table

                    element = dictionary.get(Table.key)

                    if element is not None:
                        t = Table.from_yaml(element)
                        t.parent = result
                        result.content.append(t)
                        continue

                    # endregion

                    # region Image

                    element = dictionary.get(Image.key)

                    if element is not None:
                        i = Image.from_yaml(element)
                        i.parent = result
                        result.content.append(i)
                        continue

                    # endregion

                    # region Page Break

                    try:
                        dictionary[PageBreak.key]

                    except KeyError:
                        pass

                    else:
                        result.content.append(PageBreak())

                    # endregion

                    logging.warning(f"Invalid yaml element: {dictionary}")

        return result

    def render(self) -> List:
        Paragraph.font = self.sheet.font
        Table.font = self.sheet.font

        content = []

        for element in self.content:
            assert isinstance(element, Renderable)

            element.render(content)

        return content
