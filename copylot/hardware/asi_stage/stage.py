

class ASIStageException(Exception):
    pass


class ASIStage:
    def __init__(self, com_port=None):
        self.com_port = com_port if com_port else "COM3"
