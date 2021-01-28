import sys
import traceback
import logging
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_worker
import qdarkstyle

logging.basicConfig(format="%(message)s", level=logging.INFO)


class ThreadRunner(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(ThreadRunner, self).__init__(*args, **kwargs)

        self.title = "Multi-Thread Tester"
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 200

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.main_window_layout = QVBoxLayout()
        self.main_window_layout.setAlignment(Qt.AlignTop)

        self.qthreadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.qthreadpool.maxThreadCount())

        self.worker = qt_worker.Worker("test")

        self.start_button = QPushButton("Stop Thread")
        self.main_window_layout.addWidget(self.start_button)

        self.start_button.pressed.connect(self.worker.stop)
        self.worker.signals.finished.connect(self.thread_complete)
        self.worker.signals.progress.connect(self.log_progress)
        self.worker.signals.interrupted.connect(self.thread_interrupted)

        self.qthreadpool.start(self.worker)

        widget = QWidget()
        widget.setLayout(self.main_window_layout)

        self.setCentralWidget(widget)

        self.show()  # not shown by default

    def thread_complete(self):
        logging.info("thread complete")

    def thread_interrupted(self):
        logging.info("thread interrupted")

    def log_progress(self, int):
        logging.info(f"looped {int} times")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    thread_runner = ThreadRunner()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec())
