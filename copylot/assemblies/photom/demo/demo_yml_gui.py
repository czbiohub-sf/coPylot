import sys
import yaml
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QSlider,
    QVBoxLayout,
    QGraphicsView,
    QGroupBox,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsItem,
)
from PyQt5.QtGui import QColor, QPen


class Laser:
    def __init__(self, name, power=0):
        self.name = name
        self.power = power
        self.laser_on = False

    def toggle(self):
        self.laser_on = not self.laser_on

    def set_power(self, power):
        self.power = power


class Mirror:
    def __init__(self, initial_x=0, initial_y=0):
        self.x = initial_x
        self.y = initial_y


class LaserWidget(QWidget):
    def __init__(self, laser):
        super().__init__()
        self.laser = laser
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        laser_label = QLabel(self.laser.name)
        layout.addWidget(laser_label)

        laser_power_slider = QSlider(Qt.Horizontal)
        laser_power_slider.setMinimum(0)
        laser_power_slider.setMaximum(100)
        laser_power_slider.setValue(self.laser.power)
        laser_power_slider.valueChanged.connect(self.update_power)
        layout.addWidget(laser_power_slider)

        laser_toggle_button = QPushButton('Toggle')
        laser_toggle_button.clicked.connect(self.toggle_laser)
        layout.addWidget(laser_toggle_button)

        self.setLayout(layout)

    def toggle_laser(self):
        self.laser.toggle()

    def update_power(self, value):
        self.laser.set_power(value)


class MirrorWidget(QWidget):
    def __init__(self, mirror):
        super().__init__()
        self.mirror = mirror
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        mirror_x_label = QLabel('Mirror X Position')
        layout.addWidget(mirror_x_label)

        self.mirror_x_slider = QSlider(Qt.Horizontal)
        self.mirror_x_slider.setMinimum(0)
        self.mirror_x_slider.setMaximum(100)
        self.mirror_x_slider.valueChanged.connect(self.update_mirror_x)
        layout.addWidget(self.mirror_x_slider)

        mirror_y_label = QLabel('Mirror Y Position')
        layout.addWidget(mirror_y_label)

        self.mirror_y_slider = QSlider(Qt.Horizontal)
        self.mirror_y_slider.setMinimum(0)
        self.mirror_y_slider.setMaximum(100)
        self.mirror_y_slider.valueChanged.connect(self.update_mirror_y)
        layout.addWidget(self.mirror_y_slider)

        self.setLayout(layout)

    def update_mirror_x(self, value):
        self.mirror.x = value

    def update_mirror_y(self, value):
        self.mirror.y = value


class LaserApp(QMainWindow):
    def __init__(self, lasers, mirror):
        super().__init__()
        self.lasers = lasers
        self.mirror = mirror
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 500)
        self.setWindowTitle('Laser and Mirror Control App')

        laser_group = QGroupBox('Lasers')
        laser_layout = QVBoxLayout()
        for laser in self.lasers:
            laser_widget = LaserWidget(laser)
            laser_layout.addWidget(laser_widget)
        laser_group.setLayout(laser_layout)

        mirror_group = QGroupBox('Mirror')
        mirror_layout = QVBoxLayout()
        mirror_widget = MirrorWidget(self.mirror)
        mirror_layout.addWidget(mirror_widget)
        mirror_group.setLayout(mirror_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(laser_group)
        main_layout.addWidget(mirror_group)

        self.calibrate_button = QPushButton('Calibrate')
        self.calibrate_button.clicked.connect(self.calibrate)
        main_layout.addWidget(self.calibrate_button)

        main_widget = QWidget(self)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)
        self.show()

    def calibrate(self):
        # Implement your calibration function here
        print("Calibration function executed")


class LaserMarkerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.windowGeo = (300, 300, 1000, 1000)
        self.setMouseTracking(True)
        self.mouseX = None
        self.mouseY = None
        self.board_num = 0
        self.setWindowOpacity(0.7)
        self.scale = 0.025
        self.offset = (-0.032000, -0.046200)

        self.initMarker()
        self.initUI()

    def initUI(self):
        self.setGeometry(
            self.windowGeo[0],
            self.windowGeo[1],
            self.windowGeo[2],
            self.windowGeo[3],
        )
        self.setWindowTitle('Mouse Tracker')
        # self.setFixedSize(
        #     self.windowGeo[2],
        #     self.windowGeo[3],
        # )
        self.show()

    def initMarker(self):
        scene = QGraphicsScene(self)
        view = QGraphicsView(scene)
        view.setMouseTracking(True)
        self.setCentralWidget(view)
        self.setMouseTracking(True)
        self.marker = QGraphicsSimpleTextItem('X')
        self.marker.setFlag(QGraphicsItem.ItemIsMovable, True)
        scene.addItem(self.marker)

    def recordinate(self, rawcord):
        return -self.scale * (rawcord - (self.windowGeo[2] / 2)) / 50

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        new_cursor_position = event.screenPos()

        print(f'current x: {new_cursor_position}')

    def mousePressEvent(self, event):
        marker_x = self.marker.pos().x()
        marker_y = self.marker.pos().y()
        print(f'x position: {(marker_x, marker_y)}')
        # print('Mouse press coords: ( %f : %f )' % (self.mouseX, self.mouseY))

    def mouseReleaseEvent(self, event):
        print('Mouse release coords: ( %f : %f )' % (self.mouseX, self.mouseY))


if __name__ == '__main__':
    import os

    os.environ["DISPLAY"] = ":1005"
    config_path = (
        "/home/eduardo.hirata/repos/coPylot/copylot/assemblies/photom/demo/config.yml"
    )
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
        lasers = [Laser(**laser_data) for laser_data in config['lasers']]
        mirror = Mirror(initial_x=0, initial_y=0)  # Initial mirror position

    app = QApplication(sys.argv)
    ctrl_window = LaserApp(lasers, mirror)
    photom_window = LaserMarkerWindow()
    # ctrl_window.show()
    sys.exit(app.exec_())
