import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, List, Tuple

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4 as RL_A4
from reportlab.lib.pagesizes import A3 as RL_A3
from reportlab.lib.pagesizes import A2 as RL_A2
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph as RL_Paragraph, TableStyle, Spacer
from reportlab.platypus import Table as RL_Table
from reportlab.platypus import Image as RL_Image

from dacite import from_dict


@dataclass
class PDFObject(ABC):
    """Base class of every object on a pdf page"""
    key: ClassVar[str]

    class Alignment(Enum):
        """Enum class storing information abount horizontal alignment"""
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
    
    space_before: int = field(default=0)
    space_after: int = field(default=0)

    @abstractmethod
    def generate(self, flowable_list: List):
        """Appends the object as a flowable to the page's flowable list"""
        pass

    @classmethod
    def get_with_spacing(cls, yaml_like: dict):
        result = cls()
        sp_before = yaml_like.get('space_before')
        sp_after = yaml_like.get("space_after")

        if sp_before is not None:
            result.space_before = sp_before

        if sp_after is not None:
            result.space_after = sp_after

        return result


@dataclass
class Paragraph(Renderable):
    """A paragraph is a simple PDF element that stores text"""
    key = 'paragraph'

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
                               spaceBefore=self.space_before,
                               spaceAfter=self.space_after
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

    @dataclass
    class Row:
        text: str = field(default='')

    rows: List[List[str]] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, yaml_like: dict):
        result = cls.get_with_spacing(yaml_like)

        rows = yaml_like.get('rows')

        assert isinstance(rows, list)

        for row in rows:
            assert isinstance(row, dict)
            cols = row.get('row')
            assert isinstance(cols, list)
            r = list()
            for col in cols:
                assert isinstance(col, dict)
                r.append(col.get('text'))

            result.rows.append(r)

        return result

    def generate(self, flowable_list: List):
        spacer = Spacer(width=10*inch, height=self.space_before)
        flowable_list.append(spacer)

        t = RL_Table(self.rows)

        t.setStyle(TableStyle(
            [('BOX', (0, 0), (-1, -1), 0.25, colors.black)]
        ))

        flowable_list.append(t)


@dataclass
class Image(Renderable):
    """Class to store and display images"""
    key = 'image'

    resource: str = field(default="")
    alignment: str = field(default=PDFObject.Alignment.LEFT.value)
    width: int = field(default=1*inch)
    height: int = field(default=1*inch)
    
    def __post_init__(self):
        self.space_before = self.height // 3

    @classmethod
    def from_yaml(cls, yaml_like: dict):
        return from_dict(data_class=cls, data=yaml_like)

    def generate(self, flowable_list: List):
        spacer = Spacer(width=0, height=self.space_before)
        flowable_list.append(spacer)

        img = RL_Image(self.resource, self.width, self.height)
        img.hAlign = self.alignment.upper()

        flowable_list.append(img)


@dataclass
class PDF(PDFObject):
    """Container class to organize all PDF objects into one stucture"""
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
                assert isinstance(value, list) # content must be a list of dicts

                for dictionary in value:

                    # region Paragraph
                    element = dictionary.get(Paragraph.key)

                    if element is not None:
                        result.content.append(Paragraph.from_yaml(element))
                        continue

                    # endregion

                    # region Table

                    element = dictionary.get(Table.key)

                    if element is not None:
                        result.content.append(Table.from_yaml(element))
                        continue

                    # endregion

                    # region Image

                    element = dictionary.get(Image.key)

                    if element is not None:
                        result.content.append(Image.from_yaml(element))
                        continue

                    # endregion

                    logging.warning(f"Invalid yaml element: {dictionary}")

        return result
