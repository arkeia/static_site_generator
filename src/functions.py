
from enum import Enum

from charset_normalizer import from_path
from textnode import TextNode, TextType
from htmlnode import LeafNode, ParentNode
import re
import os
import shutil


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADER = "header"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    CODE = "code"
    QUOTE = "quote"

    
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

def block_to_block_type(text):
    """
    Determines the BlockType of a given markdown block.

    Args:
        text (str): The input markdown block.

    Returns:
        BlockType: The determined BlockType of the block.
    """
    lines = text.split("\n")

    if all(re.match(r"^\s*-\s+", line) for line in lines):
        return BlockType.UNORDERED_LIST
    elif all(re.match(r"^\s*\d+\.\s+", line) for line in lines):
        return BlockType.ORDERED_LIST
    elif all(re.match(r"^>", line) for line in lines):
        return BlockType.QUOTE
    elif re.match(r"^\s*```", lines[0]) and re.match(r"^\s*```", lines[-1]):
        return BlockType.CODE
    elif re.match(r"^\s*#+\s+", lines[0]):  
        return BlockType.HEADER
    else:
        return BlockType.PARAGRAPH


def markdown_to_html_node(markdown):    
    """
    Converts a markdown string into an HtmlNode representation.

    Args:
        markdown (str): The input markdown string.

    Returns:
        HtmlNode: The HtmlNode representation of the markdown.
    """
    
    blocks = markdown_to_blocks(markdown)
    html_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.PARAGRAPH:
            text_nodes = text_to_textnodes(block)
            html_children = [tn.text_node_to_html_node() for tn in text_nodes]
            html_nodes.append(ParentNode(tag="p", children=html_children))
        elif block_type == BlockType.HEADER:
            m = re.match(r"^\s*(#+)", block)
            level = len(m.group(1)) if m else 1
            level = min(max(level, 1), 6)
            text_content = re.sub(r"^\s*#+\s+", "", block)
            text_nodes = text_to_textnodes(text_content)
            html_children = [tn.text_node_to_html_node() for tn in text_nodes]
            html_nodes.append(ParentNode(tag=f"h{level}", children=html_children))
        elif block_type == BlockType.UNORDERED_LIST:
            list_items = []
            for line in block.split("\n"):
                item_content = re.sub(r"^\s*-\s+", "", line)
                text_nodes = text_to_textnodes(item_content)
                html_children = [tn.text_node_to_html_node() for tn in text_nodes]
                list_items.append(ParentNode(tag="li", children=html_children))
            html_nodes.append(ParentNode(tag="ul", children=list_items))
        elif block_type == BlockType.ORDERED_LIST:
            list_items = []
            for line in block.split("\n"):
                item_content = re.sub(r"^\s*\d+\.\s+", "", line)
                text_nodes = text_to_textnodes(item_content)
                html_children = [tn.text_node_to_html_node() for tn in text_nodes]
                list_items.append(ParentNode(tag="li", children=html_children))
            html_nodes.append(ParentNode(tag="ol", children=list_items))
        elif block_type == BlockType.CODE:
            code_content = re.sub(r"^\s*```\s*|\s*```\s*$", "", block)
            html_nodes.append(LeafNode(tag="pre", value=code_content))
        elif block_type == BlockType.QUOTE:
            quote_lines = []
            for line in block.split("\n"):
                line_content = re.sub(r">\s*", "", line)
                text_nodes = text_to_textnodes(line_content)
                quote_lines.append(LeafNode(tag=None,value=line_content))
            html_nodes.append(ParentNode(tag="blockquote", children=quote_lines))
    if len(html_nodes) == 1:
        return html_nodes[0]
    return ParentNode(tag="div", children=html_nodes)


def recursive_directory_copy(src_path, dest_path):
    """
    Recursively copies the contents of one directory to another.

    Args:
        src_path (str): The source directory path.
        dest_path (str): The destination directory path.
    """
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    for item in os.listdir(src_path):
        s = os.path.join(src_path, item)
        d = os.path.join(dest_path, item)
        if os.path.isdir(s):
            recursive_directory_copy(s, d)
        else:
            shutil.copy(s, d)
        
def extract_title(markdown):
    """
    Extracts the title from a markdown string. The title is defined as the text of the first level 1 header.

    Args:
        markdown (str): The input markdown string.

    Returns:
        str: The extracted title, or an empty string if no level 1 header is found.
    """
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError("No level 1 header found in the markdown.")

def generate_page(from_path, template_path, dest_path):
    """
    Generates an HTML page by combining markdown content with an HTML template.

    Args:
        from_path (str): The path to the markdown file.
        template_path (str): The path to the HTML template file.
        dest_path (str): The path to save the generated HTML file.
    """

    with open(from_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    title = extract_title(markdown_content)
    html_node = markdown_to_html_node(markdown_content)
    body_html = html_node.to_html()
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    final_html = template_content.replace("{{ Title }}", title, count=1).replace("{{ Content }}", body_html, count=1)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

def generate_pages_recursively(content_dir, template_path, public_dir):
    """
    Generates HTML pages for all markdown files in a content directory, preserving the directory structure.

    Args:
        content_dir (str): The path to the content directory containing markdown files.
        template_path (str): The path to the HTML template file.
        public_dir (str): The path to the public directory where generated HTML files will be saved.
    """
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith(".md"):
                relative_path = os.path.relpath(root, content_dir)
                dest_directory = os.path.join(public_dir, relative_path)
                if not os.path.exists(dest_directory):
                    os.makedirs(dest_directory)
                from_path = os.path.join(root, file)
                dest_path = os.path.join(dest_directory, file[:-3] + ".html")
                generate_page(from_path, template_path, dest_path)
            