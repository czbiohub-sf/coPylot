import os
import sys
import numpy as np
import threading
import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import QThreadPool, QTimer
from PyQt5.QtWidgets import (
    QPushButton,
    QLabel,
    QWidget,
    QGridLayout,
    QGroupBox,
    QVBoxLayout,
    QLineEdit,
    QFileDialog,
    QGraphicsItem,
    QShortcut,
)
from PyQt5.QtCore import Qt, QTimer

from copylot.gui._qt.photom_control.helper_functions.qthreadworker import Worker
from copylot import logger

class demo_scan_points:

    def __init__(self, controlpanel):
        self.controlpanel = controlpanel
        # self.ch_list = controlpanel.channel_list
        self.num_chans = 2
        self.board_num = controlpanel.board_num
        self.input_range_list = [(0, controlpanel.window1.canvas_width), (0, controlpanel.window1.canvas_height)]
        # self.vout_range = controlpanel.galvo_x_range
        # self.ao_range = controlpanel.ao_range
        self.trans_obj = controlpanel.transform_list[controlpanel.current_laser]
        self.data_list = []
        self.threadpool = QThreadPool()
        self.isrunning = False
        self.apply_matrix = False
        self.laser_circle = demo_laser()


    def exec_scan(self):
        self.trans_obj = self.controlpanel.transform_list[self.controlpanel.current_laser]
        self.input_range_list = [
            (0, self.controlpanel.window1.canvas_width), (0, self.controlpanel.window1.canvas_height)
        ]
        while self.controlpanel.window1.iscalib:
            self.isrunning = True
            if self.apply_matrix:
                scan_path = self.trans_obj.affineTrans(self.data_list)
                print('Affine transformed.')
            else:
                scan_path = self.data_list
            for x, y in zip(scan_path[0], scan_path[1]):
                #TODO: write logic to move a point in a Window
                self.laser_circle.move_circle((x, y))
                time.sleep(1 / self.sampling_rate)
        self.isrunning = False

    def start_scan(self, data_list):
        self.data_list = data_list
        if self.isrunning:
            self.controlpanel.window1.iscalib = False
            self.threadpool.clear()
            while not self.threadpool.waitForDone():
                time.sleep(0.01)
        self.controlpanel.window1.iscalib = True
        worker = Worker(self.exec_scan)
        self.threadpool.start(worker)

    def stop_scan(self):
        self.controlpanel.window1.iscalib = False
        self.threadpool.clear()
        while not self.threadpool.waitForDone():
            time.sleep(0.01)

class demo_laser(QWidget):
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

        # Initialize the trail points
        self.trail_points = []

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)

        # Draw the trail lines
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(2)
        qp.setPen(pen)
        for i in range(len(self.trail_points) - 1):
            qp.drawLine(
                self.trail_points[i][0],
                self.trail_points[i][1],
                self.trail_points[i + 1][0],
                self.trail_points[i + 1][1],
            )

        # Draw the circle
        pen = QPen(Qt.NoPen)
        brush = QBrush(QColor(255, 0, 0))
        qp.setPen(pen)
        qp.setBrush(brush)
        qp.drawEllipse(int(self.x), int(self.y), 10, 10)

    def move_circle(self):
        if (
            self.x == self.points[self.current_point][0]
            and self.y == self.points[self.current_point][1]
        ):
            self.current_point = (self.current_point + 1) % len(self.points)
        target_x, target_y = self.points[self.current_point]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx**2 + dy**2) ** 0.5
        if dist <= self.step:
            self.x = target_x
            self.y = target_y
        else:
            self.x += self.step * dx / dist
            self.y += self.step * dy / dist

        # Add the current position to the trail points
        self.trail_points.append((int(self.x+5), int(self.y+5)))

        # Remove the oldest trail point if there are too many
        if len(self.trail_points) > 100:
            self.trail_points.pop(0)

        self.update()

@staticmethod
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

