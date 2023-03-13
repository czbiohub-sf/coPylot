import textwrap

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QLabel,
    QGroupBox,
    QVBoxLayout,
    QScrollArea,
    QWidget,
    QApplication)


class MessageBox(QGroupBox):
    def __init__(self, title):
        super().__init__()
        self.setTitle(title)
        # self.setStyleSheet('QGroupBox::title {subcontrol-origin: margin; background: transparent;}')
        self.setStyleSheet('QGroupBox {font-size: 14pt;}')
        # self.setMaximumHeight(200)
        # Add a QLabel to display text.
        self.qlabel = QLabel()
        self.qlabel.setAlignment(Qt.AlignTop)
        self.qlabel.setWordWrap(True)

        # Define a scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.qlabel)
        self.scroll.setWidgetResizable(True)

        # Configure layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll)
        self.setLayout(layout)

    def update_msg(self, message, color='black'):
        self.qlabel.setText(message)
        self.qlabel.setStyleSheet(f'color: {color}')
        self.qlabel.repaint()
