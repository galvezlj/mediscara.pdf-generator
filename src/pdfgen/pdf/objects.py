import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, List

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4 as RL_A4
from reportlab.lib.pagesizes import A3 as RL_A3
from reportlab.lib.pagesizes import A2 as RL_A2
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph as RL_Paragraph, TableStyle
from reportlab.platypus import Table as RL_Table

from dacite import from_dict


@dataclass
class PDFObject(ABC):
    key: ClassVar[str]

    class Alignment(Enum):
        LEFT = 'left'
        RIGHT = 'right'
        CENTER = 'center'

    @classmethod
    @abstractmethod
    def from_yaml(cls, yaml_file: dict):
        pass


@dataclass
class Margin(PDFObject):
    key = 'margin'

    left: int = field(default=16)
    right: int = field(default=16)
    top: int = field(default=16)
    bottom: int = field(default=16)

    @classmethod
    def from_yaml(cls, yaml_file: dict):
        pass


@dataclass
class Sheet(PDFObject):
    class Size(Enum):
        A4 = RL_A4
        A3 = RL_A3
        A2 = RL_A2

    key = 'sheet'

    margin: Margin = field(default=Margin())
    size: str = field(default='A4')

    @classmethod
    def from_yaml(cls, yaml_file: dict):
        return from_dict(data_class=cls, data=yaml_file)

    @property
    def size_tuple(self):
        for element in Sheet.Size:
            if element.name == self.size:
                return element.value


@dataclass
class Renderable(PDFObject, ABC):

    @abstractmethod
    def generate(self, flowable_list: List):
        pass


@dataclass
class Paragraph(Renderable):
    key = 'paragraph'

    alignment: str = field(default=PDFObject.Alignment.LEFT.value)
    size: int = field(default=12)
    space_before: int = field(init=False)
    space_after: int = field(default=0)

    text: str = field(default="")

    def __post_init__(self):
        self.space_before = self.size // 3

    @classmethod
    def from_yaml(cls, yaml_file: dict):
        return from_dict(data_class=cls, data=yaml_file)

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
    key = 'table'

    @dataclass
    class Row:
        text: str = field(default='')

    rows: List[List[str]] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, yaml_file: dict):
        rows = yaml_file.get('rows')

        assert isinstance(rows, list)

        result = cls()

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
        t = RL_Table(self.rows)

        t.setStyle(TableStyle(
            [('BOX', (0, 0), (-1, -1), 0.25, colors.black)]
        ))

        flowable_list.append(t)


@dataclass
class PDF(PDFObject):
    key = 'pdf'

    sheet: Sheet = field(default=Sheet())

    content: List = field(default_factory=list)

    @classmethod
    def from_yaml(cls, yaml_file: dict):
        root = yaml_file.get(cls.key)

        if root is None:
            logging.error(f"The root element should be '{cls.key}' in the spec file")
            return None

        result = cls()

        assert isinstance(root, dict)
        for key, value in root.items():
            if key == cls.sheet.key:
                result.sheet = Sheet.from_yaml(value)

            elif key == 'content':
                assert isinstance(value, list)

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

                    logging.warning(f"Invalid yaml element: {dictionary}")

        return result
