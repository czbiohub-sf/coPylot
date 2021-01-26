import sys
import traceback
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import qt_worker
import qdarkstyle


class ThreadRunner(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # run the init of QMainWindow

        self.title = "Multi-Thread Tester"
        self.left = 10
        self.top = 10
        self.width = 650
        self.height = 500

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.qthreadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.qthreadpool.maxThreadCount())

        new_worker = qt_worker.Worker(self.new_thread)
        main_worker = qt_worker.Worker(self.main_thread)

        self.qthreadpool.start(new_worker)
        self.qthreadpool.start(main_worker)

        self.show()  # not shown by default

    def new_thread(self):
        for i in range(0, 10):
            print("new thread")
            time.sleep(1)

        print("thread complete")

    def main_thread(self):
        for i in range(0, 10):
            print("main thread")
            time.sleep(1)

        print("thread complete")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    thread_runner = ThreadRunner()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec())
