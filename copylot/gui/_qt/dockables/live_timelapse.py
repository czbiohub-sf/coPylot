from PyQt5.QtWidgets import QWidget


class LiveTimelapseControlDockWidget(QWidget):

    def __init__(self, parent, threadpool):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.threadpool = threadpool

        self.running = False
        self.wait_before_shutdown = False
