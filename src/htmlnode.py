from typing import Optional

class HtmlNode:
    def __init__(self, tag: Optional[str] = None, value: Optional[str] = None, children: Optional[list] = None, props: Optional[dict] = None):
        self.tag = tag
        self.value = value
        self.children = children if children is not None else []
        self.props = props if props is not None else {}

    def __repr__(self):
        return f"HtmlNode(tag={self.tag!r}, value={self.value!r}, children={self.children!r}, props={self.props!r})"
    
    def to_html(self):
        raise NotImplementedError("to_html method not implemented yet")

    def props_to_html(self):
        if self.props is None:
            return ""
        return_value = ""
        for key, value in self.props.items():
            return_value += f' {key}="{value}"'
        return return_value


class LeafNode(HtmlNode):
    
    def __init__(self, tag: Optional[str], value: Optional[str], props: Optional[dict] = None):
        super().__init__(tag=tag, value=value, children=None, props=props)
    
    def to_html(self):
        if self.value is None:
            raise ValueError("LeafNode must have a value to convert to HTML")
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
    

class ParentNode(HtmlNode):
    
    def __init__(self, tag: str, children: list, props: Optional[dict] = None):
        super().__init__(tag=tag, value=None, children=children, props=props)
    
    def to_html(self):
        if self.tag is None:
            raise ValueError("ParentNode must have a tag to convert to HTML")
        if self.children is None:
            raise ValueError("ParentNode must have children to convert to HTML")
        children_html = ''.join(child.to_html() for child in self.children)
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"