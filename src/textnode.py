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
    
    def text_node_to_html_node(self):
        from htmlnode import LeafNode

        if self.text_type == TextType.PLAIN:
            return LeafNode(tag=None, value=self.text)
        elif self.text_type == TextType.BOLD:
            return LeafNode(tag="b", value=self.text)
        elif self.text_type == TextType.ITALIC:
            return LeafNode(tag="i", value=self.text)
        elif self.text_type == TextType.CODE:
            return LeafNode(tag="code", value=self.text)
        elif self.text_type == TextType.LINK:
            if self.url is None:
                raise ValueError("Link TextNode must have a URL")
            return LeafNode(tag="a", value=self.text, props={"href": self.url})
        elif self.text_type == TextType.IMAGE:
            if self.url is None:
                raise ValueError("Image TextNode must have a URL")
            return LeafNode(tag="img", value="", props={"src": self.url, "alt": self.text})
        else:
            raise ValueError(f"Unsupported TextType: {self.text_type}")