import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer
import numpy as np

class Circle(QWidget):
    def __init__(self, points):
        super().__init__()
        self.setGeometry(0, 0, 400, 400)
        self.points = points
        self.current_point = 0
        self.step = 5
        self.x = points[self.current_point][0]
        self.y = points[self.current_point][1]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_circle)
        self.timer.start(10)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setBrush(QColor(255, 0, 0))
        qp.setPen(QPen(Qt.black, 1))
        qp.drawEllipse(int(self.x), int(self.y), 20, 20)

    def move_circle(self):
        if self.x == self.points[self.current_point][0] and self.y == self.points[self.current_point][1]:
            self.current_point = (self.current_point + 1) % len(self.points)
        target_x, target_y = self.points[self.current_point]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist <= self.step:
            self.x = target_x
            self.y = target_y
        else:
            self.x += self.step * dx / dist
            self.y += self.step * dy / dist
        self.update()

def generate_square():
    # Define the coordinates of the four corners of the square
    x0, y0 = 0, 0  # bottom-left corner
    x1, y1 = 0, 100  # top-left corner
    x2, y2 = 100, 100  # top-right corner
    x3, y3 = 100, 0  # bottom-right corner
    # Define the number of points to interpolate along each edge
    num_points = 20

    # Interpolate points along each edge of the square
    x01 = np.linspace(x0, x1, num_points, endpoint=True)
    y01 = np.linspace(y0, y1, num_points, endpoint=True)
    x12 = np.linspace(x1, x2, num_points, endpoint=True)
    y12 = np.linspace(y1, y2, num_points, endpoint=True)
    x23 = np.linspace(x2, x3, num_points, endpoint=True)
    y23 = np.linspace(y2, y3, num_points, endpoint=True)
    x30 = np.linspace(x3, x0, num_points, endpoint=True)
    y30 = np.linspace(y3, y0, num_points, endpoint=True)

    # Combine the interpolated points into a single array of (x, y) coordinates
    x_coords = np.concatenate((x01, x12, x23, x30))
    y_coords = np.concatenate((y01, y12, y23, y30))
    coords = np.stack((x_coords, y_coords), axis=1)
    return coords 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    points = generate_square()
    circle = Circle(points)
    circle.show()
    sys.exit(app.exec_())

