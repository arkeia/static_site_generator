from enum import Enum
from typing import Optional

class TextType(Enum):
    PLAIN = "plain"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text: str, text_type: TextType, url: Optional[str] = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, value):
        if not isinstance(value, TextNode):
            return False
        return (self.text, self.text_type, self.url) == (value.text, value.text_type, value.url)

    def __repr__(self):
        return f"TextNode({self.text!r}, {self.text_type}, {self.url!r})"