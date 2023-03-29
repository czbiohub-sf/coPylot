import textwrap

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QGroupBox,
    QVBoxLayout,
    QScrollArea,
    QWidget,
    QApplication,
)

import logging


class QtLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.log_txt.appendPlainText(msg)


class QtLogBox(QGroupBox):
    def __init__(self, title: str):
        super().__init__()
        self.setTitle(title)
        # self.setStyleSheet('QGroupBox::title {subcontrol-origin: margin; background: transparent;}')
        self.setStyleSheet('QGroupBox {font-size: 14pt;}')
        # self.setMaximumHeight(200)
        # Add a log_txt to display text.
        self.log_txt = QPlainTextEdit()
        self.log_txt.setMinimumSize(QSize(200, 200))
        self.log_txt.setLineWidth(1)
        # self.log_txt.setAlignment(Qt.AlignTop)
        self.log_txt.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.log_txt.setReadOnly(True)

        # Define a scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.log_txt)
        self.scroll.setWidgetResizable(True)

        # Configure layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll)
        self.setLayout(layout)
