from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class WorkerSignals(QObject):

    finished = pyqtSignal()
    result = pyqtSignal(object)
    interrupted = pyqtSignal()
    progress = pyqtSignal(int)
