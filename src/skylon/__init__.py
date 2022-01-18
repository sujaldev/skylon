if __name__ == '__main__':
    from chrome import Chrome
    from render_engine.ui_backend import sdl, Window
else:
    from .chrome import Chrome
    from .render_engine.ui_backend import sdl, Window


class Skylon:
    def __init__(self, title, width, height, x=None, y=None):
        self.title = title

        self.window = Window(
            self.title,
            width, height,
            x, y,
            flags=sdl.SDL_WINDOW_SHOWN | sdl.SDL_WINDOW_RESIZABLE
        )

        self.chrome = Chrome(self.window)
        self.chrome.draw()

        self.handlers = {
            sdl.SDL_KEYDOWN: self.chrome.keydown_event_handler,
            sdl.SDL_KEYUP: self.chrome.keyup_event_handler,
            sdl.SDL_WINDOWEVENT: self.window_event_handler,
            sdl.SDL_MOUSEBUTTONDOWN: self.click_event_handler
        }
        self.window.handlers = self.handlers
        self.window.update()

    def start_event_loop(self):
        self.window.event_loop()

    def window_event_handler(self, event):
        if event.window.event == sdl.SDL_WINDOWEVENT_RESIZED:
            self.resize_event_handler(event)

    def resize_event_handler(self, event):
        self.chrome.get_active_tab().render_document()
        self.chrome.window_event_handler(event)
        self.window.update()

    def click_event_handler(self, event):
        btn = event.button.button
        x, y = event.button.x, event.button.y

        click_belongs_to_chrome = y <= self.chrome.CHROME_HEIGHT
        if click_belongs_to_chrome and btn == sdl.SDL_BUTTON_LEFT:
            self.chrome.left_click_event_handler(event)


if __name__ == "__main__":
    win = Skylon("Skylon", 1000, 800)
    win.start_event_loop()
