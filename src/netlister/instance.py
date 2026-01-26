from netlister.netlist_element import Netlist_Element

class Instance(Netlist_Element):
    def __init__(self, name, pins: list, reference: str, parameters: dict):
        self.name = name;
        self.pins = pins;
        self.reference = reference;
        self.parameters = parameters;
        Netlist_Element.__init__(self,'instance')
    def __str__(self):
        return(self.typeof + " " + self.name + "@" + self.reference + str(self.parameters))