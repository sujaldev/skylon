from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
)


class NavigationBar(QFrame):
    def __init__(self, parent=None, browser=None):
        super().__init__()
        self.parent = parent
        self.browser = browser

        self.back_btn = self.create_button("Back")
        self.back_btn.clicked.connect(self.on_back)

        self.forward_btn = self.create_button("Forward")
        self.forward_btn.clicked.connect(self.on_forward)

        self.refresh_btn = self.create_button("Refresh")
        self.refresh_btn.clicked.connect(self.on_refresh)

        self.url_bar = self.create_url_bar()
        self.url_bar.returnPressed.connect(self.on_search)

        self.frame_layout = QHBoxLayout()
        self.init_layout()

    def create_button(self, name):
        button_icon_path = f"./assets/{name}.svg"
        button = QPushButton()
        button.setStyleSheet(f"""
        QPushButton {{
            background-image: url("{button_icon_path}");
            background-repeat: no-repeat;
            background-position: center;
            background-color: rgba(0, 0, 0, 0.1);
            border: 10px;
            border-radius: 8px;
            padding: 10px;
        }}
        QPushButton:hover {{
            background-color: rgba(0, 0, 0, 0.5);
        }}
        
        QPushButton:pressed {{
            background-color: none;
        }}
        """)
        return button

    def create_url_bar(self):
        search = QLineEdit()
        search.setStyleSheet("""QLineEdit {
           min-width: 300px;
           padding: 10px;
           margin-left: 50px;
           margin-right: 30px;

           border-width: 10px;
           border-radius: 8px;

           background-color: rgba(0, 0, 0, 0.2);
           color: white;
       }

       QLineEdit:hover {
           background-color: #454549;
       }
       """)
        return search

    def init_layout(self):
        self.setStyleSheet("""
        background: #2A292E;
        min-height: 20px;
        """)
        self.frame_layout.addWidget(self.back_btn, 0)
        self.frame_layout.addWidget(self.forward_btn, 0)
        self.frame_layout.addWidget(self.refresh_btn, 0)
        self.frame_layout.addWidget(self.url_bar, 1)
        self.setLayout(self.frame_layout)

    def on_back(self):
        if self.browser is not None:
            self.browser.GoBack()

    def on_forward(self):
        if self.browser is not None:
            self.browser.GoForward()

    def on_refresh(self):
        if self.browser is not None:
            self.browser.Reload()

    def on_search(self):
        if self.browser is not None:
            url = self.url_bar.text()
            self.browser.LoadUrl(url)


if __name__ == "__main__":
    app = QApplication([])
    nav = NavigationBar()
    nav.show()
    app.exec()
