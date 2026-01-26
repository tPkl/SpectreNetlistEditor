from netlister.instance import Instance
from netlister.pin import Pin

class Device(Instance):
    def __init__(self,instance):
        self.name = instance.name
        self.parent = instance.parent
        self.parameters = instance.parameters
        self.reference = instance.reference
        self.pins = []
        self.labels = {}

    def connect(self, name, pin):
        self.pins.append(Pin(name, self))
        self.pins[-1].connect(pin)

    def __str__(self):
        return(self.typeof + ":" + self.reference + '[' + self.drain.net.name + ', '+ self.gate.net.name + ', '+ self.source.net.name + ', '+ self.bulk.net.name + ']')

    def __repr__(self):
        return(self.parent.__repr__() + "." + self.name)