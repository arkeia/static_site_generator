
from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Splits a list of TextNode objects into sublists whenever a TextNode with the specified delimiter is encountered.
    The delimiter TextNode is not included in the resulting sublists.

    Args:
        old_nodes (list of TextNode): The original list of TextNode objects to be split.
        delimiter (str): The text value of the TextNode that acts as the delimiter.
        text_type (TextType): The TextType of the delimiter TextNode.

    Returns:
        list of list of TextNode: A list containing sublists of TextNode objects split by the delimiter.
    """

    new_nodes = []
    current_sublist = []

    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            current_sublist.append(node)
            continue
        parts = node.text.split(delimiter)
        if parts == [node.text]:
            current_sublist.append(node)
            continue
        if len(parts) % 2 == 0:
            raise Exception("No matching closing delimiter found.")
        for i, part in enumerate(parts):
            if part and i%2 == 0:
                current_sublist.append(TextNode(part, TextType.TEXT))
            elif part and i%2 == 1:
                current_sublist.append(TextNode(part, text_type))
            if i < len(parts) - 1:
                if current_sublist:
                    new_nodes.append(current_sublist)
                    current_sublist = []
    if current_sublist:
        new_nodes.append(current_sublist)
    return new_nodes