import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from textnode import TextNode, TextType
from funcs import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, BlockType, block_to_block_type, markdown_to_html_node


class TestSplitNodesDelimiter(unittest.TestCase):
    """Test suite for the split_nodes_delimiter function"""
    
    def test_split_with_bold_delimiter(self):
        """Test splitting TEXT nodes with bold delimiter **"""
        node = TextNode("This is **bold** text", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        # Should return flat list
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "This is ")
        self.assertEqual(result[0].node_type, TextType.TEXT)
        self.assertEqual(result[1].text, "bold")
        self.assertEqual(result[1].node_type, TextType.BOLD)
        self.assertEqual(result[2].text, " text")
        self.assertEqual(result[2].node_type, TextType.TEXT)
    
    def test_split_with_italic_delimiter(self):
        """Test splitting TEXT nodes with italic delimiter *"""
        node = TextNode("This is *italic* text", TextType.TEXT)
        result = split_nodes_delimiter([node], "*", TextType.ITALIC)
        
        # Should return flat list
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "This is ")
        self.assertEqual(result[1].text, "italic")
        self.assertEqual(result[1].node_type, TextType.ITALIC)
        self.assertEqual(result[2].text, " text")
    
    def test_split_with_code_delimiter(self):
        """Test splitting TEXT nodes with code delimiter `"""
        node = TextNode("Run this `code` in terminal", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        
        # Should return flat list
        self.assertEqual(len(result), 3)
        self.assertEqual(result[1].text, "code")
        self.assertEqual(result[1].node_type, TextType.CODE)
    
    def test_split_unmatched_delimiter_raises_exception(self):
        """Test that unmatched delimiter raises exception"""
        node = TextNode("This has **unmatched bold", TextType.TEXT)
        
        with self.assertRaises(Exception) as context:
            split_nodes_delimiter([node], "**", TextType.BOLD)
        
        self.assertIn("Invalid Markdown syntax", str(context.exception))
        self.assertIn("**", str(context.exception))
    
    def test_split_no_delimiter_in_text(self):
        """Test TEXT node without any delimiters"""
        node = TextNode("No delimiters here", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "No delimiters here")
        self.assertEqual(result[0].node_type, TextType.TEXT)
    
    def test_split_only_delimiters(self):
        """Test TEXT that is only delimiters"""
        node = TextNode("**bold**", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "bold")
        self.assertEqual(result[0].node_type, TextType.BOLD)
    
    def test_split_three_delimiter_pairs(self):
        """Test with three pairs of delimiters"""
        node = TextNode("**one** and **two** plus **three**", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        # Should have 5 elements (bold, text, bold, text, bold)
        self.assertEqual(len(result), 5)
        bold_nodes = [n for n in result if n.node_type == TextType.BOLD]
        self.assertEqual(len(bold_nodes), 3)
    
    def test_split_preserves_non_text_nodes(self):
        """Test that non-TEXT nodes are preserved as-is"""
        text_node = TextNode("Text with **bold**", TextType.TEXT)
        link_node = TextNode("link", TextType.LINK, "https://example.com")
        result = split_nodes_delimiter([text_node, link_node], "**", TextType.BOLD)
        
        # Should have the split text node plus the link node
        self.assertGreater(len(result), 1)
        link_found = False
        for n in result:
            if n.node_type == TextType.LINK:
                link_found = True
                self.assertEqual(n.URL, "https://example.com")
        self.assertTrue(link_found)
    
    def test_split_preserves_text_content(self):
        """Test that all text content is preserved in result"""
        node = TextNode("Original **content** stays", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        # Reconstruct text (without delimiters)
        reconstructed = "".join(n.text for n in result)
        # Should have original content
        self.assertIn("Original", reconstructed)
        self.assertIn("content", reconstructed)
        self.assertIn("stays", reconstructed)
    
    def test_split_with_code_delimiter_backtick(self):
        """Test with backtick delimiter for code"""
        node = TextNode("Code: `print('hello')` here", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        
        code_found = False
        for n in result:
            if n.node_type == TextType.CODE and n.text == "print('hello')":
                code_found = True
        self.assertTrue(code_found)
    
    def test_split_single_pair_delimiter(self):
        """Test with just one pair of delimiters"""
        node = TextNode("Simple **bold** text", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        # Should have 3 elements
        self.assertEqual(len(result), 3)
        self.assertEqual(result[1].node_type, TextType.BOLD)
    
    def test_split_delimiter_at_start(self):
        """Test delimiter at the start of text"""
        node = TextNode("**bold** at start", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        self.assertEqual(result[0].text, "bold")
        self.assertEqual(result[0].node_type, TextType.BOLD)
    
    def test_split_delimiter_at_end(self):
        """Test delimiter at the end of text"""
        node = TextNode("text at end **bold**", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        last_node = result[-1]
        self.assertEqual(last_node.text, "bold")
        self.assertEqual(last_node.node_type, TextType.BOLD)
    
    def test_split_multiple_nodes_mixed(self):
        """Test splitting multiple TextNode objects"""
        node1 = TextNode("First **bold** text", TextType.TEXT)
        node2 = TextNode("Second text", TextType.TEXT)
        result = split_nodes_delimiter([node1, node2], "**", TextType.BOLD)
        
        # Should have flat list
        self.assertGreater(len(result), 2)
        # Find bold node
        bold_found = False
        for n in result:
            if n.node_type == TextType.BOLD:
                bold_found = True
        self.assertTrue(bold_found)
    
    def test_split_mixed_node_types(self):
        """Test with mixed node types in input"""
        text_node = TextNode("Text with **bold** part", TextType.TEXT)
        bold_node = TextNode("already bold", TextType.BOLD)
        code_node = TextNode("code snippet", TextType.CODE)
        
        nodes = [text_node, bold_node, code_node]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        
        # Should have 5 elements from text_node split + 2 from other nodes
        self.assertEqual(len(result), 5)
        # Check that all types are present
        types = set(n.node_type for n in result)
        self.assertIn(TextType.TEXT, types)
        self.assertIn(TextType.BOLD, types)
        self.assertIn(TextType.CODE, types)
    
    def test_split_empty_list(self):
        """Test with empty input list"""
        result = split_nodes_delimiter([], "**", TextType.BOLD)
        self.assertEqual(len(result), 0)
    
    def test_split_returns_flat_list(self):
        """Test that function returns flat list of TextNodes"""
        node = TextNode("Test **bold** text", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, TextNode)
    
    def test_split_text_type_for_delimited_content(self):
        """Test that delimited content gets correct text type"""
        node = TextNode("Before **bold** after", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        bold_nodes = [n for n in result if n.node_type == TextType.BOLD]
        self.assertGreater(len(bold_nodes), 0)
        for bold_node in bold_nodes:
            self.assertEqual(bold_node.node_type, TextType.BOLD)
    
    def test_split_multiple_delimiters_sequence(self):
        """Test with multiple consecutive delimiter pairs"""
        node = TextNode("**bold** then **more bold**", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        bold_count = sum(1 for n in result if n.node_type == TextType.BOLD)
        self.assertEqual(bold_count, 2)
    
    def test_split_alternating_types(self):
        """Test that alternating parts alternate between TEXT and specified type"""
        node = TextNode("a**b**c**d**e", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        
        # Should alternate: TEXT, BOLD, TEXT, BOLD, TEXT
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].node_type, TextType.TEXT)
        self.assertEqual(result[1].node_type, TextType.BOLD)
        self.assertEqual(result[2].node_type, TextType.TEXT)
        self.assertEqual(result[3].node_type, TextType.BOLD)
        self.assertEqual(result[4].node_type, TextType.TEXT)
    
    def test_split_preserves_link_url(self):
        """Test that link node URLs are preserved"""
        link = TextNode("click me", TextType.LINK, "https://example.com")
        result = split_nodes_delimiter([link], "**", TextType.BOLD)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].URL, "https://example.com")
    
    def test_split_multiple_text_nodes_sequence(self):
        """Test with multiple TEXT nodes in sequence"""
        nodes = [
            TextNode("First **bold**", TextType.TEXT),
            TextNode("Second *italic*", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        
        # First node gets split, second stays as is
        self.assertGreater(len(result), 2)


class TestExtractMarkdownImages(unittest.TestCase):
    """Test suite for the extract_markdown_images function"""
    
    def test_extract_single_image(self):
        """Test extracting a single markdown image"""
        text = "![alt text](https://example.com/image.png)"
        result = extract_markdown_images(text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("alt text", "https://example.com/image.png"))
    
    def test_extract_multiple_images(self):
        """Test extracting multiple markdown images"""
        text = "This is text with ![image1](url1) and ![image2](url2)"
        result = extract_markdown_images(text)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("image1", "url1"))
        self.assertEqual(result[1], ("image2", "url2"))
    
    def test_extract_no_images(self):
        """Test text with no images returns empty list"""
        text = "No images here, just plain text"
        result = extract_markdown_images(text)
        
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])
    
    def test_extract_image_with_empty_alt(self):
        """Test extracting image with empty alt text"""
        text = "![](empty-alt.png)"
        result = extract_markdown_images(text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("", "empty-alt.png"))
    
    def test_extract_images_with_surrounding_text(self):
        """Test extracting images with text before and after"""
        text = "![Python logo](https://python.org/logo.png) and some text ![GitHub](https://github.com/logo.svg)"
        result = extract_markdown_images(text)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("Python logo", "https://python.org/logo.png"))
        self.assertEqual(result[1], ("GitHub", "https://github.com/logo.svg"))
    
    def test_extract_images_ignores_links(self):
        """Test that regular links are not extracted as images"""
        text = "This has a [link](url.com) and ![image](img.png)"
        result = extract_markdown_images(text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("image", "img.png"))
    
    def test_extract_image_with_special_chars(self):
        """Test extracting image with special characters in alt and url"""
        text = "![Alt with spaces & special!](https://example.com/path/to/image.jpg?param=value)"
        result = extract_markdown_images(text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "Alt with spaces & special!")


class TestExtractMarkdownLinks(unittest.TestCase):
    """Test suite for the extract_markdown_links function"""
    
    def test_extract_single_link(self):
        """Test extracting a single markdown link"""
        text = "[link text](https://example.com)"
        result = extract_markdown_links(text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("link text", "https://example.com"))
    
    def test_extract_multiple_links(self):
        """Test extracting multiple markdown links"""
        text = "This is text with [link1](url1) and [link2](url2)"
        result = extract_markdown_links(text)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("link1", "url1"))
        self.assertEqual(result[1], ("link2", "url2"))
    
    def test_extract_no_links(self):
        """Test text with no links returns empty list"""
        text = "No links here, just plain text"
        result = extract_markdown_links(text)
        
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])
    
    def test_extract_link_with_empty_anchor(self):
        """Test extracting link with empty anchor text"""
        text = "[](empty-anchor.html)"
        result = extract_markdown_links(text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("", "empty-anchor.html"))
    
    def test_extract_links_with_surrounding_text(self):
        """Test extracting links with text before and after"""
        text = "[Boot.dev](https://boot.dev) is a cool site and [GitHub](https://github.com) too"
        result = extract_markdown_links(text)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("Boot.dev", "https://boot.dev"))
        self.assertEqual(result[1], ("GitHub", "https://github.com"))
    
    def test_extract_links_ignores_images(self):
        """Test that images are not extracted as links"""
        text = "Mix of ![image](img.png) and [link](url.com)"
        result = extract_markdown_links(text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("link", "url.com"))
    
    def test_extract_link_with_special_chars(self):
        """Test extracting link with special characters"""
        text = "[Click here!](https://example.com/path?param=value&other=123)"
        result = extract_markdown_links(text)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "https://example.com/path?param=value&other=123")
    
    def test_extract_link_local_path(self):
        """Test extracting link with local path"""
        text = "[Home](/index.html) and [About](../about.html)"
        result = extract_markdown_links(text)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("Home", "/index.html"))
        self.assertEqual(result[1], ("About", "../about.html"))
    
    def test_extract_mixed_images_and_links(self):
        """Test extracting only links when both images and links present"""
        text = "![img1](i1.png) some text [link1](url1) more ![img2](i2.png) text [link2](url2)"
        result = extract_markdown_links(text)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("link1", "url1"))
        self.assertEqual(result[1], ("link2", "url2"))


class TestSplitNodesImage(unittest.TestCase):
    """Test suite for the split_nodes_image function"""
    
    def test_split_images(self):
        """Test splitting node with multiple images"""
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    
    def test_split_single_image(self):
        """Test splitting node with single image"""
        node = TextNode(
            "Text with ![alt text](https://example.com/img.png) here",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "Text with ")
        self.assertEqual(new_nodes[0].node_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "alt text")
        self.assertEqual(new_nodes[1].node_type, TextType.IMAGE)
        self.assertEqual(new_nodes[1].URL, "https://example.com/img.png")
        self.assertEqual(new_nodes[2].text, " here")
    
    def test_split_image_at_start(self):
        """Test image at the start of text"""
        node = TextNode("![first](img.png) followed by text", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].node_type, TextType.IMAGE)
        self.assertEqual(new_nodes[0].text, "first")
        self.assertEqual(new_nodes[1].text, " followed by text")
    
    def test_split_image_at_end(self):
        """Test image at the end of text"""
        node = TextNode("Text ending with ![last](img.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "Text ending with ")
        self.assertEqual(new_nodes[1].node_type, TextType.IMAGE)
        self.assertEqual(new_nodes[1].text, "last")
    
    def test_split_only_image(self):
        """Test node that is only an image"""
        node = TextNode("![only](img.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].node_type, TextType.IMAGE)
        self.assertEqual(new_nodes[0].text, "only")
        self.assertEqual(new_nodes[0].URL, "img.png")
    
    def test_split_no_images(self):
        """Test node with no images remains unchanged"""
        node = TextNode("Just plain text", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "Just plain text")
        self.assertEqual(new_nodes[0].node_type, TextType.TEXT)
    
    def test_split_preserves_non_text_nodes(self):
        """Test that non-TEXT nodes are preserved"""
        nodes = [
            TextNode("Text with ![img](url.png)", TextType.TEXT),
            TextNode("already a link", TextType.LINK, "https://example.com"),
            TextNode("bold text", TextType.BOLD),
        ]
        new_nodes = split_nodes_image(nodes)
        
        # Should have split first, preserved others
        self.assertGreater(len(new_nodes), 3)
        # Check that link and bold are preserved
        link_found = False
        bold_found = False
        for node in new_nodes:
            if node.node_type == TextType.LINK and node.text == "already a link":
                link_found = True
            if node.node_type == TextType.BOLD and node.text == "bold text":
                bold_found = True
        self.assertTrue(link_found)
        self.assertTrue(bold_found)
    
    def test_split_multiple_nodes(self):
        """Test splitting multiple TEXT nodes"""
        nodes = [
            TextNode("First ![img1](url1.png)", TextType.TEXT),
            TextNode("Second ![img2](url2.png)", TextType.TEXT),
        ]
        new_nodes = split_nodes_image(nodes)
        
        # Should have 4 nodes total (2 text + 2 images)
        self.assertEqual(len(new_nodes), 4)
        image_count = sum(1 for n in new_nodes if n.node_type == TextType.IMAGE)
        self.assertEqual(image_count, 2)
    
    def test_split_empty_alt_text(self):
        """Test image with empty alt text"""
        node = TextNode("Text with ![](img.png) image", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[1].node_type, TextType.IMAGE)
        self.assertEqual(new_nodes[1].text, "")
    
    def test_split_consecutive_images(self):
        """Test multiple images with no text between them"""
        node = TextNode("![img1](url1.png)![img2](url2.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].node_type, TextType.IMAGE)
        self.assertEqual(new_nodes[1].node_type, TextType.IMAGE)


class TestSplitNodesLink(unittest.TestCase):
    """Test suite for the split_nodes_link function"""
    
    def test_split_links(self):
        """Test splitting node with multiple links"""
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )
    
    def test_split_single_link(self):
        """Test splitting node with single link"""
        node = TextNode(
            "Text with [link text](https://example.com) here",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "Text with ")
        self.assertEqual(new_nodes[0].node_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text, "link text")
        self.assertEqual(new_nodes[1].node_type, TextType.LINK)
        self.assertEqual(new_nodes[1].URL, "https://example.com")
        self.assertEqual(new_nodes[2].text, " here")
    
    def test_split_link_at_start(self):
        """Test link at the start of text"""
        node = TextNode("[first](url.com) followed by text", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].node_type, TextType.LINK)
        self.assertEqual(new_nodes[0].text, "first")
        self.assertEqual(new_nodes[1].text, " followed by text")
    
    def test_split_link_at_end(self):
        """Test link at the end of text"""
        node = TextNode("Text ending with [last](url.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text, "Text ending with ")
        self.assertEqual(new_nodes[1].node_type, TextType.LINK)
        self.assertEqual(new_nodes[1].text, "last")
    
    def test_split_only_link(self):
        """Test node that is only a link"""
        node = TextNode("[only](url.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].node_type, TextType.LINK)
        self.assertEqual(new_nodes[0].text, "only")
        self.assertEqual(new_nodes[0].URL, "url.com")
    
    def test_split_no_links(self):
        """Test node with no links remains unchanged"""
        node = TextNode("Just plain text", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text, "Just plain text")
        self.assertEqual(new_nodes[0].node_type, TextType.TEXT)
    
    def test_split_preserves_non_text_nodes(self):
        """Test that non-TEXT nodes are preserved"""
        nodes = [
            TextNode("Text with [link](url.com)", TextType.TEXT),
            TextNode("already an image", TextType.IMAGE, "https://example.com/img.png"),
            TextNode("bold text", TextType.BOLD),
        ]
        new_nodes = split_nodes_link(nodes)
        
        # Should have split first, preserved others
        self.assertGreater(len(new_nodes), 3)
        # Check that image and bold are preserved
        image_found = False
        bold_found = False
        for node in new_nodes:
            if node.node_type == TextType.IMAGE and node.text == "already an image":
                image_found = True
            if node.node_type == TextType.BOLD and node.text == "bold text":
                bold_found = True
        self.assertTrue(image_found)
        self.assertTrue(bold_found)
    
    def test_split_multiple_nodes(self):
        """Test splitting multiple TEXT nodes"""
        nodes = [
            TextNode("First [link1](url1.com)", TextType.TEXT),
            TextNode("Second [link2](url2.com)", TextType.TEXT),
        ]
        new_nodes = split_nodes_link(nodes)
        
        # Should have 4 nodes total (2 text + 2 links)
        self.assertEqual(len(new_nodes), 4)
        link_count = sum(1 for n in new_nodes if n.node_type == TextType.LINK)
        self.assertEqual(link_count, 2)
    
    def test_split_empty_anchor_text(self):
        """Test link with empty anchor text"""
        node = TextNode("Text with [](url.com) link", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[1].node_type, TextType.LINK)
        self.assertEqual(new_nodes[1].text, "")
    
    def test_split_consecutive_links(self):
        """Test multiple links with no text between them"""
        node = TextNode("[link1](url1.com)[link2](url2.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].node_type, TextType.LINK)
        self.assertEqual(new_nodes[1].node_type, TextType.LINK)
    
    def test_split_ignores_images(self):
        """Test that images are not split as links"""
        node = TextNode("Text with ![image](img.png) and [link](url.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        
        # Should only split the link, not the image
        link_count = sum(1 for n in new_nodes if n.node_type == TextType.LINK)
        image_in_text = any("![image](img.png)" in n.text for n in new_nodes if n.node_type == TextType.TEXT)
        
        self.assertEqual(link_count, 1)
        self.assertTrue(image_in_text)
    
    def test_split_local_paths(self):
        """Test links with local file paths"""
        node = TextNode("[home](/index.html) and [about](../about.html)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].URL, "/index.html")
        self.assertEqual(new_nodes[2].URL, "../about.html")


class TestTextToTextnodes(unittest.TestCase):
    """Test cases for text_to_textnodes function"""
    
    def test_comprehensive_example(self):
        """Test the comprehensive example from the assignment"""
        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        
        self.assertEqual(len(nodes), len(expected))
        for i, (node, exp) in enumerate(zip(nodes, expected)):
            self.assertEqual(node.text, exp.text, f"Node {i} text mismatch")
            self.assertEqual(node.node_type, exp.node_type, f"Node {i} type mismatch")
            self.assertEqual(node.URL, exp.URL, f"Node {i} URL mismatch")
    
    def test_plain_text(self):
        """Test with plain text only"""
        text = "This is just plain text"
        nodes = text_to_textnodes(text)
        
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, "This is just plain text")
        self.assertEqual(nodes[0].node_type, TextType.TEXT)
    
    def test_only_bold(self):
        """Test with only bold text"""
        text = "This is **bold** text"
        nodes = text_to_textnodes(text)
        
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].text, "This is ")
        self.assertEqual(nodes[0].node_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "bold")
        self.assertEqual(nodes[1].node_type, TextType.BOLD)
        self.assertEqual(nodes[2].text, " text")
        self.assertEqual(nodes[2].node_type, TextType.TEXT)
    
    def test_only_italic(self):
        """Test with only italic text"""
        text = "This is *italic* text"
        nodes = text_to_textnodes(text)
        
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].text, "This is ")
        self.assertEqual(nodes[1].text, "italic")
        self.assertEqual(nodes[1].node_type, TextType.ITALIC)
        self.assertEqual(nodes[2].text, " text")
    
    def test_only_code(self):
        """Test with only code text"""
        text = "This is `code` text"
        nodes = text_to_textnodes(text)
        
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].text, "This is ")
        self.assertEqual(nodes[1].text, "code")
        self.assertEqual(nodes[1].node_type, TextType.CODE)
        self.assertEqual(nodes[2].text, " text")
    
    def test_only_image(self):
        """Test with only image"""
        text = "Check out this ![cool image](https://example.com/img.png) here"
        nodes = text_to_textnodes(text)
        
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].text, "Check out this ")
        self.assertEqual(nodes[1].text, "cool image")
        self.assertEqual(nodes[1].node_type, TextType.IMAGE)
        self.assertEqual(nodes[1].URL, "https://example.com/img.png")
        self.assertEqual(nodes[2].text, " here")
    
    def test_only_link(self):
        """Test with only link"""
        text = "Visit [my site](https://example.com) today"
        nodes = text_to_textnodes(text)
        
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].text, "Visit ")
        self.assertEqual(nodes[1].text, "my site")
        self.assertEqual(nodes[1].node_type, TextType.LINK)
        self.assertEqual(nodes[1].URL, "https://example.com")
        self.assertEqual(nodes[2].text, " today")
    
    def test_multiple_bold_and_italic(self):
        """Test with multiple bold and italic sections"""
        text = "**Bold1** and *italic1* then **bold2** and *italic2*"
        nodes = text_to_textnodes(text)
        
        self.assertEqual(nodes[0].text, "Bold1")
        self.assertEqual(nodes[0].node_type, TextType.BOLD)
        self.assertEqual(nodes[1].text, " and ")
        self.assertEqual(nodes[2].text, "italic1")
        self.assertEqual(nodes[2].node_type, TextType.ITALIC)
        self.assertEqual(nodes[3].text, " then ")
        self.assertEqual(nodes[4].text, "bold2")
        self.assertEqual(nodes[4].node_type, TextType.BOLD)
    
    def test_mixed_formatting_no_images_links(self):
        """Test with mixed bold, italic, and code but no images or links"""
        text = "Here is **bold** and *italic* and `code` text"
        nodes = text_to_textnodes(text)
        
        self.assertEqual(len(nodes), 7)
        self.assertEqual(nodes[1].node_type, TextType.BOLD)
        self.assertEqual(nodes[3].node_type, TextType.ITALIC)
        self.assertEqual(nodes[5].node_type, TextType.CODE)
    
    def test_consecutive_formatting(self):
        """Test with consecutive formatting markers"""
        text = "**bold***italic*`code`"
        nodes = text_to_textnodes(text)
        
        self.assertEqual(nodes[0].text, "bold")
        self.assertEqual(nodes[0].node_type, TextType.BOLD)
        self.assertEqual(nodes[1].text, "italic")
        self.assertEqual(nodes[1].node_type, TextType.ITALIC)
        self.assertEqual(nodes[2].text, "code")
        self.assertEqual(nodes[2].node_type, TextType.CODE)
    
    def test_image_and_link_together(self):
        """Test with both image and link"""
        text = "![img](url1) and [link](url2)"
        nodes = text_to_textnodes(text)
        
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].node_type, TextType.IMAGE)
        self.assertEqual(nodes[0].URL, "url1")
        self.assertEqual(nodes[1].text, " and ")
        self.assertEqual(nodes[2].node_type, TextType.LINK)
        self.assertEqual(nodes[2].URL, "url2")
    
    def test_all_types_mixed(self):
        """Test with all formatting types mixed together"""
        text = "Start **bold** *italic* `code` ![img](i.png) [link](l.com) end"
        nodes = text_to_textnodes(text)
        
        # Find each type
        bold_nodes = [n for n in nodes if n.node_type == TextType.BOLD]
        italic_nodes = [n for n in nodes if n.node_type == TextType.ITALIC]
        code_nodes = [n for n in nodes if n.node_type == TextType.CODE]
        image_nodes = [n for n in nodes if n.node_type == TextType.IMAGE]
        link_nodes = [n for n in nodes if n.node_type == TextType.LINK]
        
        self.assertEqual(len(bold_nodes), 1)
        self.assertEqual(len(italic_nodes), 1)
        self.assertEqual(len(code_nodes), 1)
        self.assertEqual(len(image_nodes), 1)
        self.assertEqual(len(link_nodes), 1)


class TestMarkdownToBlocks(unittest.TestCase):
    """Test cases for markdown_to_blocks function"""
    
    def test_markdown_to_blocks(self):
        """Test the provided example from the assignment"""
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
    
    def test_single_block(self):
        """Test with a single block (no double newlines)"""
        md = "This is a single paragraph"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a single paragraph"])
    
    def test_multiple_simple_blocks(self):
        """Test with multiple simple blocks"""
        md = "Block 1\n\nBlock 2\n\nBlock 3"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Block 1", "Block 2", "Block 3"])
    
    def test_excessive_newlines(self):
        """Test that excessive newlines are handled correctly"""
        md = "Block 1\n\n\n\nBlock 2\n\n\n\n\nBlock 3"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Block 1", "Block 2", "Block 3"])
    
    def test_leading_trailing_whitespace(self):
        """Test that leading and trailing whitespace is stripped"""
        md = "  Block 1  \n\n   Block 2   \n\n\tBlock 3\t"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Block 1", "Block 2", "Block 3"])
    
    def test_heading_block(self):
        """Test with heading blocks"""
        md = "# Heading 1\n\n## Heading 2\n\nParagraph"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["# Heading 1", "## Heading 2", "Paragraph"])
    
    def test_code_block(self):
        """Test with code block"""
        md = "```\ncode line 1\ncode line 2\n```\n\nParagraph"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["```\ncode line 1\ncode line 2\n```", "Paragraph"])
    
    def test_list_block(self):
        """Test with list blocks"""
        md = "- Item 1\n- Item 2\n- Item 3\n\n1. Numbered 1\n2. Numbered 2"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["- Item 1\n- Item 2\n- Item 3", "1. Numbered 1\n2. Numbered 2"])
    
    def test_quote_block(self):
        """Test with quote blocks"""
        md = "> Quote line 1\n> Quote line 2\n\nParagraph"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["> Quote line 1\n> Quote line 2", "Paragraph"])
    
    def test_empty_string(self):
        """Test with empty string"""
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])
    
    def test_only_whitespace(self):
        """Test with only whitespace"""
        md = "   \n\n   \n\n\t\t\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])
    
    def test_mixed_content(self):
        """Test with mixed content types"""
        md = """# Title

This is a paragraph with **bold** and *italic*.

- List item 1
- List item 2

> A quote

```
code block
```

Final paragraph."""
        blocks = markdown_to_blocks(md)
        self.assertEqual(len(blocks), 6)
        self.assertEqual(blocks[0], "# Title")
        self.assertEqual(blocks[1], "This is a paragraph with **bold** and *italic*.")
        self.assertEqual(blocks[2], "- List item 1\n- List item 2")
        self.assertEqual(blocks[3], "> A quote")
        self.assertEqual(blocks[4], "```\ncode block\n```")
        self.assertEqual(blocks[5], "Final paragraph.")
    
    def test_preserves_single_newlines(self):
        """Test that single newlines within blocks are preserved"""
        md = "Line 1\nLine 2\nLine 3\n\nNew block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Line 1\nLine 2\nLine 3", "New block"])


class TestBlockToBlockType(unittest.TestCase):
    """Test cases for block_to_block_type function"""
    
    def test_heading_h1(self):
        """Test h1 heading"""
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    
    def test_heading_h2(self):
        """Test h2 heading"""
        block = "## This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    
    def test_heading_h3(self):
        """Test h3 heading"""
        block = "### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    
    def test_heading_h4(self):
        """Test h4 heading"""
        block = "#### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    
    def test_heading_h5(self):
        """Test h5 heading"""
        block = "##### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    
    def test_heading_h6(self):
        """Test h6 heading"""
        block = "###### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    
    def test_heading_too_many_hashes(self):
        """Test that 7+ # is not a heading"""
        block = "####### Not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_heading_no_space(self):
        """Test that # without space is not a heading"""
        block = "#No space"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_heading_with_content(self):
        """Test heading with various content"""
        block = "## Heading with **bold** and *italic*"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    
    def test_code_block(self):
        """Test code block"""
        block = "```\ncode here\nmore code\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
    
    def test_code_block_single_line(self):
        """Test single line code block"""
        block = "```code```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
    
    def test_code_block_with_language(self):
        """Test code block with language specifier"""
        block = "```python\nprint('hello')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
    
    def test_code_block_only_start(self):
        """Test that block with only starting ``` is not code"""
        block = "```\ncode here"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_quote_single_line(self):
        """Test single line quote"""
        block = ">This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)
    
    def test_quote_multi_line(self):
        """Test multi-line quote"""
        block = ">Line 1\n>Line 2\n>Line 3"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)
    
    def test_quote_with_spaces(self):
        """Test quote with space after >"""
        block = "> Quote with space\n> Another line"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)
    
    def test_quote_incomplete(self):
        """Test that not all lines starting with > is not a quote"""
        block = ">Line 1\nLine 2\n>Line 3"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_unordered_list_single_item(self):
        """Test single item unordered list"""
        block = "- Item 1"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)
    
    def test_unordered_list_multiple_items(self):
        """Test multiple items unordered list"""
        block = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)
    
    def test_unordered_list_with_content(self):
        """Test unordered list with formatted content"""
        block = "- **Bold** item\n- *Italic* item\n- `code` item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)
    
    def test_unordered_list_incomplete(self):
        """Test that not all lines with - is not unordered list"""
        block = "- Item 1\nItem 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_unordered_list_no_space(self):
        """Test that - without space is not unordered list"""
        block = "-Item 1\n-Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_ordered_list_single_item(self):
        """Test single item ordered list"""
        block = "1. Item 1"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)
    
    def test_ordered_list_multiple_items(self):
        """Test multiple items ordered list"""
        block = "1. Item 1\n2. Item 2\n3. Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)
    
    def test_ordered_list_many_items(self):
        """Test ordered list with many items"""
        block = "1. First\n2. Second\n3. Third\n4. Fourth\n5. Fifth"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)
    
    def test_ordered_list_wrong_start(self):
        """Test that list not starting at 1 is not ordered list"""
        block = "2. Item 1\n3. Item 2\n4. Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_ordered_list_wrong_increment(self):
        """Test that list not incrementing by 1 is not ordered list"""
        block = "1. Item 1\n2. Item 2\n4. Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_ordered_list_no_space(self):
        """Test that number. without space is not ordered list"""
        block = "1.Item 1\n2.Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_paragraph_simple(self):
        """Test simple paragraph"""
        block = "This is a paragraph"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_paragraph_multiline(self):
        """Test multi-line paragraph"""
        block = "This is a paragraph\nwith multiple lines\nof text"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_paragraph_with_formatting(self):
        """Test paragraph with inline formatting"""
        block = "This is **bold** and *italic* text"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_paragraph_with_link(self):
        """Test paragraph with link"""
        block = "Check out [this link](https://example.com)"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_paragraph_with_image(self):
        """Test paragraph with image"""
        block = "Here is an image: ![alt](url)"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_edge_case_hash_in_middle(self):
        """Test that # in middle of line is paragraph"""
        block = "This has # in the middle"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_edge_case_backticks_in_middle(self):
        """Test that ``` only at start/end makes code block"""
        block = "Some text ``` code ``` more text"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_mixed_list_markers(self):
        """Test that mixing - and numbers is paragraph"""
        block = "- Item 1\n1. Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


class TestMarkdownToHtmlNode(unittest.TestCase):
    """Test cases for markdown_to_html_node function"""
    
    def test_paragraphs(self):
        """Test the provided paragraph example from the assignment"""
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )
    
    def test_codeblock(self):
        """Test the provided codeblock example from the assignment"""
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )
    
    def test_single_paragraph(self):
        """Test with a single paragraph"""
        md = "This is a simple paragraph."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p>This is a simple paragraph.</p></div>")
    
    def test_heading_h1(self):
        """Test h1 heading"""
        md = "# Main Title"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h1>Main Title</h1></div>")
    
    def test_heading_h2(self):
        """Test h2 heading"""
        md = "## Subtitle"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h2>Subtitle</h2></div>")
    
    def test_heading_with_formatting(self):
        """Test heading with bold and italic"""
        md = "### Heading with **bold** and *italic*"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h3>Heading with <b>bold</b> and <i>italic</i></h3></div>")
    
    def test_unordered_list(self):
        """Test unordered list"""
        md = """- Item 1
- Item 2
- Item 3"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul></div>")
    
    def test_unordered_list_with_formatting(self):
        """Test unordered list with inline formatting"""
        md = """- **Bold** item
- *Italic* item
- `Code` item"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><ul><li><b>Bold</b> item</li><li><i>Italic</i> item</li><li><code>Code</code> item</li></ul></div>")
    
    def test_ordered_list(self):
        """Test ordered list"""
        md = """1. First
2. Second
3. Third"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><ol><li>First</li><li>Second</li><li>Third</li></ol></div>")
    
    def test_ordered_list_with_formatting(self):
        """Test ordered list with inline formatting"""
        md = """1. **First** item
2. *Second* item
3. `Third` item"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><ol><li><b>First</b> item</li><li><i>Second</i> item</li><li><code>Third</code> item</li></ol></div>")
    
    def test_quote_single_line(self):
        """Test single line quote"""
        md = ">This is a quote"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><blockquote>This is a quote</blockquote></div>")
    
    def test_quote_multi_line(self):
        """Test multi-line quote"""
        md = """>Line 1
>Line 2
>Line 3"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><blockquote>Line 1\nLine 2\nLine 3</blockquote></div>")
    
    def test_quote_with_formatting(self):
        """Test quote with inline formatting"""
        md = ">This is **bold** and *italic*"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><blockquote>This is <b>bold</b> and <i>italic</i></blockquote></div>")
    
    def test_mixed_content(self):
        """Test document with multiple block types"""
        md = """# Heading

Paragraph with **bold** text.

- List item 1
- List item 2

>A quote"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertIn("<h1>Heading</h1>", html)
        self.assertIn("<p>Paragraph with <b>bold</b> text.</p>", html)
        self.assertIn("<ul><li>List item 1</li><li>List item 2</li></ul>", html)
        self.assertIn("<blockquote>A quote</blockquote>", html)
    
    def test_paragraph_with_link(self):
        """Test paragraph with a link"""
        md = "Check out [this link](https://example.com) here"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, '<div><p>Check out <a href="https://example.com">this link</a> here</p></div>')
    
    def test_paragraph_with_image(self):
        """Test paragraph with an image"""
        md = "Here is an ![image](https://example.com/img.png) embedded"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, '<div><p>Here is an <img src="https://example.com/img.png" alt="image"></img> embedded</p></div>')
    
    def test_code_block_with_language(self):
        """Test code block with language specifier"""
        md = """```python
def hello():
    print("world")
```"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, '<div><pre><code>def hello():\n    print("world")\n</code></pre></div>')
    
    def test_complex_document(self):
        """Test a complex document with all block types"""
        md = """# Main Title

This is an introduction paragraph with **bold** and *italic* text.

## Subsection

Here's a list:

- First item
- Second item with `code`
- Third item

And an ordered list:

1. Step one
2. Step two
3. Step three

>This is a quote
>spanning multiple lines

```
code block here
with multiple lines
```

Final paragraph with a [link](https://boot.dev) and an ![image](img.png)."""
        
        node = markdown_to_html_node(md)
        html = node.to_html()
        
        # Verify it starts and ends with div
        self.assertTrue(html.startswith("<div>"))
        self.assertTrue(html.endswith("</div>"))
        
        # Verify all expected elements are present
        self.assertIn("<h1>Main Title</h1>", html)
        self.assertIn("<h2>Subsection</h2>", html)
        self.assertIn("<b>bold</b>", html)
        self.assertIn("<i>italic</i>", html)
        self.assertIn("<ul>", html)
        self.assertIn("<ol>", html)
        self.assertIn("<blockquote>", html)
        self.assertIn("<pre><code>", html)
        self.assertIn('<a href="https://boot.dev">link</a>', html)
        self.assertIn('<img src="img.png" alt="image">', html)


if __name__ == "__main__":
    unittest.main()
