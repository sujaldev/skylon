class Node:
    def __init__(self, tag, parent=None):
        self.tag = tag
        self.parent = parent
        self.children = []

    def show_tree(self, tab=0):
        representation = str(self)
        if representation:
            prompt = "\033[37m" + "├──" + "┼──" * tab + "┼\033[0m"
            print(prompt + representation)

        # RECURSE ON CHILDREN
        for child in self.children:
            child.show_tree(tab=tab + 1)

    def __repr__(self):
        return self.tag.__repr__()


class Document(Node):
    pass


class Element(Node):
    pass


class TextNode(Node):
    def __repr__(self):
        if not self.tag.data.isspace():
            return '"' + self.tag.data + '"'
        else:
            return ''
