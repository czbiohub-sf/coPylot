import sys
from widgets.utils.show_error import show_dac_error
from PyQt5.QtWidgets import QApplication

class SampleError(object):
    def __init__(self):
        self.errorcode = 404
        self.message = 'This is an error.'

app = QApplication(sys.argv)
e = SampleError()
_ = show_dac_error(e)
sys.exit(app.exec_())
