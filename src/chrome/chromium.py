import sys

from cefpython3 import cefpython as cef

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import *

from src.chrome.navbar import NavigationBar


class ChromiumApplication(QApplication):
    def __init__(self):
        super().__init__([])
        self.timer = self.create_timer()

    def create_timer(self):
        timer = QTimer()
        timer.timeout.connect(self.on_timeout)
        timer.start(10)
        return timer

    # noinspection PyMethodMayBeStatic
    def on_timeout(self):
        cef.MessageLoopWork()


class ChromiumBrowserWindow(QMainWindow):
    DEFAULT_TITLE = "Chromium Browser"
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 600

    def __init__(self):
        super().__init__()
        self.chrome = None
        self.web_view = None
        self.setWindowTitle(self.DEFAULT_TITLE)
        self.init_window()
        self.show()

    def init_window(self):
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        self.web_view = WebViewWidget(parent=self)
        self.chrome = NavigationBar(parent=self, browser=self.web_view.browser)

        frame = QFrame()
        self.setCentralWidget(frame)
        layout = QVBoxLayout(frame)

        layout.addWidget(self.chrome, 0)
        layout.addWidget(self.web_view, 1)

        layout.setContentsMargins(0, 0, 0, 0)

    def closeEvent(self, event):
        if self.web_view.browser is not None:
            self.web_view.browser.CloseBrowser(True)  # force=True
            del self.web_view.browser  # required to close cleanly


class LoadHandler:
    def __init__(self, web_view_widget):
        self.web_view_widget = web_view_widget

    # noinspection PyPep8Naming
    def OnLoadStart(self, browser, *_, **__):
        navbar = self.web_view_widget.container.chrome
        navbar.url_bar.setText(browser.GetUrl())


class WebViewWidget(QWidget):
    DEFAULT_URL = "https://www.google.com"
    HANDLERS = [LoadHandler]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.container = parent
        self.browser = None
        self.browser_widget = None
        self_layout = QVBoxLayout(self)
        self_layout.setContentsMargins(0, 0, 0, 0)
        self.init_browser()

    def init_browser(self):
        browser_window = QWindow()
        window_config = cef.WindowInfo()
        rect_pos_and_size = [0, 0, self.width(), self.height()]
        window_config.SetAsChild(
            int(browser_window.winId()),
            rect_pos_and_size
        )
        self.browser = cef.CreateBrowserSync(window_config, url=self.DEFAULT_URL)
        self.browser_widget = QWidget.createWindowContainer(browser_window)
        self.layout().addWidget(self.browser_widget)
        self.set_handlers()

    def set_handlers(self):
        for handler in self.HANDLERS:
            self.browser.SetClientHandler(handler(self))

    def resizeEvent(self, event):
        if self.browser is not None:
            self.browser.SetBounds(0, 0, self.width(), self.height())


def launch_chromium():
    sys.excepthook = cef.ExceptHook
    cef.Initialize()
    app = ChromiumApplication()
    # noinspection PyUnusedLocal
    window = ChromiumBrowserWindow()
    app.exec()
    app.timer.stop()
    cef.Shutdown()


if __name__ == "__main__":
    launch_chromium()
