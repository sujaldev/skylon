if __name__ == "__main__":
    from layouts import DocumentLayout
else:
    from .layouts import DocumentLayout


class RenderTree:
    def __init__(self, document, window, viewport_width, viewport_height, x=0, y=0):
        self.document = document
        self.window = window

        self.x, self.y = x, y
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

        self.layout_tree = DocumentLayout(
            self.document,
            self.viewport_width,
            self.viewport_height,
            self.x, self.y
        )

        self.layout_tree.build_layout()

    def paint(self):
        with self.window.skia_surface as canvas:
            self.layout_tree.paint(canvas)
