from PyQt5.QtGui import QPainter, QPen, QImage, QColor, QPainterPath, QBrush, QFont
from PyQt5.QtWidgets import (
    QMainWindow,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsItem,
    QGraphicsView,
    QWidget,
    QApplication,
    QGraphicsPathItem,
    QGraphicsEllipseItem,
    QGraphicsRectItem,
)
from PyQt5.QtCore import (
    Qt,
    QEvent,
    QPoint,
    QRect,
    QPointF,
    QLineF,
    QTimer,
    QThread,
    pyqtSignal,
)
from PyQt5 import QtGui
from copylot.gui._qt.job_runners.worker import WorkerSignals
from qtpy.QtCore import Qt, Signal, Slot, QRunnable, QRectF

# from copylot.gui._qt.photom_control.utils.conversion import signal_to_dac
from copylot.gui._qt.photom_control.utils.conversion import value_converter
from copylot import logger
import time

"""
This script creates a LiveViewWindow to control laser spot when overlaid with camera display.
"""


class LiveViewWindow(QMainWindow):
    laser_demo_pos = pyqtSignal(QPointF)

    def __init__(self, parent):
        super().__init__()
        # Inherit arguments from ControlPanel
        self.controlpanel = parent
        self.demo_mode = parent.demo_mode
        self.mirror = self.controlpanel.mirror_0

        # Create a LiveViewwindow
        self.setMouseTracking(True)
        self.opacity = 0.7
        self.setWindowOpacity(self.opacity)
        self.left_hold = False
        self.right_hold = False
        self.setGeometry(*self.controlpanel.liveViewGeo)
        self.setWindowTitle('Mouse Tracker')
        self.show()
        print(
            f'liveView actual {self.frameGeometry().x(), self.frameGeometry().y(), self.width(), self.height()}'
        )

        # Correct geometry with top and side bars
        self.topbar_size = (
            self.frameGeometry().height() - self.controlpanel.liveViewGeo[3]
        )
        self.sidebar_size = (
            self.frameGeometry().width() - self.controlpanel.liveViewGeo[2]
        )
        self.canvas_height = self.frameGeometry().height() - self.topbar_size
        self.canvas_width = self.frameGeometry().width() - self.sidebar_size
        self.offset_x = self.canvas_width / 2
        self.offset_y = self.canvas_height / 2

        # Create a scene to manage and display 2D graphic items
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.canvas_width, self.canvas_height)

        # Create a view to display the scene
        self.view = QGraphicsView(self.scene)
        self.view.setMouseTracking(True)
        self.view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.view.viewport().installEventFilter(self)
        # Add the markers font and color
        self.marker = QGraphicsSimpleTextItem('+')
        marker_font = QFont()
        marker_font.setPointSize(20)
        marker_font.setBold(True)
        self.marker.setFont(marker_font)
        brush = QBrush(QColor('red'))
        self.marker.setBrush(brush)
        self.marker.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.scene.addItem(self.marker)
        self.view.setScene(self.scene)
        # ===========================================
        # EH: Functions that rely on other copylot hardware
        self.moveMarker(self.canvas_width / 2, self.canvas_height / 2, self.marker)

        # Create an image for drawing activation area
        self.image = QImage(self.size(), QImage.Format_ARGB32)
        # self.image.fill(Qt.white)
        self.lastPoint = QPoint()
        # Finalize window and set the view as main widget
        self.setCentralWidget(self.view)
        self.setMouseTracking(True)

        # Placeholders of attributes
        self.scanregion = QRect()
        self.ref_marker_list = []  # marker list for reference
        self.ctrl_marker_list = []  # marker list to control laser
        self.iscalib = False
        self.scan_region_list = []
        self.scan_region_num_list = []

        # TODO: this laser demo is not implemented properly.Needs further debugging
        self.laser_demo_X = 0
        self.laser_demo_Y = 0

    def initCircle(self, x=100, y=100, color='red', size=10):
        marker = QGraphicsEllipseItem(0, 0, size, size)
        marker.setBrush(QBrush(QColor(color)))
        self.drawMarker(marker, movable=False)
        return self.moveMarker(x, y, marker)
        # self.drawMarker(marker, movable=False)

    def initMarker(self, x=100, y=100, text='+', color='black', size=10):
        """
        Create a marker.
        :param x: x coordinate
        :param y: y coordinate
        :param text: text of the marker
        :param color: marker color
        :return: TextItem object
        """
        marker = QGraphicsSimpleTextItem(text)

        if isinstance(color, str):
            marker.setBrush(QColor(color))
        else:
            marker.setBrush(color)

        return self.moveMarker(x, y, marker)

    def initMarkerlist(self, cord_ref, cord_ctrl):
        """
        Create a list of markers.
        :param cord_ref: a list of reference markers.
        :param cord_ctrl: a list of control markers
        """
        self.clearMarkerlist()
        for i in range(len(cord_ref)):
            self.ref_marker_list.append(
                self.initMarker(
                    cord_ref[i][0],
                    cord_ref[i][1],
                    color=QColor(76, 0, 153)
                    if self.controlpanel.current_laser == 0
                    else Qt.red,
                    text='O',
                )
            )
            self.drawMarker(self.ref_marker_list[-1], True)
        for i in range(len(cord_ctrl)):
            self.ctrl_marker_list.append(
                self.initMarker(cord_ctrl[i][0], cord_ctrl[i][1], color='red')
            )
            self.drawMarker(self.ctrl_marker_list[-1], True)

    def initOffset(self):
        """
        Initialize offset values (when window size is changed)
        """
        self.canvas_height = self.frameGeometry().height() - self.topbar_size
        self.canvas_width = self.frameGeometry().width() - self.sidebar_size
        self.offset_x = self.canvas_width / 2
        self.offset_y = self.canvas_height / 2

    def initWindowsize(self):
        """
        Initialize window after changing window size.
        """
        self.initOffset()
        self.scene.setSceneRect(
            0,
            0,
            self.canvas_width - self.sidebar_size,
            self.canvas_height - self.topbar_size,
        )
        print(
            f'window size {self.frameGeometry().x(), self.frameGeometry().y(), self.canvas_width, self.canvas_height}'
        )

    def drawMarker(self, marker, movable=False):
        """
        Add a marker to the scene.
        :param marker: marker object
        :param movable: marker is movable on the scene if True
        """
        marker.setFlag(QGraphicsItem.ItemIsMovable, movable)
        self.scene.addItem(marker)

    def drawTetragon(self, coord):
        path = QPainterPath(QPointF(*coord[0]))
        [path.lineTo(QPointF(*i)) for i in coord[1:] + coord[:1]]
        painter = QPainter(self.image)
        painter.setPen(
            QPen(
                QColor(76, 0, 153) if self.controlpanel.current_laser == 0 else Qt.red,
                1,
                Qt.DotLine,
            )
        )
        painter.eraseRect(self.rect())
        painter.drawPath(path)
        self.view.viewport().update()

    def moveTetragon(self):
        if len(self.ref_marker_list) > 0:
            coord = [self.getMarkerCenter(mk) for mk in self.ref_marker_list]
            self.drawTetragon(coord)

    def moveMarker(self, x, y, marker=None):
        """
        Move marker to a designated position.
        :param x: x coordinate of the destination
        :param y: y coordinate of the destination
        :param marker: marker object
        :return: a marker object at new position
        """
        if not self.controlpanel.demo_mode:
            # Apply the transformation
            if (
                self.controlpanel.transform_list[
                    self.controlpanel.current_laser
                ].affmatrix
                is not None
            ):  
                print('not demo and not affmat none')
                cord = self.controlpanel.transform_list[
                    self.controlpanel.current_laser
                ].affineTrans([x, y])
                logger.info(f'moving marker {cord}')
            else:
                cord = [x, y]
            if self.controlpanel.dac_mode:
                # signal_to_dac(
                #     self.controlpanel.ao_range,
                #     cord[0],
                #     value_range=(0, self.canvas_width),  # range of output laser power
                #     Vout_range=(-10, 10),
                #     dac_ch=self.controlpanel.galvo_x,
                #     board_num=self.controlpanel.board_num,
                #     invert=True,
                # )
                # signal_to_dac(
                #     self.controlpanel.ao_range,
                #     cord[1],
                #     value_range=(0, self.canvas_height),  # range of output laser power
                #     Vout_range=(-10, 10),
                #     dac_ch=self.controlpanel.galvo_y,
                #     board_num=self.controlpanel.board_num,
                #     invert=True,
                # )
                raise NotImplementedError("DAC not implemented")
            else:
                # TODO: the mirror range is hardcoded..
                # Rescale coords to mirror values
                logger.info(f'Start marker to {cord}')
                cord[0] = value_converter(cord[0], (0, self.canvas_width), (-1.0, 1.0), invert=False)
                cord[1] = value_converter(cord[1], (0, self.canvas_height), (-1.0, 1.0), invert=True)
                logger.info(f'rescaled marker to {cord}')  
                self.mirror.position_x = cord[0][0]
                self.mirror.position_y = cord[1][0]
                logger.info(f'Moving marker to {cord}')
                time.sleep(0.02)

        if marker is not None:
            return self.dispMarkerbyCenter(marker, [x, y])

    def getMarkerCenter(self, marker):
        """
        Get the center coordinate of a marker.
        :param marker: a marker object
        :return: coordinate x & y of the marker center
        """
        if isinstance(marker, QGraphicsEllipseItem):
            boundingRect = marker.boundingRect()
            x = marker.pos().x() + boundingRect.left() + boundingRect.width() / 2
            y = marker.pos().y() + boundingRect.height() / 2
        elif isinstance(marker, QGraphicsSimpleTextItem):
            fm = QtGui.QFontMetricsF(QtGui.QFont())
            boundingRect = fm.tightBoundingRect(marker.text())
            margintop = fm.ascent() + boundingRect.top()
            x = marker.pos().x() + boundingRect.left() + boundingRect.width() / 2
            y = marker.pos().y() + margintop + boundingRect.height() / 2
        return [x, y]

    def dispMarkerbyCenter(self, marker, cord=None):
        """
        Display the marker at a given coordinate as its center position.
        :param marker: a marker object
        :param cord: coordinate of the center position
        """
        if cord is None:
            cord = (marker.x(), marker.y())

        if isinstance(marker, QGraphicsEllipseItem):
            boundingRect = marker.boundingRect()
            marker.setPos(
                cord[0] - boundingRect.width() / 2,
                cord[1] - boundingRect.height() / 2,
            )
        elif isinstance(marker, QGraphicsSimpleTextItem):
            fm = QtGui.QFontMetricsF(QtGui.QFont())
            boundingRect = fm.tightBoundingRect(marker.text())
            margintop = fm.ascent() + boundingRect.top()
            marker.setPos(
                cord[0] - boundingRect.left() - boundingRect.width() / 2,
                cord[1] - margintop - boundingRect.height() / 2,
            )
        return marker

    def removeMarker(self, marker):
        """
        Remove marker object
        :param marker: a marker object
        """
        try:
            self.scene.removeItem(marker)
        except:
            pass

    def clearMarkerlist(self):
        for i in self.ref_marker_list:
            self.removeMarker(i)
        self.ref_marker_list = []
        for i in self.ctrl_marker_list:
            self.removeMarker(i)
        self.ctrl_marker_list = []
        painter = QPainter(self.image)
        painter.eraseRect(self.rect())
        self.view.viewport().update()

    def eventFilter(self, source, event):
        """
        Event filter is used to track mouse action in real-time.
        This is required by Qt natively.
        """
        if event.type() == QEvent.MouseMove:
            mouse_pos = event.pos()
            self.statusBar().showMessage(
                f"Cursor position: ({mouse_pos.x()}, {mouse_pos.y()})"
            )
            if self.iscalib:
                self.moveTetragon()
                ctrl_marker_posi = [
                    self.getMarkerCenter(mk) for mk in self.ctrl_marker_list
                ]
                # TODO: implement this?
                if not self.controlpanel.demo_mode:
                    if self.controlpanel.dac_mode:
                        raise NotImplementedError("eventfiler dac not implemented")
                    else:
                        pass
                        # self.controlpanel.tabmanager.laser_cali.mirror_controller.data_list = list(map(list, zip(*ctrl_marker_posi)))
                        # logger.info(f'tabmanager data_list {self.controlpanel.tabmanager.laser_cali.mirror_controller.data_list}')
                # self.controlpanel.tabmanager.laser_cali.dac_controller.data_list = list(map(list, zip(*ctrl_marker_posi)))
                # print(f'Ctrl. marker {ctrl_marker_posi}')

            # Draw a selecting bounding box
            elif self.right_hold:
                # Get the shape
                shape_ind = (
                    self.controlpanel.tabmanager.multi_pattern.bg_indiv.bg_shape.checkedId()
                )
                painter = QPainter(self.image)
                painter.setPen(
                    QPen(
                        QColor(76, 0, 153)
                        if self.controlpanel.current_laser == 0
                        else Qt.red,
                        3,
                        Qt.DotLine,
                    )
                )
                self.scanregion = QRect(
                    self.lastPoint.x(),
                    self.lastPoint.y(),
                    event.pos().x() - self.lastPoint.x(),
                    event.pos().y() - self.lastPoint.y(),
                )
                painter.eraseRect(self.rect())
                if shape_ind == 0:
                    painter.drawRect(self.scanregion)
                elif shape_ind == 1:
                    painter.drawEllipse(self.scanregion)
                self.view.viewport().update()
            # Move cursor or draw area using left click
            elif self.left_hold:
                cord = self.getMarkerCenter(self.marker)
                if not self.controlpanel.demo_mode:
                    if (
                        self.controlpanel.transform_list[
                            self.controlpanel.current_laser
                        ].affmatrix
                        is not None
                    ):
                        logger.info('transforming coordinate...')
                        cord = self.controlpanel.transform_list[
                            self.controlpanel.current_laser
                        ].affineTrans(cord)
                        logger.info(f'tranferred {cord}')
                    if self.controlpanel.dac_mode:
                        # signal_to_dac(
                        #     controlpanel.ao_range,
                        #     cord[0],
                        #     (0, self.canvas_width),
                        #     Vout_range=(-10, 10),
                        #     dac_ch=controlpanel.galvo_x,
                        #     invert=True,
                        # )
                        # signal_to_dac(
                        #     controlpanel.ao_range,
                        #     cord[1],
                        #     (0, self.canvas_height),
                        #     Vout_range=(-10, 10),
                        #     dac_ch=controlpanel.galvo_y,
                        #     invert=True,
                        # )
                        raise NotImplementedError("DAC not implemented")
                    else:
                        logger.info(f'getmarker center {cord}')
                        cord[0] = value_converter(cord[0], (0, self.canvas_width), (-1.0, 1.0), invert=True)
                        cord[1] = value_converter(cord[1], (0, self.canvas_height), (-1.0, 1.0), invert=False)
                        self.mirror.position_x = cord[0][0]
                        self.mirror.position_y = cord[1][0]
        elif event.type() == QEvent.MouseButtonPress:
            print('mouse pressed')
            self.lastPoint = event.pos()
            if event.buttons() == Qt.LeftButton:
                self.left_hold = True
                print('left button clicked.')
            elif event.buttons() == Qt.RightButton:
                if self.iscalib:
                    self.controlpanel.tabmanager.laser_cali.apply_calib()
                    print('Laser calibration applied.')
                else:
                    self.right_hold = True
                print('right button clicked.')
        elif event.type() == QEvent.MouseButtonRelease:
            if self.iscalib:
                self.controlpanel.tabmanager.laser_cali.revert_calib()
                print('Laser calibration reverted.')
            else:
                if self.right_hold:
                    self.controlpanel.tabmanager.pattern_ctrl.update_scansize(
                        self.scanregion
                    )
                    self.controlpanel.tabmanager.multi_pattern.bg_indiv.update_scanpar()
                self.left_hold = False
                self.right_hold = False
                print('mouse released')

        elif event.type() == QEvent.MouseButtonDblClick:
            print('double clicked')
        elif event.type() == QEvent.Paint:
            canvasPainter = QPainter(self.view.viewport())
            canvasPainter.drawImage(self.rect(), self.image, self.image.rect())
        elif event.type() == QEvent.Resize:
            self.initWindowsize()
            self.image = QImage(self.size(), QImage.Format_ARGB32)
            self.image.fill(Qt.white)
        return QWidget.eventFilter(self, source, event)

    def draw_preview(self, scan_path):
        painter = QPainter(self.image)
        painter.setPen(
            QPen(
                QColor(76, 0, 153) if self.controlpanel.current_laser == 0 else Qt.red,
                2,
                Qt.SolidLine,
            )
        )
        painter.eraseRect(self.scanregion)
        for i in range(len(scan_path[0]) - 1):
            point1 = QPointF(scan_path[0][i], scan_path[1][i])
            point2 = QPointF(scan_path[0][i + 1], scan_path[1][i + 1])
            line = QLineF(point1, point2)
            painter.drawLine(line)
        self.view.viewport().update()
        logger.info('Drawing preview...')

    def clear_preview(self, region=None):
        if region is None:
            region = self.scanregion
        elif region == 'all':
            region = self.rect()
        painter = QPainter(self.image)
        painter.eraseRect(region)
        self.view.viewport().update()

    def draw_scanregion(self, param, ind):
        if ind == 0:
            item = QGraphicsRectItem(*param)
        elif ind == 1:
            item = QGraphicsEllipseItem(*param)
        itemn = QGraphicsSimpleTextItem(str(len(self.scan_region_list) + 1))
        itemn.setPos(param[0], param[1])
        item.setPen(
            QPen(
                QColor(76, 0, 153) if self.controlpanel.current_laser == 0 else Qt.red,
                2,
                Qt.SolidLine,
            )
        )
        b = QBrush(Qt.DiagCrossPattern)
        b.setColor(
            QColor(76, 0, 153) if self.controlpanel.current_laser == 0 else Qt.red
        )
        item.setBrush(b)
        self.scan_region_list.append(item)
        self.scan_region_num_list.append(itemn)
        self.scene.addItem(item)
        self.scene.addItem(itemn)
        self.scene.update()

    def remove_scanregion(self, ind):
        self.scene.removeItem(self.scan_region_list[ind])
        del self.scan_region_list[ind]
        self.scene.removeItem(self.scan_region_num_list[ind])
        del self.scan_region_num_list[ind]

    def reorder_scanregion(self):
        for i, j in enumerate(self.scan_region_num_list):
            j.setText(str(i + 1))

    # def update_cursor(self, pos):
    #     self.statusBar().showMessage(f'Cursor pos:({pos.x()}, {pos.y()})')

    def draw_demo_laser(self):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(0, 255, 0, 127)))
        painter.drawEllipse(QRectF(self.laser_demo_X, self.laser_demo_Y, 20, 20))

    def start_laser_demo(self):
        self.demo_running = True
        self.laser_demo_thread = LaserDemo(self)
        self.draw_demo_laser()
        self.laser_demo_thread.laser_demo_pos.connect(self.update_demo_pos)
        self.laser_demo_thread.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawEllipse(QRectF(self.laser_demo_X, self.laser_demo_Y, 20, 20))

    def update_demo_pos(self, pos):
        self.laser_demo_X = pos.x()
        self.laser_demo_Y = pos.y()
        self.update()

    def stop_laser_demo(self):
        self.demo_running = False


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
        # self.laserDemo = True

    def run(self):
        while True:
            if self.parent.demo_running:
                logger.info(f"coords :{self.coords[self.index]}")
                self.index += 1
                if self.index >= len(self.coords):
                    self.index = 0
                self.laser_demo_pos.emit(QPointF(*self.coords[self.index]))
            self.msleep(50)

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


class photom_marker(QGraphicsSimpleTextItem):
    """
    Photom marker that allows dragging with the left click and trigger secondary function with right click

    Parameters
    ----------
    QGraphicsSimpleTextItem :
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            brush = QBrush(Qt.red)
            self.setBrush(brush)
        elif event.button() == Qt.LeftButton:
            brush = QBrush(Qt.black)
            self.setBrush(brush)
        super().mousePressEvent(event)
