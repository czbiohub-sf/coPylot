import sys
import traceback
import logging
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

logging.basicConfig(format="%(message)s", level=logging.INFO)


class Worker(QRunnable):
    def __init__(self, name, *args, **kwargs):
        super(Worker, self).__init__()
        self.name = name
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        logging.info(f"{self.name} started")
        for i in range(0, 10):
            logging.info(f"{self.name} running")
            time.sleep(1)

        logging.info(f"{self.name} complete")
