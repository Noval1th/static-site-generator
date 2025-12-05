# hello world
from textnode import TextNode


print("hello world")

def main():
    printNode = TextNode("This is some anchor text", "link", "https://www.boot.dev")
    print(printNode)
    
    
if __name__ == "__main__":
    main()