import unittest

from textnode import TextNode, TextType
from funcs import text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)


class TestTextNodeToHtmlNode(unittest.TestCase):
    def test_text(self):
        """Test TEXT type converts to LeafNode with no tag"""
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    
    def test_bold(self):
        """Test BOLD type converts to LeafNode with 'b' tag"""
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")
        self.assertEqual(html_node.to_html(), "<b>Bold text</b>")
    
    def test_italic(self):
        """Test ITALIC type converts to LeafNode with 'i' tag"""
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")
        self.assertEqual(html_node.to_html(), "<i>Italic text</i>")
    
    def test_code(self):
        """Test CODE type converts to LeafNode with 'code' tag"""
        node = TextNode("print('hello')", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('hello')")
        self.assertEqual(html_node.to_html(), "<code>print('hello')</code>")
    
    def test_link(self):
        """Test LINK type converts to LeafNode with 'a' tag and href prop"""
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props["href"], "https://example.com")
        self.assertIn("href=\"https://example.com\"", html_node.to_html())
    
    def test_image(self):
        """Test IMAGE type converts to LeafNode with 'img' tag and src/alt props"""
        node = TextNode("Alt text", TextType.IMAGE, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props["src"], "https://example.com/image.png")
        self.assertEqual(html_node.props["alt"], "Alt text")
    
    def test_unsupported_type(self):
        """Test that unsupported TextType raises ValueError"""
        node = TextNode("Some text", TextType.UNDERLINED)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)
    
    def test_plain_type_raises(self):
        """Test that PLAIN type raises ValueError"""
        node = TextNode("Some text", TextType.PLAIN)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)
    
    def test_text_empty_string(self):
        """Test TEXT type with empty string"""
        node = TextNode("", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.to_html(), "")
    
    def test_bold_special_characters(self):
        """Test BOLD type with special characters"""
        node = TextNode("Bold <text> & \"stuff\"", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertIn("Bold <text> & \"stuff\"", html_node.value)
    
    def test_italic_with_spaces(self):
        """Test ITALIC type with multiple spaces"""
        node = TextNode("   Italic   text   ", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "   Italic   text   ")
    
    def test_code_with_newlines(self):
        """Test CODE type with newlines"""
        code_text = "def hello():\\n    print('world')"
        node = TextNode(code_text, TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, code_text)
    
    def test_link_with_hash(self):
        """Test LINK type with URL containing hash and params"""
        node = TextNode("Link", TextType.LINK, "https://example.com/page#section?param=value")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.props["href"], "https://example.com/page#section?param=value")
    
    def test_link_local_path(self):
        """Test LINK type with local path"""
        node = TextNode("Home", TextType.LINK, "/index.html")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.props["href"], "/index.html")
    
    def test_image_alt_text_empty(self):
        """Test IMAGE type with empty alt text"""
        node = TextNode("", TextType.IMAGE, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props["alt"], "")
    
    def test_image_alt_text_with_quotes(self):
        """Test IMAGE type with alt text containing quotes"""
        node = TextNode("A picture of \"something\" cool", TextType.IMAGE, "https://example.com/pic.jpg")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.props["alt"], "A picture of \"something\" cool")
    
    def test_image_special_chars_in_url(self):
        """Test IMAGE type with special characters in URL"""
        url = "https://example.com/image%20file.png"
        node = TextNode("Encoded image", TextType.IMAGE, url)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.props["src"], url)
    
    def test_quote_type_raises(self):
        """Test that QUOTE type raises ValueError"""
        node = TextNode("Quoted text", TextType.QUOTE)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)
    
    def test_heading_type_raises(self):
        """Test that HEADING type raises ValueError"""
        node = TextNode("Heading text", TextType.HEADING)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)
    
    def test_list_item_type_raises(self):
        """Test that LIST_ITEM type raises ValueError"""
        node = TextNode("Item text", TextType.LIST_ITEM)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)
    
    def test_text_html_output(self):
        """Test TEXT type HTML output"""
        node = TextNode("Raw text content", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.to_html(), "Raw text content")
    
    def test_bold_html_output_format(self):
        """Test BOLD HTML output format"""
        node = TextNode("important", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        html_output = html_node.to_html()
        self.assertTrue(html_output.startswith("<b>"))
        self.assertTrue(html_output.endswith("</b>"))
    
    def test_italic_html_output_format(self):
        """Test ITALIC HTML output format"""
        node = TextNode("emphasis", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        html_output = html_node.to_html()
        self.assertTrue(html_output.startswith("<i>"))
        self.assertTrue(html_output.endswith("</i>"))
    
    def test_code_html_output_format(self):
        """Test CODE HTML output format"""
        node = TextNode("x = 5", TextType.CODE)
        html_node = text_node_to_html_node(node)
        html_output = html_node.to_html()
        self.assertTrue(html_output.startswith("<code>"))
        self.assertTrue(html_output.endswith("</code>"))
    
    def test_link_href_prop_set(self):
        """Test LINK has href prop set correctly"""
        url = "https://boot.dev"
        node = TextNode("Boot Dev", TextType.LINK, url)
        html_node = text_node_to_html_node(node)
        self.assertIn("href", html_node.props)
        self.assertEqual(html_node.props["href"], url)
    
    def test_image_props_complete(self):
        """Test IMAGE has both src and alt props"""
        url = "https://example.com/photo.jpg"
        alt = "A beautiful photo"
        node = TextNode(alt, TextType.IMAGE, url)
        html_node = text_node_to_html_node(node)
        self.assertIn("src", html_node.props)
        self.assertIn("alt", html_node.props)
        self.assertEqual(html_node.props["src"], url)
        self.assertEqual(html_node.props["alt"], alt)
        
if __name__ == "__main__":
    unittest.main()
