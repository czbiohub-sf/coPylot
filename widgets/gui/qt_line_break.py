from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame


class LineBreak(QWidget):
    def __init__(self, alignment, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.alignment = alignment

        self.line_break_layout = QHBoxLayout()
        self.line_break_layout.setContentsMargins(0, 0, 0, 0)

        self.hline_break = QFrame()
        self.hline_break.setFrameShape(QFrame.HLine)
        self.hline_break.setFrameShadow(QFrame.Sunken)
        self.line_break_layout.setAlignment(self.alignment)
        self.line_break_layout.addWidget(self.hline_break, 0)

        self.setLayout(self.line_break_layout)
