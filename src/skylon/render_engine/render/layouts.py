from render_engine.helpers.CONSTANTS import HIDDEN_ELEMENTS, BLOCK_ELEMENTS
from render_engine.html_lib.structures.DOM import TextNode
import skia

from random import choice
from string import hexdigits


def random_color():
    seed = hexdigits.replace("abcdef", "")
    return int("".join(choice(seed) for i in range(6)) + "FF", 16)


DEFAULT_FONT_SIZE = 18
DEFAULT_TEXT_COLOR = skia.ColorBLACK

DEFAULT_FONT = skia.Font(None, size=DEFAULT_FONT_SIZE)
DEFAULT_FONT_METRICS = DEFAULT_FONT.getMetrics()


def calc_layout(node):
    tag_name = node.tag.tag_name
    if tag_name in HIDDEN_ELEMENTS:
        return
    elif isinstance(node, TextNode):
        return InlineLayout
    elif tag_name in BLOCK_ELEMENTS:
        return BlockLayout
    else:
        return InlineLayout


class Layout:
    def __init__(self, dom_node, parent=None, last_sibling=None, font_modifiers=()):
        self.dom_node = dom_node
        self.parent = parent
        self.last_sibling = last_sibling

        # To be calculated from self.dom_node.children
        self.children = []

        # Hidden by default
        self.x, self.y = 0, 0
        if self.parent is not None:
            self.x, self.y = self.parent.x, self.parent.y
        self.width, self.height = 0, 0

        self.font = DEFAULT_FONT
        self.font_metrics = DEFAULT_FONT_METRICS
        self.text_color = DEFAULT_TEXT_COLOR

        self.font_modifiers = font_modifiers
        self.change_font_based_on_modifiers()

    def change_font_based_on_modifiers(self):
        style = None
        if "a" in self.font_modifiers:
            self.text_color = skia.ColorBLUE

        if "i" in self.font_modifiers and "b" in self.font_modifiers:
            style = skia.FontStyle.BoldItalic()
        elif "i" in self.font_modifiers:
            style = skia.FontStyle.Italic()
        elif "b" in self.font_modifiers:
            style = skia.FontStyle.Bold()

        if style:
            typeface = skia.Typeface(None, style)
            self.font = skia.Font(typeface, size=DEFAULT_FONT_SIZE)
            self.font_metrics = self.font_metrics

    def __paint(self, canvas):
        right = self.x + self.width
        bottom = self.y + self.height
        rect = skia.Rect(self.x, self.y, right, bottom)
        paint = skia.Paint(Color=skia.ColorTRANSPARENT)
        canvas.drawRect(rect, paint)

        if isinstance(self.dom_node, TextNode):
            paint = skia.Paint(
                AntiAlias=True,
                Color=self.text_color,
            )
            text = self.dom_node.tag.data
            textBlob = skia.TextBlob(text, self.font)
            canvas.drawTextBlob(textBlob, self.x, self.y + self.height, paint)

    def paint(self, canvas):
        self.__paint(canvas)
        for child in self.children:
            child.paint(canvas)

    def show_tree(self, tab=0):
        representation = str(self)
        if representation:
            prompt = "\033[37m" + "├──" + "┼──" * tab + "┼\033[0m"
            print(prompt + representation)

        # RECURSE ON CHILDREN
        for child in self.children:
            child.show_tree(tab=tab + 1)

    def __repr__(self):
        layout_type = self.__class__.__name__
        node_desc = f"{layout_type}::{self.dom_node.tag}"
        geometric_desc = f"(x:{self.x}, y:{self.y}, w:{self.width}, h:{self.height})"
        font_desc = " " + (", ".join(self.font_modifiers)) if self.font_modifiers else ""
        return f"<{node_desc} {geometric_desc}{font_desc}>"


class DocumentLayout(Layout):
    def __init__(self, dom_node, viewport_width, viewport_height, x=0, y=0):
        super().__init__(dom_node)
        self.x, self.y = x, y
        self.width, self.height = viewport_width, viewport_height

    def find_body_node(self):
        for child in self.dom_node.children:
            if child.tag.tag_name == "body":
                return child

    def build_layout(self):
        body_dom_node = self.find_body_node()
        # We know body is a block layout, hence no check
        body_layout_node = BlockLayout(body_dom_node, parent=self, last_sibling=None,
                                       font_modifiers=self.font_modifiers)
        self.children.append(body_layout_node)
        body_layout_node.build_layout()


class BlockLayout(Layout):
    def __init__(self, dom_node, parent, last_sibling, font_modifiers):
        super().__init__(dom_node, parent, last_sibling, font_modifiers)

        # Block Layouts are greedy as they take up maximum possible space
        # from this we know it's width will be equal to the parent's and
        # if width is equal to the parent then obviously x is equal too.
        self.x = self.parent.x
        self.width = self.parent.width

        # y coordinate only depends on last_sibling or if this is none,
        # the parent. Both of which are known at initialization and
        # hence y can be calculated on initialization.
        if last_sibling is None:
            self.y = self.parent.y
        else:
            self.y = self.last_sibling.y + self.last_sibling.height

    def build_layout(self):
        last_sibling = None
        for child_dom_node in self.dom_node.children:
            layout_mode = calc_layout(child_dom_node)
            element_is_hidden = layout_mode is None
            if element_is_hidden:
                continue

            if isinstance(child_dom_node, TextNode):
                child_layout_node = InlineLayout.handle_text_elem(self, child_dom_node, last_sibling)
            else:
                child_layout_node = layout_mode(child_dom_node, self, last_sibling, self.font_modifiers)
                child_layout_node.build_layout()
                self.children.append(child_layout_node)
            last_sibling = child_layout_node

        self.height = sum([child.height for child in self.children])


class InlineLayout(Layout):

    def __init__(self, dom_node, parent, last_sibling, font_modifiers):
        super().__init__(dom_node, parent, last_sibling, font_modifiers)

        tag_name = self.dom_node.tag.tag_name
        if tag_name in ("i", "b", "a"):
            self.font_modifiers += tuple(tag_name)

        self.nearest_block_ancestor = None  # Setting to None initially, so it is calculated only when required.

        if self.last_sibling is None:
            self.x, self.y = self.parent.x, self.parent.y
        elif isinstance(self.last_sibling, BlockLayout):
            self.x = self.parent.x
            self.y = self.last_sibling.y + self.last_sibling.height
        else:
            self.x = self.last_sibling.x + self.last_sibling.width
            self.y = self.last_sibling.y

    def find_nearest_block_ancestor(self, layout_node=None):
        if layout_node is None:
            layout_node = self

        parent_is_block_level = isinstance(layout_node.parent, BlockLayout)
        if parent_is_block_level:
            return layout_node.parent
        elif isinstance(layout_node, DocumentLayout):
            return 0
        elif layout_node.parent is not None:
            return layout_node.find_nearest_block_ancestor(layout_node=self.parent)
        else:
            return 0

    def handle_block_inside_inline(self, dom_node, last_sibling):
        if self.nearest_block_ancestor is None:
            self.nearest_block_ancestor = self.find_nearest_block_ancestor()

        if self.nearest_block_ancestor != 0:
            layout_node = BlockLayout(dom_node, self.nearest_block_ancestor, last_sibling, self.font_modifiers)
            layout_node.build_layout()
            layout_node.parent = self
            self.children.append(layout_node)
            return layout_node

    def handle_text_elem(self, dom_node, last_sibling):
        layout_node = InlineLayout(dom_node, self, last_sibling, self.font_modifiers)
        node_text = dom_node.tag.data
        layout_node.width = layout_node.font.measureText(node_text)

        ascent, descent = layout_node.font_metrics.fAscent, layout_node.font_metrics.fDescent
        layout_node.height = descent - ascent

        self.children.append(layout_node)
        return layout_node

    def build_layout(self):
        last_sibling = None
        for child_dom_node in self.dom_node.children:
            layout_mode = calc_layout(child_dom_node)

            if layout_mode is BlockLayout:
                layout_node = self.handle_block_inside_inline(child_dom_node, last_sibling)
            elif isinstance(child_dom_node, TextNode):
                layout_node = self.handle_text_elem(child_dom_node, last_sibling)
            else:
                layout_node = InlineLayout(child_dom_node, self, last_sibling, self.font_modifiers)
                layout_node.build_layout()
                self.children.append(layout_node)

            if layout_node is not None:
                self.width = max(layout_node.width, self.width)
                self.height += layout_node.height
