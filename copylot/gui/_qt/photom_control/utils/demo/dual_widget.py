import sys
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QThread
from PyQt5.QtGui import QPainter, QBrush, QColor, QPainterPath
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget
import numpy  as np

class SquareThread(QThread):
    squarePos = pyqtSignal(QPointF)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.index = 0
        vertices = [(0, 0), (200, 0), (300, 200), (100, 200)]
        num_coords_per_side = 20
        self.coords = generate_trapezoid_coordinates(vertices, num_coords_per_side)

    def run(self):
        while True:
            if self.parent.isRunning:
                self.index += 1
                if self.index >= len(self.coords):
                    self.index = 0
                self.squarePos.emit(QPointF(*self.coords[self.index]))
            self.msleep(50)

class MovingCircle(QWidget):
    circlePos = pyqtSignal(QPointF)
    squarePos = pyqtSignal(QPointF)

    def __init__(self):
        super().__init__()
        self.circleX = 10
        self.circleY = 10
        self.squareX = 0
        self.squareY = 0
        self.isRunning = True
        self.squareThread = SquareThread(self)
        self.squareThread.squarePos.connect(self.update_square_pos)
        self.squareThread.start()

    def mousePressEvent(self, event):
        self.circleX = event.x()
        self.circleY = event.y()
        self.circlePos.emit(QPointF(self.circleX, self.circleY))

    def mouseMoveEvent(self, event):
        self.circleX = event.x()
        self.circleY = event.y()
        self.circlePos.emit(QPointF(self.circleX, self.circleY))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw square
        painter.setBrush(QBrush(QColor(255, 0, 0, 127)))
        painter.drawRect(QRectF(self.squareX, self.squareY, 10, 10))

        # Draw circle
        painter.setBrush(QBrush(QColor(0, 255, 0, 127)))
        painter.drawEllipse(QRectF(self.circleX - 10, self.circleY - 10, 20, 20))

    def closeEvent(self, event):
        self.isRunning = False

    def update_square_pos(self, pos):
        self.squareX = pos.x()
        self.squareY = pos.y()
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 600)

        # Create button
        self.button = QPushButton('Open window', self)
        self.button.move(50, 50)
        self.button.clicked.connect(self.open_window)

    def open_window(self):
        # Create new window
        self.new_window = MovingCircle()
        self.new_window.circlePos.connect(self.update_circle)
        self.new_window.show()

    def update_circle(self, pos):
        self.statusBar().showMessage(f'Circle pos: ({pos.x()}, {pos.y()})')


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

def generate_trapezoid_coordinates(vertices, num_coords_per_side):
    # Generate the coordinates along each side of the trapezoid
    coordinates = []
    for i in range(len(vertices)):
        start = vertices[i]
        end = vertices[(i+1) % len(vertices)]
        x_diff = end[0] - start[0]
        y_diff = end[1] - start[1]
        for j in range(num_coords_per_side):
            x = start[0] + j * (x_diff / num_coords_per_side)
            y = start[1] + j * (y_diff / num_coords_per_side)
            coordinates.append([x, y])

    return coordinates


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
