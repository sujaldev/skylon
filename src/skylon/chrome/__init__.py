if __name__ == "__main__":
    from tab_ui import Tab, skia
else:
    from .tab_ui import Tab, skia


class Chrome:
    CHROME_HEIGHT = 85
    CHROME_BG_COLOR = 0XFFDEE1E6

    NAVBAR_HEIGHT = 45
    NAVBAR_COLOR = 0xFFFFFFFF

    URL_BAR_HEIGHT = 35
    URL_BAR_MARGIN = 150
    URL_BAR_RADIUS = 17
    URL_BAR_COLOR = 0XFFF1F3F4

    NAV_BUTTONS_MARGIN = 20

    def __init__(self, window):
        self.window = window

        self.tabs = []
        self.active_tab = None

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
        x1 = self.URL_BAR_MARGIN
        x2 = self.window.width - x1
        y1 = self.CHROME_HEIGHT - (self.NAVBAR_HEIGHT // 2) - (self.URL_BAR_HEIGHT // 2)
        base_rect = skia.Rect(
            x1, y1,
            x2, y1 + self.URL_BAR_HEIGHT
        )
        paint = skia.Paint(Color=self.URL_BAR_COLOR)
        radius = self.URL_BAR_RADIUS
        canvas.drawRoundRect(
            base_rect,
            radius, radius,
            paint
        )

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

    def add_tab(self, title="New Tab", active=True):
        if self.active_tab is not None:
            self.tabs[self.active_tab].active = False
        tab_index = len(self.tabs)
        tab = Tab(self.window, tab_index, title, active)
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
        if key == "t":
            self.add_tab()
        elif key == "w":
            self.remove_active_tab()
        elif key == "left" and self.active_tab - 1 >= 0:
            self.switch_tab(self.active_tab - 1)
        elif key == "right" and self.active_tab + 1 <= len(self.tabs) - 1:
            self.switch_tab(self.active_tab + 1)


if __name__ == '__main__':
    from render_engine.ui_backend import Window, sdl

    win = Window("Skylon Chrome", 1000, 800, flags=sdl.SDL_WINDOW_SHOWN | sdl.SDL_WINDOW_RESIZABLE)
    chrome = Chrome(win)
    chrome.add_tab("Hello World!")
    win.handlers[sdl.SDL_WINDOWEVENT] = chrome.window_event_handler
    win.handlers[sdl.SDL_KEYDOWN] = chrome.keydown_event_handler
    chrome.draw()
    win.event_loop()
