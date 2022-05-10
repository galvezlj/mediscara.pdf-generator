from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar

from reportlab.lib.enums import TA_LEFT


@dataclass
class PDFObject:
    key: ClassVar[str] = ''

    def __post_init__(self):
        self.key = PDFObject.__name__.lower()

    class Alignment(Enum):
        LEFT = 'left'
        RIGHT = 'right'
        CENTER = 'center'


@dataclass
class Paragraph(PDFObject):
    alignment: str = field(default=PDFObject.Alignment.LEFT.value)
    size: int = field(default=12)
    space_before: int = field(init=False)
    space_after: int = field(default=0)

    def __post_init__(self):
        self.space_before = self.size // 3
