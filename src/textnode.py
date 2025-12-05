from enum import Enum

class TextType(Enum):
    TEXT = 0
    PLAIN = 1
    BOLD = 2
    ITALIC = 3
    UNDERLINED = 4
    STRIKETHROUGH = 5
    CODE = 6
    LINK = 7
    IMAGE = 8
    QUOTE = 9
    HEADING = 10
    LIST_ITEM = 11
    BLOCKQUOTE = 12
    HIGHLIGHTED = 13
    
    
class TextNode:
    def __init__(self, text: str, node_type: TextType, URL: str = None):
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