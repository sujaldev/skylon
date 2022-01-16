import skia


class Tab:
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

    def __init__(self, window, tab_index, title="New Tab", active=False):
        self.window = window
        self.tab_index = tab_index
        self.title = title
        self.active = active

        self.x1, self.x2, self.y1, self.y2 = 0, 0, 0, 0
        self.set_position()

    def set_position(self):
        self.x1, self.y1 = self.MARGIN_LEFT + (self.BASE_WIDTH * self.tab_index), 0
        self.x2, self.y2 = self.x1 + self.BASE_WIDTH, self.BASE_HEIGHT

    def draw(self):
        self.set_position()
        with self.window.skia_surface as canvas:
            if self.active:
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
