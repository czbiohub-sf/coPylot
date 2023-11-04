from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QPainter, QPainterPath
from PyQt5.QtWidgets import QWidget, QApplication
import sys

class MovingCircle(QWidget):
    def __init__(self, coords):
        super().__init__()
        self.coords = coords
        self.current_pos = 0
        self.timer = self.startTimer(100) # Timer to update the position every 100ms
        self.setGeometry(100, 100, 500, 500) # Set the size and position of the window
        self.show() # Show the window

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor(76, 0, 153), 1, Qt.SolidLine)) # Set the pen color to blue
        painter.setBrush(QColor(76, 0, 153)) # Set the brush color to blue
        painter.drawEllipse(QPointF(*self.coords[self.current_pos]), 10, 10) # Draw a circle at the current position

    def timerEvent(self, event):
        self.current_pos = (self.current_pos + 1) % len(self.coords) # Update the current position
        self.update() # Redraw the widget
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    coords = [(100, 100), (200, 200), (300, 100), (200, 50)]
    mc = MovingCircle(coords)
    sys.exit(app.exec_())

