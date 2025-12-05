
from textnode import TextNode, TextType
import re


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
                    new_nodes.extend(current_sublist)
                    current_sublist = []
    if current_sublist:
        new_nodes.extend(current_sublist)
    return new_nodes

def extract_markdown_images(text):
    """
    Extracts all markdown image URLs from the given text.

    Args:
        text (str): The input text containing markdown image syntax.
    """
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)




def extract_markdown_links(text):
    """
    Extracts all markdown link URLs from the given text.

    Args:
        text (str): The input text containing markdown link syntax.
    """
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)

def split_nodes_image(old_nodes):
    """
    Splits a list of TextNode objects into sublists whenever a markdown image is encountered.
    The image TextNode is included in the resulting sublists.

    Args:
        old_nodes (list of TextNode): The original list of TextNode objects to be split.    
    """
    new_nodes = []
    current_sublist = []

    for node in old_nodes:
        current_sublist = []
        if node.text_type is not TextType.TEXT:
            new_nodes.extend([node])
            continue
        parts = extract_markdown_images(node.text)
        if parts == []:
            new_nodes.extend([node])
            continue
        for part in parts:
            sections = node.text.split(f"![{part[0]}]({part[1]})", 1)
            if sections[0]:
                current_sublist.append(TextNode(sections[0], TextType.TEXT))
            current_sublist.append(TextNode(part[0], TextType.IMAGE, url=part[1]))
            if sections[1] != "":
                current_sublist.append(TextNode(sections[1], TextType.TEXT))
        
        new_nodes.extend(current_sublist)
    return new_nodes

def split_nodes_link(old_nodes):
    """
    Splits a list of TextNode objects into sublists whenever a markdown link is encountered.
    The link TextNode is included in the resulting sublists.

    Args:
        old_nodes (list of TextNode): The original list of TextNode objects to be split.    
    """
    new_nodes = []
    current_sublist = []

    new_nodes = []
    current_sublist = []

    for node in old_nodes:
        current_sublist = []
        if node.text_type is not TextType.TEXT:
            new_nodes.extend([node])
            continue
        parts = extract_markdown_links(node.text)
        if parts == []:
            new_nodes.extend([node])
            continue
        for part in parts:
            sections = node.text.split(f"[{part[0]}]({part[1]})", 1)
            if sections[0]:
                current_sublist.append(TextNode(sections[0], TextType.TEXT))
            current_sublist.append(TextNode(part[0], TextType.LINK, url=part[1]))
            if sections[1] != "":
                current_sublist.append(TextNode(sections[1], TextType.TEXT))
        
        new_nodes.extend(current_sublist)
    return new_nodes


def text_to_textnodes(text):
    """
    Converts a plain text string into a list of TextNode objects.

    Args:
        text (str): The input plain text string.

    Returns:
        list of TextNode: A list containing TextNodes with the input text.
    """
    node_list = [TextNode(text, TextType.TEXT)]
    node_list = split_nodes_delimiter(node_list, "`", TextType.CODE)
    node_list = split_nodes_delimiter(node_list, "**", TextType.BOLD)
    node_list = split_nodes_delimiter(node_list, "_", TextType.ITALIC)
    node_list = split_nodes_link(node_list)
    node_list = split_nodes_image(node_list)
    return node_list

def markdown_to_blocks(markdown):
    """
    Converts a markdown string into a list of block-level HtmlNode objects.

    Args:
        markdown (str): The input markdown string.
    """
    blocks : list[str] = markdown.split("\n\n")
    result_blocks = []
    for block in blocks:
        result_blocks.append(block.strip("\n "))
    return result_blocks