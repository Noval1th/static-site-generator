from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re
from enum import Enum


class BlockType(Enum):
    """Enumeration of markdown block types"""
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Splits a list of TextNode objects based on a specified delimiter.
    
    Args:
        old_nodes (list of TextNode): The original list of TextNode objects to be split.
        delimiter (str): The string delimiter used to split the text.
        text_type (TextType): The TextType to assign to the new TextNode objects created from the split text.
        
    Returns:
        list of TextNode: A flat list of TextNode objects with delimited content converted to the specified type.
    """
    new_nodes = []

    for node in old_nodes:
        if node.node_type == TextType.TEXT:
            parts = node.text.split(delimiter)
            if len(parts) % 2 == 0:
                raise Exception(f"Invalid Markdown syntax: unmatched '{delimiter}' delimiter")
            for i, part in enumerate(parts):
                if part:
                    if i % 2 == 0:
                        # Text parts remain as TEXT
                        new_nodes.append(TextNode(part, TextType.TEXT))
                    else:
                        # Delimited parts get the specified type
                        new_nodes.append(TextNode(part, text_type))
        else:
            # Non-TEXT nodes are preserved as-is
            new_nodes.append(node)

    return new_nodes

def extract_markdown_images(text):
    """
    Extract markdown image syntax from text.
    
    Args:
        text (str): Raw markdown text
        
    Returns:
        list of tuples: Each tuple contains (alt_text, url) for markdown images.
        
    Example:
        >>> extract_markdown_images("![alt](url)")
        [("alt", "url")]
    """
    # Regex pattern to match ![alt text](url)
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    """
    Extract markdown link syntax from text.
    
    Args:
        text (str): Raw markdown text
        
    Returns:
        list of tuples: Each tuple contains (anchor_text, url) for markdown links.
        
    Example:
        >>> extract_markdown_links("[link text](url)")
        [("link text", "url")]
    """
    # Regex pattern to match [anchor text](url) but not ![alt](url)
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes):
    """
    Split TextNodes based on markdown image syntax.
    
    Args:
        old_nodes (list of TextNode): The original list of TextNode objects to be split.
        
    Returns:
        list of TextNode: A flat list of TextNode objects with images converted to IMAGE type.
        
    Example:
        >>> node = TextNode("Text with ![alt](url) image", TextType.TEXT)
        >>> split_nodes_image([node])
        [TextNode("Text with ", TextType.TEXT), TextNode("alt", TextType.IMAGE, "url"), TextNode(" image", TextType.TEXT)]
    """
    new_nodes = []
    
    for node in old_nodes:
        if node.node_type != TextType.TEXT:
            # Non-TEXT nodes are preserved as-is
            new_nodes.append(node)
            continue
        
        # Extract all images from this node
        images = extract_markdown_images(node.text)
        
        if not images:
            # No images found, keep the node as-is
            new_nodes.append(node)
            continue
        
        # Split the text by images
        remaining_text = node.text
        for alt_text, url in images:
            # Find the full image markdown syntax
            image_markdown = f"![{alt_text}]({url})"
            parts = remaining_text.split(image_markdown, 1)
            
            # Add text before the image (if any)
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            
            # Add the image node
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            
            # Continue with remaining text
            remaining_text = parts[1] if len(parts) > 1 else ""
        
        # Add any remaining text after the last image
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    
    return new_nodes


def split_nodes_link(old_nodes):
    """
    Split TextNodes based on markdown link syntax.
    
    Args:
        old_nodes (list of TextNode): The original list of TextNode objects to be split.
        
    Returns:
        list of TextNode: A flat list of TextNode objects with links converted to LINK type.
        
    Example:
        >>> node = TextNode("Text with [anchor](url) link", TextType.TEXT)
        >>> split_nodes_link([node])
        [TextNode("Text with ", TextType.TEXT), TextNode("anchor", TextType.LINK, "url"), TextNode(" link", TextType.TEXT)]
    """
    new_nodes = []
    
    for node in old_nodes:
        if node.node_type != TextType.TEXT:
            # Non-TEXT nodes are preserved as-is
            new_nodes.append(node)
            continue
        
        # Extract all links from this node
        links = extract_markdown_links(node.text)
        
        if not links:
            # No links found, keep the node as-is
            new_nodes.append(node)
            continue
        
        # Split the text by links
        remaining_text = node.text
        for anchor_text, url in links:
            # Find the full link markdown syntax
            link_markdown = f"[{anchor_text}]({url})"
            parts = remaining_text.split(link_markdown, 1)
            
            # Add text before the link (if any)
            if parts[0]:
                new_nodes.append(TextNode(parts[0], TextType.TEXT))
            
            # Add the link node
            new_nodes.append(TextNode(anchor_text, TextType.LINK, url))
            
            # Continue with remaining text
            remaining_text = parts[1] if len(parts) > 1 else ""
        
        # Add any remaining text after the last link
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    
    return new_nodes


def text_to_textnodes(text):
    """
    Convert raw markdown text into a list of TextNode objects.
    
    Processes the text by splitting on delimiters for bold, italic, code,
    and then extracting images and links.
    
    Args:
        text (str): Raw markdown text
        
    Returns:
        list of TextNode: A list of TextNode objects representing the parsed markdown.
        
    Example:
        >>> text_to_textnodes("This is **bold** and _italic_")
        [TextNode("This is ", TextType.TEXT), TextNode("bold", TextType.BOLD), ...]
    """
    # Start with a single TEXT node containing all the text
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Apply all the splitting functions in sequence
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    
    return nodes


def markdown_to_blocks(markdown):
    """
    Split a markdown document into blocks.
    
    Blocks are separated by blank lines (double newlines). Leading and trailing
    whitespace is stripped from each block, and empty blocks are removed.
    
    Args:
        markdown (str): Raw markdown text representing a full document
        
    Returns:
        list of str: A list of block strings with whitespace stripped
        
    Example:
        >>> markdown_to_blocks("# Heading\\n\\nParagraph text\\n\\n- List item")
        ["# Heading", "Paragraph text", "- List item"]
    """
    # Split on double newlines
    blocks = markdown.split("\n\n")
    
    # Strip whitespace and filter out empty blocks
    cleaned_blocks = []
    for block in blocks:
        stripped = block.strip()
        if stripped:  # Only include non-empty blocks
            cleaned_blocks.append(stripped)
    
    return cleaned_blocks


def block_to_block_type(block):
    """
    Determine the type of a markdown block.
    
    Args:
        block (str): A single block of markdown text (whitespace already stripped)
        
    Returns:
        BlockType: The type of the block
        
    Block type rules:
        - Headings: Start with 1-6 # characters, followed by a space
        - Code: Start with ``` and end with ```
        - Quote: Every line starts with >
        - Unordered list: Every line starts with "- "
        - Ordered list: Every line starts with number + ". ", incrementing from 1
        - Paragraph: Default if none of the above match
    """
    lines = block.split("\n")
    
    # Check for heading (1-6 # followed by space)
    if block.startswith("#"):
        count = 0
        for char in block:
            if char == "#":
                count += 1
            else:
                break
        if 1 <= count <= 6 and len(block) > count and block[count] == " ":
            return BlockType.HEADING
    
    # Check for code block (starts and ends with ```)
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    
    # Check for quote block (every line starts with >)
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    
    # Check for unordered list (every line starts with "- ")
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list (every line starts with number. incrementing from 1)
    is_ordered_list = True
    for i, line in enumerate(lines):
        expected_prefix = f"{i + 1}. "
        if not line.startswith(expected_prefix):
            is_ordered_list = False
            break
    if is_ordered_list and len(lines) > 0:
        return BlockType.ORDERED_LIST
    
    # Default to paragraph
    return BlockType.PARAGRAPH


def text_to_children(text):
    """
    Convert inline markdown text to a list of HTMLNode children.
    
    Uses text_to_textnodes to parse inline markdown (bold, italic, code, links, images)
    and then converts each TextNode to an HTMLNode.
    
    Args:
        text (str): Text with inline markdown formatting
        
    Returns:
        list of HTMLNode: Child nodes representing the inline content
    """
    from main import text_node_to_html_node
    
    # Convert text to TextNodes (handles inline markdown)
    text_nodes = text_to_textnodes(text)
    
    # Convert each TextNode to HTMLNode
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    
    return children


def paragraph_to_html_node(block):
    """
    Convert a paragraph block to an HTMLNode.
    
    Args:
        block (str): Paragraph text
        
    Returns:
        ParentNode: A <p> tag with inline content as children
    """
    # Join lines with spaces (paragraphs can have newlines within them)
    lines = block.split("\n")
    text = " ".join(lines)
    children = text_to_children(text)
    return ParentNode("p", children)


def heading_to_html_node(block):
    """
    Convert a heading block to an HTMLNode.
    
    Args:
        block (str): Heading text (starts with # characters)
        
    Returns:
        ParentNode: An <h1> through <h6> tag with inline content as children
    """
    # Count the # characters to determine heading level
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    
    # Extract text after the # characters and space
    text = block[level + 1:]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    """
    Convert a code block to an HTMLNode.
    
    Code blocks should NOT parse inline markdown.
    
    Args:
        block (str): Code block text (wrapped in ```)
        
    Returns:
        ParentNode: A <pre><code> structure with raw text
    """
    # Remove the ``` markers from start and end
    # The block format is: ```\ncode\ncode\n```
    # We need to extract just the code part
    
    if not block.startswith("```"):
        raise ValueError("Code block must start with ```")
    
    # Find the first newline after ```
    first_newline = block.index("\n")
    # Find the last ``` 
    last_backticks = block.rfind("```")
    
    # Extract code between first newline and last ```
    code_text = block[first_newline + 1:last_backticks]
    
    # Create code node without parsing inline markdown
    code_node = LeafNode("code", code_text)
    pre_node = ParentNode("pre", [code_node])
    return pre_node


def quote_to_html_node(block):
    """
    Convert a quote block to an HTMLNode.
    
    Args:
        block (str): Quote text (each line starts with >)
        
    Returns:
        ParentNode: A <blockquote> tag with inline content as children
    """
    # Remove the > from each line
    lines = block.split("\n")
    cleaned_lines = []
    for line in lines:
        # Remove the > and any space after it
        if line.startswith("> "):
            cleaned_lines.append(line[2:])
        elif line.startswith(">"):
            cleaned_lines.append(line[1:])
    
    # Join lines with newlines preserved
    text = "\n".join(cleaned_lines)
    children = text_to_children(text)
    return ParentNode("blockquote", children)


def unordered_list_to_html_node(block):
    """
    Convert an unordered list block to an HTMLNode.
    
    Args:
        block (str): Unordered list text (each line starts with -)
        
    Returns:
        ParentNode: A <ul> tag with <li> children
    """
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        # Remove the "- " prefix
        text = line[2:]
        children = text_to_children(text)
        li_node = ParentNode("li", children)
        list_items.append(li_node)
    
    return ParentNode("ul", list_items)


def ordered_list_to_html_node(block):
    """
    Convert an ordered list block to an HTMLNode.
    
    Args:
        block (str): Ordered list text (each line starts with number.)
        
    Returns:
        ParentNode: An <ol> tag with <li> children
    """
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        # Remove the "N. " prefix (where N is a number)
        # Find the first space after the number and period
        space_index = line.index(". ") + 2
        text = line[space_index:]
        children = text_to_children(text)
        li_node = ParentNode("li", children)
        list_items.append(li_node)
    
    return ParentNode("ol", list_items)


def block_to_html_node(block):
    """
    Convert a single markdown block to an HTMLNode.
    
    Args:
        block (str): A markdown block
        
    Returns:
        HTMLNode: The appropriate HTML node for the block type
    """
    block_type = block_to_block_type(block)
    
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    elif block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    elif block_type == BlockType.CODE:
        return code_to_html_node(block)
    elif block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    elif block_type == BlockType.UNORDERED_LIST:
        return unordered_list_to_html_node(block)
    elif block_type == BlockType.ORDERED_LIST:
        return ordered_list_to_html_node(block)
    else:
        raise ValueError(f"Unsupported block type: {block_type}")


def markdown_to_html_node(markdown):
    """
    Convert a full markdown document to a single parent HTMLNode.
    
    The markdown is split into blocks, each block is converted to the appropriate
    HTML node type, and all blocks are wrapped in a <div> container.
    
    Args:
        markdown (str): Full markdown document text
        
    Returns:
        ParentNode: A <div> containing all the block-level HTML nodes
    """
    # Split markdown into blocks
    blocks = markdown_to_blocks(markdown)
    
    # Convert each block to an HTML node
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    
    # Wrap all blocks in a div
    return ParentNode("div", children)
