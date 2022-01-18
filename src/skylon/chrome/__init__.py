if __name__ == "__main__":
    from tab_ui import TabUI, skia
else:
    import sdl2 as sdl
    from .tab_ui import TabUI, skia


class Chrome:
    CHROME_HEIGHT = 85
    CHROME_BG_COLOR = 0XFFDEE1E6

    NAVBAR_HEIGHT = 45
    NAVBAR_COLOR = 0xFFFFFFFF

    URL_BAR_HEIGHT = 35
    URL_BAR_MARGIN = 150
    URL_BAR_TEXT_MARGIN = 20
    URL_BAR_RADIUS = 17
    URL_BAR_COLOR = 0XFFF1F3F4
    STROKE_WIDTH = 2
    STROKE_COLOR = 0XFF4285F4

    NAV_BUTTONS_MARGIN = 20

    def __init__(self, window):
        self.window = window
        self.ctrl_clicked = False

        self.tabs = []
        self.active_tab = None
        self.add_tab_shortcut_handler()

    def get_active_tab(self):
        return self.tabs[self.active_tab]

    def __draw_chrome_bg(self, canvas):
        bg_rect = skia.Rect(0, 0, self.window.width, self.CHROME_HEIGHT)
        bg_paint = skia.Paint(Color=self.CHROME_BG_COLOR)
        canvas.drawRect(bg_rect, bg_paint)

    def __draw_navbar_bg(self, canvas):
        bg_rect = skia.Rect(
            0, self.CHROME_HEIGHT - self.NAVBAR_HEIGHT,
            self.window.width, self.CHROME_HEIGHT - 1
        )
        bg_paint = skia.Paint(self.NAVBAR_COLOR)
        canvas.drawRect(bg_rect, bg_paint)

    def __draw_url_bar(self, canvas):
        x1, y1 = self.URL_BAR_MARGIN, self.CHROME_HEIGHT - (self.NAVBAR_HEIGHT // 2) - (self.URL_BAR_HEIGHT // 2)
        x2, y2 = self.window.width - x1, y1 + self.URL_BAR_HEIGHT

        base_paint = skia.Paint(Color=self.URL_BAR_COLOR)
        base_rect = skia.Rect(x1, y1, x2, y2)
        radius = self.URL_BAR_RADIUS
        canvas.drawRoundRect(base_rect, radius, radius, base_paint)

        self.__draw_url_bar_text(canvas)

        if not self.get_active_tab().url_bar_has_focus:
            return
        border_paint = skia.Paint(
            AntiAlias=True, Color=self.STROKE_COLOR, Style=skia.Paint.kStroke_Style, StrokeWidth=self.STROKE_WIDTH
        )
        x1, y1 = x1 + self.STROKE_WIDTH, y1 + self.STROKE_WIDTH
        x2, y2 = x2 - self.STROKE_WIDTH, y2 - self.STROKE_WIDTH
        border_rect = skia.Rect(x1, y1, x2, y2)
        canvas.drawRoundRect(border_rect, radius, radius, border_paint)

    def __draw_url_bar_text(self, canvas):
        self.__clear_url_bar_text(canvas)
        typeface = skia.FontMgr().matchFamilyStyle("Montserrat", skia.FontStyle.Normal())
        font = skia.Font(typeface, 13)

        text_limit = self.window.width - (2 * self.URL_BAR_MARGIN) - (2 * self.URL_BAR_TEXT_MARGIN)
        active_tab = self.get_active_tab()
        no_need_for_drawing = (not active_tab.url_bar_text) or (font.measureText(active_tab.url_bar_text) > text_limit)
        if no_need_for_drawing:
            return

        x = self.URL_BAR_MARGIN + self.URL_BAR_TEXT_MARGIN
        y = self.CHROME_HEIGHT - (self.NAVBAR_HEIGHT // 2) - (self.URL_BAR_HEIGHT // 2) + self.URL_BAR_TEXT_MARGIN
        textBlob = skia.TextBlob(active_tab.url_bar_text, font)
        paint = skia.Paint(Color=skia.ColorBLACK)
        canvas.drawTextBlob(textBlob, x, y, paint)

    def __clear_url_bar_text(self, canvas):
        x1 = self.URL_BAR_MARGIN + self.URL_BAR_TEXT_MARGIN
        y1 = self.CHROME_HEIGHT - (self.NAVBAR_HEIGHT // 2) - (self.URL_BAR_HEIGHT // 2) + self.STROKE_WIDTH * 2
        x2 = self.window.width - x1
        y2 = y1 + self.URL_BAR_HEIGHT - self.STROKE_WIDTH * 4
        clear_rect = skia.Rect(x1, y1, x2, y2)
        paint = skia.Paint(Color=self.URL_BAR_COLOR)
        canvas.drawRect(clear_rect, paint)

    # noinspection PyArgumentList
    def __draw_navbar_buttons(self, canvas):
        width, height = 24, 24
        x1 = self.NAV_BUTTONS_MARGIN
        y1 = self.CHROME_HEIGHT - (self.NAVBAR_HEIGHT // 2) - (height // 2)
        canvas.drawImageRect(
            skia.Image.open("./assets/back-arrow-inactive.png"),
            skia.Rect(x1, y1, x1 + width, y1 + width)
        )

        x1 = x1 + width + self.NAV_BUTTONS_MARGIN
        canvas.drawImageRect(
            skia.Image.open("./assets/forward-arrow-inactive.png"),
            skia.Rect(x1, y1, x1 + width, y1 + width)
        )

        x1 = x1 + width + self.NAV_BUTTONS_MARGIN
        canvas.drawImageRect(
            skia.Image.open("./assets/refresh.png"),
            skia.Rect(x1, y1, x1 + width, y1 + width)
        )

    def draw(self):
        with self.window.skia_surface as canvas:
            self.__draw_chrome_bg(canvas)
            self.__draw_navbar_bg(canvas)
            self.__draw_url_bar(canvas)
            self.__draw_navbar_buttons(canvas)
            for tab in self.tabs:
                if tab.active:
                    continue
                tab.draw()
            if self.active_tab is not None:
                self.tabs[self.active_tab].draw()
        self.window.update()

    def add_tab_shortcut_handler(self):
        if self.active_tab is not None:
            self.tabs[self.active_tab].active = False
        tab_index = len(self.tabs)
        tab = TabUI(self.window, tab_index, self.CHROME_HEIGHT, active=True)
        self.tabs.append(tab)
        self.active_tab = tab_index
        self.draw()

    def remove_active_tab(self):
        if self.active_tab is not None:
            del self.tabs[self.active_tab]
            for tab in self.tabs:
                if tab.tab_index >= self.active_tab:
                    tab.tab_index -= 1

            num_active_tabs = len(self.tabs)
            if self.active_tab >= num_active_tabs:
                self.active_tab = num_active_tabs - 1
            self.tabs[self.active_tab].active = True
            self.draw()

    def switch_tab(self, tab_index):
        try:
            self.tabs[self.active_tab].active = False
            self.active_tab = tab_index
            self.tabs[self.active_tab].active = True
            self.draw()
        except IndexError:
            print("No Such tab exists.")

    def window_event_handler(self, event):
        if event.window.event == sdl.SDL_WINDOWEVENT_RESIZED:
            self.draw()

    def keydown_event_handler(self, event):
        scancode = event.key.keysym.scancode
        keycode = sdl.SDL_GetKeyFromScancode(scancode)
        key = sdl.SDL_GetKeyName(keycode).decode().lower()
        active_tab = self.get_active_tab()
        if "ctrl" in key:
            self.ctrl_clicked = True
        elif self.ctrl_clicked and key == "t":
            self.add_tab_shortcut_handler()
        elif self.ctrl_clicked and key == "w":
            self.remove_active_tab()
        elif self.ctrl_clicked and key == "left" and self.active_tab - 1 >= 0:
            self.switch_tab(self.active_tab - 1)
        elif self.ctrl_clicked and key == "right" and self.active_tab + 1 <= len(self.tabs) - 1:
            self.switch_tab(self.active_tab + 1)
        elif active_tab.url_bar_has_focus:
            if key == "backspace":
                active_tab.url_bar_text = active_tab.url_bar_text[:-1]
            elif key == "space":
                active_tab.url_bar_text += " "
            elif key == "tab":
                active_tab.url_bar_text += "\t"
            elif "return" in key and active_tab.url_bar_has_focus:
                active_tab.url = active_tab.url_bar_text
                active_tab.fetch_document()
                active_tab.render_document()
            elif len(key) == 1:
                active_tab.url_bar_text += key
            self.__draw_url_bar_text(self.window.skia_surface.getCanvas())
            self.window.update()

    def keyup_event_handler(self, event):
        scancode = event.key.keysym.scancode
        keycode = sdl.SDL_GetKeyFromScancode(scancode)
        key = sdl.SDL_GetKeyName(keycode).decode().lower()
        if "ctrl" in key:
            self.ctrl_clicked = False

    def left_click_event_handler(self, event):
        x, y = event.button.x, event.button.y
        click_in_navbar = y >= self.NAVBAR_HEIGHT
        click_in_url_bar = self.URL_BAR_MARGIN <= x <= self.window.width - self.URL_BAR_MARGIN
        canvas = self.window.skia_surface.getCanvas()
        active_tab = self.get_active_tab()
        if click_in_navbar and click_in_url_bar:
            active_tab.url_bar_has_focus = True
        elif active_tab.url_bar_has_focus:
            active_tab.url_bar_has_focus = False
        self.__draw_url_bar(canvas)
        self.window.update()
