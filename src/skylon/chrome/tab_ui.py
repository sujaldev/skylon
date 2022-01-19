import skia
import requests
from urllib.parse import urlparse
from render_engine.render import RenderTree
from render_engine.html_lib.parser import HTMLParser


class TabUI:
    DEBUG = True

    BASE_HEIGHT = 40
    BASE_WIDTH = 250
    MARGIN_LEFT = 20
    RADIUS = 10
    BASE_COLOR = 0xFFFFFFFF
    INACTIVE_BASE_COLOR = 0XFF8B8E92
    INACTIVE_LINE_MARGIN = 7

    ARC_RADIUS = 10

    DEFAULT_FONT = skia.Font(None, 18)
    FONT_MARGIN_TOP = 25
    FONT_MARGIN_LEFT = 15

    CLOSE_BTN_SIZE = 20
    CLOSE_BTN_MARGIN = 15

    def __init__(self, window, tab_index, chrome_height, title="New Tab", active=False):
        self.window = window
        self.tab_index = tab_index
        self.chrome_height = chrome_height
        self.title = title
        self.active = active

        self.x1, self.x2, self.y1, self.y2 = 0, 0, 0, 0
        self.set_position()

        self.url = None
        self.document = None
        self.render_tree = None
        self.url_bar_has_focus = False
        self.url_bar_text = ""

    def fetch_document(self):
        content = None
        self.url = self.url.replace(";//", "://")

        # FILE URL
        if self.url.startswith("file://"):
            try:
                with open(urlparse(self.url).path) as source:
                    content = source.read()
            except IsADirectoryError:
                print("Invalid File URL")

        # NET URL
        try:
            if content is None:
                request = requests.get(self.url)
                content = request.content.decode()
                if not request.ok:
                    return
        except Exception as e:
            print(e)
            return

        if content is None:
            return
        parser = HTMLParser(content)
        parser.parse()
        self.document = parser.document
        self.title = self.find_title()

    def find_title(self):
        head = [child for child in self.document.children if child.tag.tag_name == "head"][0]
        for child in head.children:
            if child.tag.tag_name != "title":
                continue
            for node in child.children:
                if node.tag.type == "character":
                    return node.tag.data

    def render_document(self):
        if self.document:
            self.render_tree = self.create_render_tree()
            self.render_tree.paint()
            self.log()

    def log(self):
        if self.DEBUG:
            sep = "\n" + "-" * 20 + "\n"
            print(sep + "Document:")
            self.document.show_tree()
            print(sep + "Layout:")
            self.render_tree.layout_tree.show_tree()

    def __clear_document_canvas(self):
        canvas = self.window.skia_surface.getCanvas()
        x1, y1 = 0, self.chrome_height
        x2, y2 = self.window.width, self.window.height
        clear_rect = skia.Rect(x1, y1, x2, y2)
        canvas.drawRect(clear_rect, skia.Paint(Color=skia.ColorWHITE))

    def create_render_tree(self):
        chrome_height = self.chrome_height
        tree = RenderTree(
            self.document, self.window,
            self.window.width, self.window.height - chrome_height,
            y=chrome_height
        )
        return tree

    def set_position(self):
        self.x1, self.y1 = self.MARGIN_LEFT + (self.BASE_WIDTH * self.tab_index), 0
        self.x2, self.y2 = self.x1 + self.BASE_WIDTH, self.BASE_HEIGHT

    def draw(self):
        self.__clear_document_canvas()
        self.set_position()
        with self.window.skia_surface as canvas:
            if self.active:
                self.render_document()
                self.__draw_active_tab(canvas)
            else:
                self.__draw_inactive_tab(canvas)
            self.__draw_commons(canvas)

    def __draw_rounded_base_rect(self, canvas):
        base_rect = skia.Rect(
            self.x1, self.y1,
            self.x2, self.y2
        )
        canvas.drawRoundRect(
            base_rect,
            self.RADIUS, self.RADIUS,
            skia.Paint(self.BASE_COLOR)
        )

    def __make_left_arc_path(self):
        x, y, radius = self.x1, self.y2, self.ARC_RADIUS
        path = skia.Path()
        arc_diameter = radius * 2
        # noinspection PyTypeChecker
        path.addArc(skia.Rect(x - arc_diameter, y - arc_diameter, x, y), 0, 90)
        path.lineTo(x + arc_diameter, y)
        return path

    def __make_right_arc_path(self, canvas):
        x, y, radius = self.x2, self.y2, self.ARC_RADIUS
        path = skia.Path()
        arc_diameter = radius * 2
        # noinspection PyTypeChecker
        path.addArc(skia.Rect(x, y - arc_diameter, x + arc_diameter, y), 90, 90)
        path.lineTo(x - arc_diameter, y)
        return path

    def __draw_arc_on_bottom_borders(self, canvas):
        left_path = self.__make_left_arc_path()
        right_path = self.__make_right_arc_path(canvas)
        paint = skia.Paint(
            Color=self.BASE_COLOR,
            Style=skia.Paint.kFill_Style
        )
        canvas.drawPath(left_path, paint)
        canvas.drawPath(right_path, paint)

    def __draw_active_tab(self, canvas):
        self.__draw_rounded_base_rect(canvas)
        self.__draw_arc_on_bottom_borders(canvas)

    def __draw_inactive_tab(self, canvas):
        path = skia.Path()
        margin = self.INACTIVE_LINE_MARGIN
        path.moveTo(self.x2 + 2, self.y1 + margin)
        path.lineTo(self.x2 + 2, self.y2 - margin)
        canvas.drawPath(
            path, skia.Paint(
                Color=self.INACTIVE_BASE_COLOR,
                StrokeWidth=1, Style=skia.Paint.kStroke_Style
            )
        )

    def __draw_commons(self, canvas):
        self.__draw_title(canvas)
        self.__draw_close_btn(canvas)

    def __draw_title(self, canvas):
        typeface = skia.FontMgr().matchFamilyStyle("Montserrat", skia.FontStyle.Normal())
        text = skia.TextBlob(self.title, skia.Font(typeface, 12))
        paint = skia.Paint(Color=skia.ColorBLACK)
        x = self.x1 + self.FONT_MARGIN_LEFT
        y = self.y1 + self.FONT_MARGIN_TOP
        canvas.drawTextBlob(text, x, y, paint)

    def __draw_close_btn(self, canvas):
        x1 = self.x2 - self.CLOSE_BTN_SIZE - self.CLOSE_BTN_MARGIN
        y1 = (self.BASE_HEIGHT // 2) - (self.CLOSE_BTN_SIZE // 2)
        canvas.drawImageRect(
            skia.Image.open("./assets/close.png"),
            skia.Rect(x1, y1, x1 + self.CLOSE_BTN_SIZE, y1 + self.CLOSE_BTN_SIZE)
        )
