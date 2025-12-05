from enum import Enum

class TextNodeType(Enum):
    PLAIN_TEXT = 1
    BOLD_TEXT = 2
    ITALIC_TEXT = 3
    UNDERLINED_TEXT = 4
    STRIKETHROUGH_TEXT = 5
    CODE_TEXT = 6
    LINK_TEXT = 7
    QUOTE_TEXT = 8
    HEADING_TEXT = 9
    LIST_ITEM_TEXT = 10
    BLOCKQUOTE_TEXT = 11
    HIGHLIGHTED_TEXT = 12
    
    
class TextNode:
    def __init__(self, text: str, node_type: TextNodeType, URL: str = None):
        self.text = text
        self.node_type = node_type
        self.URL = URL

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return NotImplemented
        return (self.text == other.text and
                self.node_type == other.node_type and
                self.URL == other.URL)

    def __repr__(self):
        return f"TextNode(type={self.node_type}, text={self.text}, URL={self.URL})"