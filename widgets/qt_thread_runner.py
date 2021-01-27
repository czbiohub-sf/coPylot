import sys
import traceback
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_worker
import qdarkstyle


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

        self.start_button = QPushButton("Launch Thread!")
        self.start_button.pressed.connect(self.launch_thread)

        self.thread_name_input = QLineEdit()
        self.thread_name_input.setText("thread name")

        self.main_window_layout.addWidget(self.start_button)
        self.main_window_layout.addWidget(self.thread_name_input)

        self.qthreadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.qthreadpool.maxThreadCount())

        widget = QWidget()
        widget.setLayout(self.main_window_layout)

        self.setCentralWidget(widget)

        self.show()  # not shown by default

    def launch_thread(self):
        name = self.thread_name_input.text()
        new_worker = qt_worker.Worker(name)
        self.qthreadpool.start(new_worker)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    thread_runner = ThreadRunner()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec())
