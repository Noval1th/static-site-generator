# hello world
from textnode import TextNode, TextType
from htmlnode import LeafNode, ParentNode, HTMLNode
import os
import shutil


def text_node_to_html_node(text_node):
    """
    Convert a TextNode to an HTMLNode (LeafNode).
    
    Handles each TextType:
    - TEXT: LeafNode with no tag
    - BOLD: LeafNode with 'b' tag
    - ITALIC: LeafNode with 'i' tag
    - CODE: LeafNode with 'code' tag
    - LINK: LeafNode with 'a' tag and href prop
    - IMAGE: LeafNode with 'img' tag, empty value, src and alt props
    
    Raises ValueError for unsupported types.
    """
    if text_node.node_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.node_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.node_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.node_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.node_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.URL})
    elif text_node.node_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.URL, "alt": text_node.text})
    else:
        raise ValueError(f"Unsupported TextType: {text_node.node_type}")


def copy_directory_contents(src_dir, dest_dir):
    """
    Recursively copy all contents from source directory to destination directory.
    
    First deletes all contents of the destination directory to ensure a clean copy.
    Then copies all files and subdirectories recursively.
    
    Args:
        src_dir (str): Path to the source directory
        dest_dir (str): Path to the destination directory
    """
    # Delete all contents of destination directory if it exists
    if os.path.exists(dest_dir):
        print(f"Clearing destination directory: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    # Create the destination directory
    os.makedirs(dest_dir)
    print(f"Created destination directory: {dest_dir}")
    
    # Recursively copy contents
    _copy_recursive(src_dir, dest_dir)


def _copy_recursive(src, dest):
    """
    Helper function to recursively copy directory contents.
    
    Args:
        src (str): Source directory path
        dest (str): Destination directory path
    """
    # List all items in the source directory
    items = os.listdir(src)
    
    for item in items:
        src_path = os.path.join(src, item)
        dest_path = os.path.join(dest, item)
        
        if os.path.isfile(src_path):
            # Copy file
            shutil.copy2(src_path, dest_path)
            print(f"Copied file: {src_path} -> {dest_path}")
        elif os.path.isdir(src_path):
            # Create destination directory and recurse
            os.makedirs(dest_path)
            print(f"Created directory: {dest_path}")
            _copy_recursive(src_path, dest_path)


print("hello world")

def main():
    # Example: Copy static directory to public
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(project_root, "static")
    public_dir = os.path.join(project_root, "public")
    
    if os.path.exists(static_dir):
        print("Copying static files to public directory...")
        copy_directory_contents(static_dir, public_dir)
        print("Copy complete!")
    else:
        print(f"Static directory not found: {static_dir}")
    
    
if __name__ == "__main__":
    main()