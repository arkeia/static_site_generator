import unittest

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