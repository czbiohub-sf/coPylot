from PyQt5.QtCore import QObject, pyqtSignal


class WorkerSignals(QObject):
    launching = pyqtSignal()
    running = pyqtSignal()
    finished = pyqtSignal()
