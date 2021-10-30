import sys
from cefpython3 import cefpython as cef
from src.chrome.db_handler import create_user, user_exists, cache_user


class WelcomeLauncher:
    WINDOW_TITLE = "Welcome!"
    DEFAULT_RECT = [400, 0, 1400, 900]
    # UI_URL = "https://sujalsinghx86.github.io/school-project-web/index.html?#"
    UI_URL = "file:///home/picard/NIVZER/PROJECTS/SKYLON/skylon-web-ui/index.html?#"
    HANDLERS = []

    def __init__(self):
        sys.excepthook = cef.ExceptHook
        cef.Initialize()
        self.browser = self.create_browser()
        cef.MessageLoop()
        cef.Shutdown()

    def create_browser(self):
        window_config = self.configure_window()
        browser = cef.CreateBrowserSync(window_config, url=self.UI_URL)
        self.set_handlers(browser)
        self.expose_python_funcs(browser)
        return browser

    def configure_window(self):
        window_config = cef.WindowInfo()
        window_config.SetAsChild(0)  # parentWindowHandle = 0
        window_config.windowRect = self.DEFAULT_RECT
        window_config.windowName = self.WINDOW_TITLE
        return window_config

    def set_handlers(self, browser):
        for handler in self.HANDLERS:
            browser.SetClientHanlder(handler)

    def expose_python_funcs(self, browser):
        bindings = cef.JavascriptBindings()
        bindings.SetFunction("update_user_existence", self.update_user_existence)
        bindings.SetFunction("create_user", create_user)
        bindings.SetFunction("cache_user", cache_user)
        bindings.SetFunction("close_browser", self.close)
        browser.SetJavascriptBindings(bindings)

    def update_user_existence(self, first_name, last_name, email):
        user_existence = user_exists(first_name, last_name, email)
        self.browser.ExecuteFunction("UpdateExistence", user_existence)

    def close(self):
        cef.QuitMessageLoop()
        cef.Shutdown()
        del self.browser


if __name__ == "__main__":
    WelcomeLauncher()
