from PyQt5.QtWidgets import QErrorMessage


class show_dac_error(QErrorMessage):
    def __init__(self, dac_error):
        super().__init__()
        message = (
            'A DAC error occurred.<br>Error Code: ' + str(dac_error.errorcode)
            + '<br>Message: ' + dac_error.message
        )
        QErrorMessage.showMessage(self, message)
