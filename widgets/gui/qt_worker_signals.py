from PyQt5.QtCore import *


class WorkerSignals(QObject):
    finished = pyqtSignal()
