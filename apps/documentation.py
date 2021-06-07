from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

# shamelessly ripped off from: http://zetcode.com/pyqt/qwebengineview/


class Documentation(QWidget):
    def __init__(self):
        super().__init__()
        self.webEngineView = QWebEngineView()
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout(self)
        self.load_page()
        vbox.addWidget(self.webEngineView)
        self.setLayout(vbox)
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('CIM Documentation')
        self.show()

    def load_page(self):
        with open('./docs/documentation.html', 'r') as f:
            html = f.read()
            self.webEngineView.setHtml(html, baseUrl=QUrl('file:///docs/'))
