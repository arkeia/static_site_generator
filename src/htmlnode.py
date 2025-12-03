class HtmlNode:
    def __init__(self, tag: str = None, value: str = None, children: list = None, props: dict = None):
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