class Galvo:
    speed: float = 0.5

    def __init__(self, name: str):
        self.name = name

    def scan(self):
        raise NotImplementedError

    def set_speed(self, s: float):
        self.speed = s

    def set_minimum(self, min: float):
        raise NotImplementedError

    def set_maximum(self, max: float):
        raise NotImplementedError

    def set_position(self, pos: float):
        raise NotImplementedError
