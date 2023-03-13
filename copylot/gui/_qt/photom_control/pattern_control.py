from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QButtonGroup,
    QVBoxLayout,
)
from widgets.helper_functions.draw_pattern_unit import DrawPatternUnit
from widgets.helper_functions.messagebox import MessageBox
from widgets.helper_functions.laser_selection_box import LaserSelectionBox


class PatternControl(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.laser_selection_box = LaserSelectionBox(self.parent)
        self.bttngp_sq = DrawPatternUnit('Square', parent)
        self.bttngp_di = DrawPatternUnit('Disk', parent)
        self.msgbox = MessageBox('Current Status')

        # A ButtonGroup with exclusive selection for shape selection
        self.bg_pattern_selection = QButtonGroup(self)
        self.bg_pattern_selection.addButton(self.bttngp_sq.rb_group, 0)
        self.bg_pattern_selection.addButton(self.bttngp_di.rb_group, 1)
        self.bg_pattern_selection.setExclusive(True)
        self.bg_pattern_selection.buttons()[self.parent.parent.current_scan_shape].setChecked(True)
        self.bg_pattern_selection.buttonClicked.connect(
            lambda: self.parent.update_scan_shape(self.bg_pattern_selection.checkedId())
        )
        self.bg_pattern_selection.buttonClicked.connect(
            lambda: self.parent.update_scan_pattern(self.get_pattern_unit().bg_scan.checkedId())
        )
        # Checking if the button responses
        self.bttngp_sq.rb_group.clicked.connect(lambda: print(f'A square {self.bttngp_sq.verticalsize_input.text()} on a side will be drawn.'))
        self.bttngp_di.rb_group.clicked.connect(lambda: print(f'A disk {self.bttngp_sq.verticalsize_input.text()} on the radius will be drawn.'))

        # Link groups
        self.bttngp_sq.external_draw_list = [self.bttngp_di]
        self.bttngp_di.external_draw_list = [self.bttngp_sq]
        self.bttngp_sq.messagebox = self.msgbox
        self.bttngp_di.messagebox = self.msgbox

        # Set layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.layout.addWidget(self.laser_selection_box)
        self.layout.addWidget(self.bttngp_sq)
        self.layout.addWidget(self.bttngp_di)
        self.layout.addWidget(self.msgbox)
        self.setLayout(self.layout)

    def get_pattern_unit(self):
        if self.bg_pattern_selection.checkedId() == 0:
            return self.bttngp_sq
        elif self.bg_pattern_selection.checkedId() == 1:
            return self.bttngp_di

    def update_scansize(self, rect):
        punit = self.get_pattern_unit()
        punit.verticalsize_input.setText(str(abs(rect.height())))
        punit.horizontalsize_input.setText(str(abs(rect.width())))

    def print_log(self, obj=None):
        for i in obj.buttons():
            if i.isChecked():
                print(i.text() + f' pattern is selected.')


