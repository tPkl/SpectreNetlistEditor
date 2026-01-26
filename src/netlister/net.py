from netlister.netlist_element import Netlist_Element
from netlister.instance import Instance

class Net(Netlist_Element):
    def __init__(self, name: str, parent: Instance):
        self.name = name
        self.nettype = 'standard'
        self.nodes = set()
        self.labels = {}
        self.is_vdd = False
        self.is_gnd = False
        self.is_internal = False
        self.is_io = False
        self.parent = parent

    def connect(self, pin):
        self.nodes.add(pin)

    def __repr__(self):
        return (self.parent.__repr__() + "." + self.name)