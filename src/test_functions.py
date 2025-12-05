import unittest
import tempfile
import os

from textnode import TextNode, TextType
from functions import extract_markdown_images, extract_markdown_links, markdown_to_blocks, split_nodes_delimiter

class TestFunctions(unittest.TestCase):
    def test_split_nodes_delimiter(self):
        nodes = [
            TextNode("Hello, this is a test. Split here. This is after the split. Split here again. And here.", TextType.TEXT),
            TextNode("No delimiters", TextType.TEXT),
        ]
        delimiter = "Split here"
        result = split_nodes_delimiter(nodes, delimiter, TextType.TEXT)
        expected = [
            TextNode("Hello, this is a test. ", TextType.TEXT),
            TextNode(". This is after the split.", TextType.TEXT),
            TextNode(" again. And here.", TextType.TEXT),
            TextNode("No delimiters", TextType.TEXT),
        ]

        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected_new_nodes = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected_new_nodes)



    def test_split_nodes_delimiter_raises(self):
        node = TextNode("This is a test with unmatched delimiter ` here.", TextType.TEXT)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

        matches = extract_markdown_images(
            "No images here!"
        )
        self.assertListEqual([], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://example.com) inside."
        )
        self.assertListEqual([("link", "https://example.com")], matches)

        matches = extract_markdown_links(
            "No links here!"
        )
        self.assertListEqual([], matches)

    def test_text_to_textnode(self):
        from functions import text_to_textnodes
        text = "This is a sample text with a [link](https://example.com) and an ![image](https://i.imgur.com/zjjcJKZ.png)."
        expected_nodes = [
            TextNode("This is a sample text with a ", TextType.TEXT),
            TextNode("link", TextType.LINK, url="https://example.com"),
            TextNode(" and an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, url="https://i.imgur.com/zjjcJKZ.png"),
            TextNode(".", TextType.TEXT),
        ]
        result_nodes = text_to_textnodes(text)
        self.assertEqual(result_nodes, expected_nodes)

        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"

        expected_nodes = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, url="https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, url="https://boot.dev"),
        ]
        result_nodes = text_to_textnodes(text)
        self.assertEqual(result_nodes, expected_nodes)

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph


This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type(self):
        from functions import block_to_block_type, BlockType

        self.assertEqual(
            block_to_block_type("# This is a header"),
            BlockType.HEADER,
        )
        self.assertEqual(
            block_to_block_type("This is a paragraph."),
            BlockType.PARAGRAPH,
        )
        self.assertEqual(
            block_to_block_type("- List item 1\n- List item 2"),
            BlockType.UNORDERED_LIST,
        )
        self.assertEqual(
            block_to_block_type("1. First item\n2. Second item"),
            BlockType.ORDERED_LIST,
        )
        self.assertEqual(
            block_to_block_type("```\nCode block\n```"),
            BlockType.CODE,
        )
        self.assertEqual(
            block_to_block_type("> This is a quote."),
            BlockType.QUOTE,
        )

    def test_markdown_to_html_node_headers(self):
        from functions import markdown_to_html_node

        # simple header
        node = markdown_to_html_node("# Hello World")
        self.assertEqual(node.to_html(), "<h1>Hello World</h1>")

        # header with extra hashes should clamp to h6
        node = markdown_to_html_node("####### Too many hashes")
        self.assertEqual(node.to_html(), "<h6>Too many hashes</h6>")

        # header with surrounding whitespace
        node = markdown_to_html_node("  ##   Indented header  ")
        self.assertEqual(node.to_html(), "<h2>Indented header</h2>")

    def test_markdown_to_html_node_lists_and_paragraphs(self):
        from functions import markdown_to_html_node

        # unordered list
        node = markdown_to_html_node("- Item one\n- Item two")
        self.assertEqual(node.to_html(), "<ul><li>Item one</li><li>Item two</li></ul>")

        # ordered list
        node = markdown_to_html_node("1. First\n2. Second")
        self.assertEqual(node.to_html(), "<ol><li>First</li><li>Second</li></ol>")

        # paragraph
        node = markdown_to_html_node("This is a paragraph.")
        self.assertEqual(node.to_html(), "<p>This is a paragraph.</p>")

    def test_markdown_to_html_node_code_and_quote(self):
        from functions import markdown_to_html_node

        # code block
        node = markdown_to_html_node("```\nprint(\"hi\")\n```")
        self.assertEqual(node.to_html(), "<pre>print(\"hi\")</pre>")

        # quote
        node = markdown_to_html_node("> A quoted line")
        self.assertEqual(node.to_html(), "<blockquote><p>A quoted line</p></blockquote>")

    def test_textnode_to_html_node_and_htmlnode_to_html(self):
        from textnode import TextNode, TextType
        from htmlnode import LeafNode

        # simple text node
        tn = TextNode("hello", TextType.TEXT)
        hn = tn.text_node_to_html_node()
        self.assertEqual(hn.to_html(), "hello")

        # bold
        tn = TextNode("bold", TextType.BOLD)
        hn = tn.text_node_to_html_node()
        self.assertEqual(hn.to_html(), "<b>bold</b>")

        # italic
        tn = TextNode("ital", TextType.ITALIC)
        hn = tn.text_node_to_html_node()
        self.assertEqual(hn.to_html(), "<i>ital</i>")

        # code
        tn = TextNode("c", TextType.CODE)
        hn = tn.text_node_to_html_node()
        self.assertEqual(hn.to_html(), "<code>c</code>")

        # link
        tn = TextNode("lnk", TextType.LINK, url="https://x")
        hn = tn.text_node_to_html_node()
        self.assertEqual(hn.to_html(), "<a href=\"https://x\">lnk</a>")

        # image
        tn = TextNode("alt", TextType.IMAGE, url="https://img")
        hn = tn.text_node_to_html_node()
        self.assertEqual(hn.to_html(), "<img src=\"https://img\" alt=\"alt\"></img>")

    def test_extract_title(self):
        from functions import extract_title

        # simple title
        self.assertEqual(extract_title("# My Title"), "My Title")

        # title with extra spaces
        self.assertEqual(extract_title("#   Spaced Title  "), "Spaced Title")

        # first level-1 header is chosen
        md = "# First\n## Second\n# Third"
        self.assertEqual(extract_title(md), "First")

        # no level-1 header raises ValueError (new behavior)
        with self.assertRaises(ValueError):
            extract_title("No headers here\n## Only level2")

        # leading spaces before # do not count (function raises ValueError)
        with self.assertRaises(ValueError):
            extract_title("  # Indented")

    def test_generate_page(self):
        from functions import generate_page

        # Create a temporary directory for test files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create markdown file
            md_path = os.path.join(tmpdir, "test.md")
            md_content = """# My Page Title

This is a paragraph with **bold** text and _italic_ text.

- Item 1
- Item 2
"""
            with open(md_path, 'w') as f:
                f.write(md_content)

            # Create template file
            template_path = os.path.join(tmpdir, "template.html")
            template_content = """<!DOCTYPE html>
<html>
<head>
<title>{{ title }}</title>
</head>
<body>
{{ content }}
</body>
</html>"""
            with open(template_path, 'w') as f:
                f.write(template_content)

            # Generate page
            dest_path = os.path.join(tmpdir, "output.html")
            generate_page(md_path, template_path, dest_path)

            # Verify output file exists
            self.assertTrue(os.path.exists(dest_path))

            # Verify output content
            with open(dest_path, 'r') as f:
                output = f.read()

            # Check that title and content are replaced
            self.assertIn("<title>My Page Title</title>", output)
            self.assertIn("<p>This is a paragraph with <b>bold</b> text and <i>italic</i> text.</p>", output)
            self.assertIn("<ul><li>Item 1</li><li>Item 2</li></ul>", output)
            self.assertNotIn("{{ title }}", output)
            self.assertNotIn("{{ content }}", output)

    def test_generate_page_with_code_block(self):
        from functions import generate_page

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create markdown with code block
            md_path = os.path.join(tmpdir, "code.md")
            md_content = """# Code Example

Here is a code block:

```
def hello():
    print("Hello, World!")
```
"""
            with open(md_path, 'w') as f:
                f.write(md_content)

            # Simple template
            template_path = os.path.join(tmpdir, "template.html")
            template_content = "<html><body><h1>{{ title }}</h1>{{ content }}</body></html>"
            with open(template_path, 'w') as f:
                f.write(template_content)

            # Generate page
            dest_path = os.path.join(tmpdir, "output.html")
            generate_page(md_path, template_path, dest_path)

            # Verify output
            with open(dest_path, 'r') as f:
                output = f.read()

            self.assertIn("<h1>Code Example</h1>", output)
            self.assertIn("<pre>def hello():", output)
            self.assertIn("print(\"Hello, World!\")", output)