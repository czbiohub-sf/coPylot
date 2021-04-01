from PyQt5.QtCore import QObject, pyqtSignal


class WorkerSignals(QObject):
    running = pyqtSignal()
    finished = pyqtSignal()
