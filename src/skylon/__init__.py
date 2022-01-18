from render_engine.ui_backend import sdl, Window
from render_engine.html_lib.parser import HTMLParser
from render_engine.render import RenderTree
from chrome import Chrome


class Skylon:
    DEBUG = True

    def __init__(self, source, width, height, x=None, y=None):
        parser = HTMLParser(source)
        parser.parse()
        self.document = parser.document
        self.title = self.find_title()

        self.window = Window(
            self.title,
            width, height,
            x, y,
            flags=sdl.SDL_WINDOW_SHOWN | sdl.SDL_WINDOW_RESIZABLE
        )

        self.chrome = Chrome(self.window)
        self.chrome.draw()

        self.render_tree = self.create_render_tree()
        self.render_tree.paint()

        self.handlers = {
            sdl.SDL_KEYDOWN: self.chrome.keydown_event_handler,
            sdl.SDL_WINDOWEVENT: self.window_event_handler,
            sdl.SDL_MOUSEBUTTONDOWN: self.click_event_handler
        }
        self.window.handlers = self.handlers
        self.log()
        self.window.update()

    def log(self):
        sep = "\n" + ("-" * 20) + "\n"
        if self.DEBUG:
            print(sep + "Document:")
            self.document.show_tree()
            print(sep + "Layout:")
            self.render_tree.layout_tree.show_tree()

    def create_render_tree(self):
        chrome_height = self.chrome.CHROME_HEIGHT
        tree = RenderTree(
            self.document, self.window,
            self.window.width, self.window.height - chrome_height,
            y=chrome_height
        )
        return tree

    def find_title(self):
        head = [child for child in self.document.children if child.tag.tag_name == "head"][0]
        for child in head.children:
            if child.tag.tag_name != "title":
                continue
            for node in child.children:
                if node.tag.type == "character":
                    return node.tag.data

    def start_event_loop(self):
        self.window.event_loop()

    def window_event_handler(self, event):
        if event.window.event == sdl.SDL_WINDOWEVENT_RESIZED:
            self.resize_event_handler(event)

    def resize_event_handler(self, event):
        self.render_tree = self.create_render_tree()
        self.render_tree.paint()
        self.chrome.window_event_handler(event)
        self.log()
        self.window.update()

    def click_event_handler(self, event):
        btn = event.button.button
        x, y = event.button.x, event.button.y

        click_belongs_to_chrome = y <= self.chrome.CHROME_HEIGHT
        if click_belongs_to_chrome and btn == sdl.SDL_BUTTON_LEFT:
            self.chrome.left_click_event_handler(event)


if __name__ == "__main__":
    html = """
<html>
    <head>
        <title>Skylon Hello World</title>
    </head>
    <body>
        <p><i><b>
            <p>Hello<p>test</p></p>
        </b></i></p>
        <i>
            <a>test</a>
        </i>
    </body>
</html>
"""
    win = Skylon(html, 1000, 800)
    win.start_event_loop()
