from PyQt5.QtCore import Qt, QPersistentModelIndex
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QButtonGroup,
    QRadioButton,
    QLineEdit,
    QGroupBox,
    QGridLayout,
    QApplication,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class ScanTable(QGroupBox):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setHorizontalHeaderLabels(
            ['Shape', 'Center', 'Size', 'Interval', 'Speed', 'Cycle', 'Pattern', 'Laser']
        )
        h = self.tableWidget.horizontalHeader()
        [h.setSectionResizeMode(i, QHeaderView.ResizeToContents) for i in range(8)]
        self.pb_add = QPushButton('Add', self)
        self.pb_remove = QPushButton('Remove', self)

        # Set layout
        self.setTitle('Scan Table')
        self.setStyleSheet('font-size: 14pt')
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.addWidget(self.tableWidget, 0, 0, 1, 2)
        grid.addWidget(self.pb_add, 1, 0)
        grid.addWidget(self.pb_remove, 1, 1)
        self.setLayout(grid)

        # Connect buttons
        self.pb_add.clicked.connect(self.add_scan)
        self.pb_remove.clicked.connect(self.remove_row)

    def add_scan(self):
        """
        Add a scanning region to the table.
        """
        if self.checkstatus():
            self.parent.parent.parent.window1.draw_scanregion(
                self.parent.parent.parent.window1.scanregion.getRect(), self.parent.bg_indiv.bg_shape.checkedId()
            )
            data = [
                self.parent.bg_indiv.bg_shape.buttons()[self.parent.bg_indiv.bg_shape.checkedId()].text(),
                self.parent.bg_indiv.scan_center,
                self.parent.bg_indiv.scan_size,
                self.parent.bg_indiv.gap_input.text(),
                self.parent.bg_indiv.speed_input.text(),
                self.parent.bg_indiv.cyl_input.text(),
                self.parent.bg_indiv.bg_scan.buttons()[self.parent.bg_indiv.bg_scan.checkedId()].text(),
                '405' if self.parent.parent.parent.current_laser == 0 else '785',
            ]
            self.add_row(data)

    def add_row(self, data):
        ind = self.tableWidget.rowCount()
        self.tableWidget.insertRow(ind)
        for i, v in enumerate(data):
            self.tableWidget.setItem(ind, i, QTableWidgetItem(str(v)))
        self.tableWidget.viewport().update()

    def remove_row(self):
        # Get selected rows
        selected = []
        for i in sorted(self.tableWidget.selectionModel().selectedRows()):
            selected.append(QPersistentModelIndex(i))
        # indices of selected rows
        ind = [i.row() for i in selected]
        # Remove selected rows
        for i in selected:
            self.tableWidget.removeRow(i.row())
        # Remove scan regions
        for i in ind[::-1]:
            self.parent.parent.parent.window1.remove_scanregion(i)
        self.parent.parent.parent.window1.reorder_scanregion()
        self.parent.parent.parent.window1.scene.update()

    def checkstatus(self):
        """
        Check if all parameters are numbers and fill them into attributes.
        """
        self.parent.msgbox.update_msg(f'Checking status ...')
        try:
            [float(i) for i in self.parent.bg_indiv.scan_size]
        except:
            self.parent.msgbox.update_msg(f'Invalid input in Size. \nInterval value must be a number.', 'red')
            return False
        try:
            self.cycl_par = float(self.parent.bg_indiv.cyl_input.text())
            # if self.cycl_par != float(self.cyl_input.text()):
            #     self.parent.msgbox.update_msg(f'Cycle is rounded to {self.cycl_par}.')
        except:
            self.parent.msgbox.update_msg(f'Invalid input in Cycle. \nInterval value must be an integer.', 'red')
            return False
        try:
            self.gap_par = float(self.parent.bg_indiv.gap_input.text())
        except:
            self.parent.msgbox.update_msg('Invalid input in Interval. \nInterval value must be a number.', 'red')
            return False
        try:
            self.speed_par = float(self.parent.bg_indiv.speed_input.text())
        except:
            self.parent.msgbox.update_msg('Invalid input in Speed. \nInterval value must be a number.', 'red')
            return False
        self.parent.msgbox.update_msg('')
        return True
