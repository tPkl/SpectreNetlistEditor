from netlister.netlist_element import Netlist_Element
from netlister.instance import Instance
from netlister.net import Net

class Pin(Net):
    def __init__(self, name: str, parent: Instance):
        self.name = name
        self.parent = parent
        self.net = False
        self.direction = False

    def connect(self, net: Net):
        if not self.net:
            # get the net object from the subcircuit
            self.net = self.parent.parent.nets[net]
            self.net.connect(self)
    
    def __repr__(self):
        return (self.parent.__repr__() + "." + self.name)