import sys

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
from PyQt5.QtGui import QPainter, QPen, QMouseEvent, QCursor, QFont, QFontMetricsF
from copylot import logger


class CustomWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.windowGeo = (300, 300, 500, 500)
        self.setMouseTracking(True)
        self.mouseX = None
        self.mouseY = None
        self.board_num = 0
        self.setWindowOpacity(0.7)
        self.scale = 0.025
        self.offset = (-0.032000, -0.046200)

        self.view = None
        self.scene = None
        self.initMarker()
        self.initUI()
        print(
            f'liveView actual {self.frameGeometry().x(), self.frameGeometry().y(), self.width(), self.height()}'
        )
        print(self.frameGeometry().height(), self.frameGeometry().width())

    def initUI(self):
        # self.setGeometry(
        #     self.windowGeo[0],
        #     self.windowGeo[1],
        #     self.windowGeo[2],
        #     self.windowGeo[3],
        # )
        self.setWindowTitle('Mouse Tracker')
        self.setFixedSize(
            self.windowGeo[2],
            self.windowGeo[3],
        )
        self.show()

    def initMarker(self):
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setMouseTracking(True)
        self.setCentralWidget(self.view)
        self.view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.view.viewport().installEventFilter(self)

        self.setMouseTracking(True)
        self.marker = QGraphicsSimpleTextItem('X')
        self.marker.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.scene.addItem(self.marker)
        self.view.setScene(self.scene)
        # Disable scrollbars
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.sidebar_size = self.frameGeometry().width() - self.windowGeo[2]
        self.topbar_size = self.frameGeometry().height() - self.windowGeo[3]
        self.canvas_width = self.view.frameGeometry().width() - self.sidebar_size
        self.canvas_height = self.view.frameGeometry().height() - self.topbar_size
        print(f'sidebar size: {self.sidebar_size}, topbar size: {self.topbar_size}')
        print(f'canvas width: {self.canvas_width}, canvas height: {self.canvas_height}')
        self.display_marker_center(
            self.marker, (self.canvas_width / 2, -self.canvas_height / 2)
        )

    def recordinate(self, rawcord):
        return -self.scale * (rawcord - (self.windowGeo[2] / 2)) / 50

    # def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
    #     new_cursor_position = event.screenPos()

    #     print(f'current x: {new_cursor_position}')

    # def mousePressEvent(self, event):
    #     # marker_x = self.marker.pos().x()
    #     # marker_y = self.marker.pos().y()
    #     marker_x, marker_y = self.get_marker_center(self.marker)
    #     print(f'x position: {(marker_x, marker_y)}')

    #     # print('Mouse press coords: ( %f : %f )' % (self.mouseX, self.mouseY))

    # def mouseReleaseEvent(self, event):
    #     pass
    #     # print('Mouse release coords: ( %f : %f )' % (self.mouseX, self.mouseY))

    def get_marker_center(self, marker):
        fm = QFontMetricsF(QFont())
        boundingRect = fm.tightBoundingRect(marker.text())
        mergintop = fm.ascent() + boundingRect.top()
        x = marker.pos().x() + boundingRect.left() + boundingRect.width() / 2
        y = marker.pos().y() + mergintop + boundingRect.height() / 2
        return x, y

    def display_marker_center(self, marker, cord=None):
        if cord is None:
            cord = (marker.x(), marker.y())

        # Get the font metrics for accurate measurement
        fm = QFontMetricsF(marker.font())

        # Calculate the bounding rectangle of the text
        boundingRect = fm.boundingRect(marker.text())

        # Calculate the correct position to move the marker
        # so that its center is at the specified coordinates
        newX = cord[0] - boundingRect.width() / 2
        newY = cord[1] - boundingRect.height() / 2

        # Set the new position of the marker
        marker.setPos(newX, newY)
        return marker

    def eventFilter(self, source, event):
        "The mouse movements do not work without this function"
        if event.type() == QMouseEvent.MouseMove:
            print('mouse move')
            print(f'x: {event.screenPos().x()}, y: {event.screenPos().y()}')
            # print(f'x: {event.posF().x()}, y: {event.posF().y()}')
            # print(f'x: {event.localPosF().x()}, y: {event.localPosF().y()}')
            # print(f'x: {event.windowPosF().x()}, y: {event.windowPosF().y()}')
            # print(f'x: {event.screenPosF().x()}, y: {event.screenPosF().y()}')
            # print(f'x: {event.globalPosF().x()}, y: {event.globalPosF().y()}')
            print(f'x: {event.pos().x()}, y: {event.pos().y()}')
        elif event.type() == QMouseEvent.MouseButtonPress:
            print('mouse button pressed')
            if event.buttons() == Qt.LeftButton:
                print('left button pressed')
            elif event.buttons() == Qt.RightButton:
                print('right button pressed')

        elif event.type() == QMouseEvent.MouseButtonRelease:
            print('mouse button released')
            if event.buttons() == Qt.LeftButton:
                print('left button released')
            elif event.buttons() == Qt.RightButton:
                print('right button released')

        return super(CustomWindow, self).eventFilter(source, event)


class CtrlWindow(QMainWindow):
    def __init__(self, mouse_tracker_window):
        super().__init__()
        # Get the number of screens and make the live view
        num_screens = QDesktopWidget().screenCount()
        logger.debug(f'num screens {num_screens}')
        self.mouse_tracker_window = mouse_tracker_window
        self.windowGeo = (1300, 300, 500, 1000)
        self.buttonSize = (200, 100)
        self.initUI()

        # Set the layout on the central widget

    def initUI(self):
        # Create a central widget for the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

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
        self.button.clicked.connect(self.buttonClicked)
        layout.addWidget(self.button)

        self.show()

    def buttonClicked(self):
        print('button clicked')
        x, y = self.mouse_tracker_window.get_marker_center(
            self.mouse_tracker_window.marker
        )
        print(f'x: {x}, y: {y}')
        self.mouse_tracker_window.marker.setPos(0, 0)
        # self.mouse_tracker_windowdisplay_marker_center(self.mouse_tracker_window.marker, (0.0, 0.0))
        # self.mouse_tracker_window.marker.setPos(0, 0)


if __name__ == "__main__":
    import os

    os.environ["DISPLAY"] = ":1005"
    app = QApplication(sys.argv)
    dac = CustomWindow()
    ctrl = CtrlWindow(dac)
    sys.exit(app.exec_())
