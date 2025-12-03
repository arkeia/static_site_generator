import unittest

from htmlnode import HtmlNode, LeafNode, ParentNode

class TestHtmlNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HtmlNode(tag="div", props={"class": "container", "id": "main"})
        node2 = HtmlNode(tag="div")
        expected_html = ' class="container" id="main"'
        self.assertEqual(node.props_to_html(), expected_html)

        node_no_props = HtmlNode(tag="span")
        self.assertEqual(node_no_props.props_to_html(), "")
        self.assertNotEqual(node, node2)

class TestLeafNode(unittest.TestCase):
    def test_to_html(self):
        leaf = LeafNode(tag="p", value="Hello, World!", props={"class": "text"})
        expected_html = '<p class="text">Hello, World!</p>'
        self.assertEqual(leaf.to_html(), expected_html)

        leaf_no_tag = LeafNode(tag=None, value="Just text")
        self.assertEqual(leaf_no_tag.to_html(), "Just text")

        with self.assertRaises(ValueError):
            leaf_no_value = LeafNode(tag="p", value=None)
            leaf_no_value.to_html()

class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

if __name__ == "__main__":
    unittest.main()