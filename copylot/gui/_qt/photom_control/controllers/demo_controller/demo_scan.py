import os
import sys
import numpy as np
import time

from PyQt5.QtGui import QKeySequence, QPainter, QColor, QPen, QBrush
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
    QApplication,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QPointF
from copylot.gui._qt.photom_control.scan_algrthm.scan_algorithm import ScanAlgorithm
from copylot.gui._qt.photom_control.helper_functions.qthreadworker import Worker
from copylot import logger


class DemoScanPoints:
    laser_demo_pos = pyqtSignal(QPointF)

    def __init__(self, controlpanel, sampling_rate=100):
        self.controlpanel = controlpanel
        self.window = self.controlpanel.window1
        # self.ch_list = controlpanel.channel_list
        # self.num_chans = None
        self.input_range_list = [
            (0, self.controlpanel.window1.canvas_width),
            (0, self.controlpanel.window1.canvas_height),
        ]
        # self.vout_range = controlpanel.galvo_x_range
        # self.ao_range = controlpanel.ao_range
        self.trans_obj = self.controlpanel.transform_list[
            self.controlpanel.current_laser
        ]
        self.data_list = []
        self.isrunning = False
        self.apply_matrix = False
        
        ## EH: testing pseudo laser.
        self.laser_demo_X = 0
        self.laser_demo_Y = 0
        self.demo_laser = LaserDemo(self)
        logger.info(f'rectangle window {self.size_par}')
        # self.scan_path = self.scan_obj.generate_rect()
        
    def start_scan(self, data_list):
        logger.info('Start Demo Scan')
        self.window.draw_demo_calib(self.scan_path)
        logger.info('Showing laser calib path')
        self.data_list = data_list
        if self.isrunning:
            self.controlpanel.window1.iscalib = False
            self.demo_laser.laser_demo_pos.connect(self.update_demo_pos)
            self.demo_laser.start()
        self.controlpanel.window1.iscalib = True

    def update_demo_pos(self, pos):
        self.laser_demo_X = pos.x()
        self.laser_demo_Y = pos.y()
        self.update()

    def stop_scan(self):
        self.controlpanel.window1.iscalib = False
        self.laser_demo_thread.stop()
        # Cleanup the calib trace
        self.window.clear_preview(region='all')
        logger.info('Scanning for calib has stopped.')


class LaserDemo(QThread):
    laser_demo_pos = pyqtSignal(QPointF)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.index = 0
        self.vertices = [(0, 0), (200, 0), (300, 200), (100, 200)]
        self.num_coords_per_side = 20
        self.coords = self.generate_trapezoid_coordinates(
            self.vertices, self.num_coords_per_side
        )
        
    def run(self):
        while True:
            if self.parent.isrunning:
                self.index += 1
                if self.index >= len(self.coords):
                    self.index = 0
                self.laser_demo_pos.emit(QPointF(*self.coords[self.index]))
            self.msleep(50)
            if self.parent.apply_matrix:
                logger.info('applying matrix transform')
                # self.coords = self.parent.trans_obj.affineTrans(self.)
                print('Affine transformed.')

    @staticmethod
    def generate_trapezoid_coordinates(vertices, num_coords_per_side):
        # Generate the coordinates along each side of the trapezoid
        coordinates = []
        for i in range(len(vertices)):
            start = vertices[i]
            end = vertices[(i + 1) % len(vertices)]
            x_diff = end[0] - start[0]
            y_diff = end[1] - start[1]
            for j in range(num_coords_per_side):
                x = start[0] + j * (x_diff / num_coords_per_side)
                y = start[1] + j * (y_diff / num_coords_per_side)
                coordinates.append([x, y])

        return coordinates
