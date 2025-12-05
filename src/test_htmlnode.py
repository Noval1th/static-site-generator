import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_htmlnode_initialization_with_all_params(self):
        """Test HTMLNode initialization with all parameters"""
        props = {"class": "container", "id": "main"}
        children = [HTMLNode(tag="span", value="child")]
        node = HTMLNode(
            tag="div",
            value="test content",
            children=children,
            props=props
        )
        
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "test content")
        self.assertEqual(node.children, children)
        self.assertEqual(node.props, props)
    
    def test_htmlnode_initialization_with_defaults(self):
        """Test HTMLNode initialization with default values"""
        node = HTMLNode()
        
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertEqual(node.children, [])
        self.assertEqual(node.props, {})
    
    def test_props_to_html(self):
        """Test props_to_html method converts props dict to HTML string"""
        props = {"class": "card", "id": "card-1", "data-value": "test"}
        node = HTMLNode(tag="div", props=props)
        props_html = node.props_to_html()
        
        self.assertIn('class="card"', props_html)
        self.assertIn('id="card-1"', props_html)
        self.assertIn('data-value="test"', props_html)
    
    def test_props_to_html_empty(self):
        """Test props_to_html with empty props"""
        node = HTMLNode(tag="div")
        props_html = node.props_to_html()
        
        self.assertEqual(props_html, "")
    
    def test_htmlnode_repr(self):
        """Test __repr__ method returns expected string representation"""
        props = {"class": "button"}
        node = HTMLNode(tag="button", value="Click me", props=props)
        repr_str = repr(node)
        
        self.assertIn("tag=button", repr_str)
        self.assertIn("value=Click me", repr_str)
        self.assertIn("props=", repr_str)
    
    def test_to_html_not_implemented(self):
        """Test to_html method raises NotImplementedError"""
        node = HTMLNode(tag="div", value="test")
        
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_leaf_initialization(self):
        props = {"style": "color:red;"}
        node = LeafNode("span", "Red text", props)
        
        self.assertEqual(node.tag, "span")
        self.assertEqual(node.value, "Red text")
        self.assertEqual(node.children, [])
        self.assertEqual(node.props, props) 

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
        
    def test_leaf_to_html_with_props(self):
        props = {"class": "intro", "id": "first-paragraph"}
        node = LeafNode("p", "Hello, world!", props)
        self.assertEqual(node.to_html(), '<p class="intro" id="first-paragraph">Hello, world!</p>')
        
    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Just some text")
        self.assertEqual(node.to_html(), "Just some text")
        
    def test_leaf_to_html_no_value(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()  
            
    def test_leaf_noValue(self):
        node = LeafNode("div", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    
    def test_parent_initialization(self):
        """Test ParentNode initialization with tag, children, and props"""
        child = LeafNode("span", "text")
        props = {"class": "container"}
        parent = ParentNode("div", [child], props)
        
        self.assertEqual(parent.tag, "div")
        self.assertIsNone(parent.value)
        self.assertEqual(parent.children, [child])
        self.assertEqual(parent.props, props)
    
    def test_parent_to_html_no_tag(self):
        """Test ParentNode.to_html() raises ValueError when tag is None"""
        child = LeafNode("span", "text")
        parent = ParentNode(None, [child])
        
        with self.assertRaises(ValueError):
            parent.to_html()
    
    def test_parent_to_html_no_children(self):
        """Test ParentNode.to_html() raises ValueError when children list is empty"""
        parent = ParentNode("div", [])
        
        with self.assertRaises(ValueError):
            parent.to_html()
    
    def test_parent_to_html_no_children_none(self):
        """Test ParentNode.to_html() raises ValueError when children is None"""
        parent = ParentNode("div", None)
        
        with self.assertRaises(ValueError):
            parent.to_html()
    
    def test_parent_to_html_with_props(self):
        """Test ParentNode.to_html() with props includes them in opening tag"""
        child = LeafNode("span", "text")
        props = {"class": "wrapper", "id": "main"}
        parent = ParentNode("div", [child], props)
        html = parent.to_html()
        
        self.assertIn('class="wrapper"', html)
        self.assertIn('id="main"', html)
        self.assertTrue(html.startswith('<div'))
        self.assertTrue(html.endswith('</div>'))
    
    def test_parent_to_html_multiple_children(self):
        """Test ParentNode.to_html() with multiple children"""
        child1 = LeafNode("span", "first")
        child2 = LeafNode("span", "second")
        child3 = LeafNode("span", "third")
        parent = ParentNode("div", [child1, child2, child3])
        
        html = parent.to_html()
        self.assertEqual(
            html,
            "<div><span>first</span><span>second</span><span>third</span></div>"
        )
    
    def test_parent_to_html_mixed_children(self):
        """Test ParentNode.to_html() with both LeafNode and ParentNode children"""
        leaf = LeafNode("b", "bold")
        nested_leaf = LeafNode("i", "italic")
        nested_parent = ParentNode("em", [nested_leaf])
        parent = ParentNode("p", [leaf, nested_parent])
        
        html = parent.to_html()
        self.assertEqual(html, "<p><b>bold</b><em><i>italic</i></em></p>")
    
    def test_parent_to_html_deeply_nested(self):
        """Test ParentNode.to_html() with deeply nested structure"""
        level3 = LeafNode("span", "deep")
        level2 = ParentNode("div", [level3])
        level1 = ParentNode("section", [level2])
        
        html = level1.to_html()
        self.assertEqual(html, "<section><div><span>deep</span></div></section>")
    
    def test_parent_initialization_default_props(self):
        """Test ParentNode initialization with default props"""
        child = LeafNode("p", "text")
        parent = ParentNode("div", [child])
        
        self.assertEqual(parent.props, {})
    
    
if __name__ == "__main__":
    unittest.main()
