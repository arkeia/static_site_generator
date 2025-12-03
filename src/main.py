from textnode import TextNode, TextType

def main():
    link = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(link)

if __name__ == "__main__":
    main()