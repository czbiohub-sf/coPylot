import sys
import qdarkstyle
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QApplication
from widgets.gui.qt_main_widget import MainWidget


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = "Pisces Parameter Controller"
        self.left = 10
        self.top = 10
        self.width = 500
        self.height = 500

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.setCentralWidget(MainWidget(self))

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec())
