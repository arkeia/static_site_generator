import unittest

from textnode import TextNode, TextType
from functions import split_nodes_delimiter

class TestFunctions(unittest.TestCase):
    def test_split_nodes_delimiter(self):
        nodes = [
            TextNode("Hello, this is a test. Split here. This is after the split. Split here again. And here.", TextType.TEXT),
            TextNode("No delimiters", TextType.TEXT),
        ]
        delimiter = "Split here"
        result = split_nodes_delimiter(nodes, delimiter, TextType.TEXT)
        expected = [
            [TextNode("Hello, this is a test. ", TextType.TEXT)],
            [TextNode(". This is after the split.", TextType.TEXT)],
            [TextNode(" again. And here.", TextType.TEXT)],
            [TextNode("No delimiters", TextType.TEXT)],
        ]

        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected_new_nodes = [
            [TextNode("This is text with a ", TextType.TEXT)],
            [TextNode("code block", TextType.CODE)],
            [TextNode(" word", TextType.TEXT)],
        ]
        self.assertEqual(new_nodes, expected_new_nodes)



    def test_split_nodes_delimiter_raises(self):
        node = TextNode("This is a test with unmatched delimiter ` here.", TextType.TEXT)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "`", TextType.CODE)