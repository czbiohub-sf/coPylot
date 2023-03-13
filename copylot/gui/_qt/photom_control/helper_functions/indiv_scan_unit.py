from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QButtonGroup,
    QRadioButton,
    QLineEdit,
    QGroupBox,
    QGridLayout,
    QApplication,
)

from widgets.scan_algrthm.scan_algorithm import ScanAlgorithm


class IndividualScanSetting(QGroupBox):
    def __init__(self, tabmanager, parent):
        super().__init__()
        self.tabmanager = tabmanager
        self.parent = parent
        self.window = tabmanager.parent.window1
        self.rb_rect = QRadioButton('Rect', self)
        self.rb_disk = QRadioButton('Disk', self)
        self.rb_lsj = QRadioButton('Lissajous', self)
        self.rb_rst = QRadioButton('Raster', self)
        self.rb_spr = QRadioButton('Spiral', self)
        self.size_input = QLineEdit(self)
        self.center_pos = QLineEdit(self)
        self.gap_input = QLineEdit('1', self)
        self.speed_input = QLineEdit('1', self)
        self.cyl_input = QLineEdit('1', self)
        self.pb_preview = QPushButton('Preview')
        self.pb_preview.setCheckable(True)
        self.stop_draw_flag = False
        self.pause_draw_flag = False
        self.external_draw_list = None
        self.scanobj = None
        self.scan_path = None
        self.size_par = None
        self.cycl_par = None
        self.gap_par = None
        self.speed_par = None
        self.marker_pos0 = self.window.getMarkerCenter(self.window.marker)
        self.dac_controller = None
        self.scan_size = None
        self.scan_center = None

        # ButtonGroups for scanning algorithm
        self.bg_shape = QButtonGroup(self)
        self.bg_shape.addButton(self.rb_rect, 0)
        self.bg_shape.addButton(self.rb_disk, 1)
        self.bg_shape.buttons()[self.tabmanager.parent.current_scan_shape].setChecked(True)
        self.bg_scan = QButtonGroup(self)
        self.bg_scan.addButton(self.rb_lsj, 0)
        self.bg_scan.addButton(self.rb_rst, 1)
        self.bg_scan.addButton(self.rb_spr, 2)
        self.bg_scan.buttons()[self.tabmanager.parent.current_scan_pattern].setChecked(True)

        # Construct grid layout
        self.setTitle('Individual pattern')
        self.setStyleSheet('font-size: 14pt')
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.addWidget(self.rb_rect, 0, 0)
        grid.addWidget(self.rb_disk, 0, 1)
        grid.addWidget(self.pb_preview, 0, 2)
        grid.addWidget(QLabel('Size (V, H)'), 1, 0)
        grid.addWidget(self.size_input, 1, 1)
        grid.addWidget(QLabel('Center (x, y)'), 2, 0)
        grid.addWidget(self.center_pos, 2, 1)
        grid.addWidget(QLabel('Interval'), 3, 0)
        grid.addWidget(self.gap_input, 3, 1)
        grid.addWidget(QLabel('pixels'), 3, 2)
        grid.addWidget(QLabel('Speed'), 4, 0)
        grid.addWidget(self.speed_input, 4, 1)
        grid.addWidget(QLabel('sec/cycle'), 4, 2)
        grid.addWidget(QLabel('Cycle'), 5, 0)
        grid.addWidget(self.cyl_input, 5, 1)
        grid.addWidget(QLabel('times'), 5, 2)
        grid.addWidget(self.rb_lsj, 6, 0)
        grid.addWidget(self.rb_rst, 6, 1)
        grid.addWidget(self.rb_spr, 6, 2)
        grid.setAlignment(Qt.AlignCenter)
        self.setLayout(grid)

        # Linking buttons to functions
        self.pb_preview.clicked.connect(self.preview)
        self.bg_shape.buttonClicked.connect(lambda: self.tabmanager.update_scan_shape(self.bg_shape.checkedId()))
        self.bg_shape.buttonClicked.connect(lambda: self.tabmanager.update_scan_pattern(self.bg_scan.checkedId()))
        self.bg_scan.buttonClicked.connect(lambda: self.tabmanager.update_scan_pattern(self.bg_scan.checkedId()))

    def preview(self):
        """
        Show the real scanning path on the live window.
        """
        if self.pb_preview.isChecked():
            if self.checkstatus():
                self.select_algorithm((self.window.scanregion.center().x(), self.window.scanregion.center().y()))
                path = self.scan_path
                self.window.draw_preview(path)
                if len(path[0]) > 0:
                    self.parent.msgbox.update_msg('Showing preview of scanning path.')
        else:
            self.window.clear_preview()
            self.parent.msgbox.update_msg('')

    def update_scanpar(self):
        """
        Update scanning parameters after dragging with a right click.
        """
        self.scan_size = (abs(self.window.scanregion.height()), abs(self.window.scanregion.width()))
        self.scan_center = (self.window.scanregion.center().x(), self.window.scanregion.center().y())
        self.size_input.setText(str(self.scan_size))
        self.center_pos.setText(str(self.scan_center))

    def checkstatus(self):
        """
        Check if all parameters are numbers and fill them into attributes.
        """
        self.parent.msgbox.update_msg(f'Checking status ...')
        try:
            [float(i) for i in self.scan_size]
        except:
            self.parent.msgbox.update_msg(f'Invalid input in Size. \nInterval value must be a number.', 'red')
            return False
        try:
            self.cycl_par = float(self.cyl_input.text())
            # if self.cycl_par != float(self.cyl_input.text()):
            #     self.parent.msgbox.update_msg(f'Cycle is rounded to {self.cycl_par}.')
        except:
            self.parent.msgbox.update_msg(f'Invalid input in Cycle. \nInterval value must be an integer.', 'red')
            return False
        try:
            self.gap_par = float(self.gap_input.text())
        except:
            self.parent.msgbox.update_msg('Invalid input in Interval. \nInterval value must be a number.', 'red')
            return False
        try:
            self.speed_par = float(self.speed_input.text())
        except:
            self.parent.msgbox.update_msg('Invalid input in Speed. \nInterval value must be a number.', 'red')
            return False
        return True

    def select_algorithm(self, position=None):
        """
        Select scanning algorithm. Scanning data will be created in self.scan_path.
        """
        self.parent.msgbox.update_msg(f'Selecting algorithm ...')
        if position is None:
            self.marker_pos0 = self.window.getMarkerCenter(self.window.marker)
        else:
            self.marker_pos0 = position
        self.scanobj = ScanAlgorithm(
            self.marker_pos0,
            self.scan_size,
            self.gap_par,
            self.bg_shape.checkedButton().text(),
            self.speed_par,
        )
        print('Scan with ' + self.bg_scan.buttons()[self.bg_scan.checkedId() - 1].text())
        if self.bg_scan.checkedId() == 0:
            self.scan_path = self.scanobj.generate_lissajous()
        elif self.bg_scan.checkedId() == 1:
            self.scan_path = self.scanobj.generate_sin()
        elif self.bg_scan.checkedId() == 2:
            self.scan_path = self.scanobj.generate_spiral()
        print(f'total number of points {len(self.scan_path[0])}')

