import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt


class CtrlWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.positions = [(100, 100), (200, 200), (300, 100), (400, 200)]

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setPen(QPen(QColor(0, 0, 0), 2))
        qp.setBrush(QBrush(QColor(255, 0, 0)))
        for pos in self.positions:
            qp.drawEllipse(pos[0], pos[1], 50, 50)


class CustomWindow(QWidget):
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setPen(QPen(QColor(0, 0, 0), 2))
        qp.setBrush(QBrush(QColor(0, 255, 0)))
        qp.drawEllipse(100, 100, 100, 100)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ctrl_window = CtrlWindow()
        self.custom_window = CustomWindow()

        layout = QHBoxLayout()
        layout.addWidget(self.ctrl_window)
        layout.addWidget(self.custom_window)

        self.setLayout(layout)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
