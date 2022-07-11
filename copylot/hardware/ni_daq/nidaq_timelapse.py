

class NIDaqTimelapse:
    def __init__(self):
        self._registered_array_generators = {}

    def register_array_generator(self, channel, generator):
        self._registered_array_generators[channel] = generator
