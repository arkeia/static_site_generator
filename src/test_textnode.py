import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        node3 = TextNode("This is a different text node", TextType.ITALIC)
        node4 = TextNode("This is a text node", TextType.LINK, "https://example.com")
        node5 = TextNode("This is a text node", TextType.LINK, None)
        node6 = TextNode("This is a text node", TextType.LINK, "https://example.com")
        self.assertEqual(node, node2)
        self.assertNotEqual(node, node3)
        self.assertNotEqual(node4, node5)
        self.assertEqual(node4, node6)

    def test_text(self):
        node = TextNode("This is a text node", TextType.PLAIN)
        html_node = TextNode.text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    
    def test_link_without_url_raises(self):
        node = TextNode("This is a link", TextType.LINK)
        with self.assertRaises(ValueError):
            TextNode.text_node_to_html_node(node)
    
    def test_image_without_url_raises(self):
        node = TextNode("This is an image", TextType.IMAGE)
        with self.assertRaises(ValueError):
            TextNode.text_node_to_html_node(node)

    def test_repr(self):
        node = TextNode("Sample text", TextType.ITALIC, "https://example.com")
        expected_repr = "TextNode('Sample text', TextType.ITALIC, 'https://example.com')"
        self.assertEqual(repr(node), expected_repr)

if __name__ == "__main__":
    unittest.main()