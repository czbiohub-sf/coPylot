import sys
# from mcculw import ul
# from mcculw.ul import ULError

# from props.ao import AnalogOutputProps

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsItem,
    QGraphicsView,
    QPushButton,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QDesktopWidget,
)

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QMouseEvent, QCursor
from copylot import logger

class CustomWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.windowGeo = (300, 300, 1000, 1000)
        self.setMouseTracking(True)
        self.mouseX = None
        self.mouseY = None
        self.board_num = 0
        # self.ao_props = AnalogOutputProps(self.board_num)
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
        # self.signal_to_DAC()
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
        new_cursor_position = event.scenePos()

        print(f'current x: {new_cursor_position}')


        # self.mouseX = self.recordinate(event.x())
        # self.mouseY = self.recordinate(event.y())
        # print('Mouse coords: ( %f : %f )' % (self.mouseX, self.mouseY))
        # print(f'{event.x()}, {event.y()}')
        # ao_range = self.ao_props.available_ranges[0]
        # raw_valueX = ul.from_eng_units(self.board_num, ao_range, self.mouseX)
        # raw_valueY = ul.from_eng_units(self.board_num, ao_range, self.mouseY)
        # print(f'{raw_valueX}, {raw_valueY}')

    def mousePressEvent(self, event):
        marker_x = self.marker.pos().x()
        marker_y = self.marker.pos().y()
        print(f'x position: {(marker_x, marker_y)}')
        # print('Mouse press coords: ( %f : %f )' % (self.mouseX, self.mouseY))
        # self.signal_to_DAC()

    # def mouseReleaseEvent(self, event):
        # print('Mouse release coords: ( %f : %f )' % (self.mouseX, self.mouseY))


    # def signal_to_DAC(self):
    #     if self.mouseX is None:
    #         self.mouseX = 0
    #     if self.mouseY is None:
    #         self.mouseY = 0
    #
    #     self.mouseX = self.mouseX + self.offset[0]
    #     self.mouseY = self.mouseY + self.offset[1]
    #     ao_range = self.ao_props.available_ranges[0]
    #     raw_valueX = ul.from_eng_units(self.board_num, ao_range, self.mouseX)
    #     raw_valueY = ul.from_eng_units(self.board_num, ao_range, self.mouseY)
    #
    #     try:
    #         ul.a_out(self.board_num, 1, ao_range, raw_valueX)
    #         ul.a_out(self.board_num, 0, ao_range, raw_valueY)
    #     except ULError as e:
    #         self.show_ul_error(e)


class CtrlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #Get the number of screens and make the live view 
        num_screens = QDesktopWidget().screenCount()
        logger.debug(f'num screens {num_screens}')
        
        self.windowGeo = (1300, 300, 500, 1000)
        self.buttonSize = (200, 100)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.setGeometry(
            self.windowGeo[0],
            self.windowGeo[1],
            self.windowGeo[2],
            self.windowGeo[3],
        )
        self.setWindowTitle('Control panel')
        self.setFixedSize(
            self.windowGeo[2],
            self.windowGeo[3],
        )

        self.button = QPushButton("OK", self)
        self.button.setStyleSheet(
            "QPushButton{"
            "font-size: 24px;"
            "font-family: Helvetica;"
            "border-width: 2px;"
            "border-radius: 15px;"
            "border-color: black;"
            "border-style: outset;"
            "}\n"
            "QPushButton:pressed {background-color: gray;}"
        )
        self.button.move(250, 250)  # button location
        self.button.setGeometry(
            (self.windowGeo[2] - self.buttonSize[0]) // 2,
            100,
            self.buttonSize[0],
            self.buttonSize[1],
        )

        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dac = CustomWindow()
    ctrl = CtrlWindow()
    sys.exit(app.exec_())
