from netlister.netlist_element import Netlist_Element
from netlister.net import Net

class Subcircuit(Netlist_Element):
    def __init__(self, name: str, nets: list, instances: list):
        self.name = name;
        self.labels = {}
        self.power_nets = []
        self.ground_nets = []
        self.internal_nets = []
        # dictionarry of net names,
        # key is net name, value is net object
        # marke these nets also as io
        self.nets = {} #= nets;
        for n in nets:
            self.nets[n] = Net(n, self)
            self.nets[n].is_io = True
        
        self.instances = instances;
        for i in self.instances:
            # register subcircuit as parrent
            i.parent = self
            # add all internal nets
            for n in i.pins:
                if n not in self.nets:
                    self.nets[n] = Net(n, self)
        
        Netlist_Element.__init__(self,'subcircuit')

    def __str__(self):
        insts = {}
        for i in self.instances:
            insts[i.name] = i.reference
        return(self.typeof + " " + self.name + "(" + str(self.nets) + "):" + str(insts))

    def map_instances(self, mapping_function):
        for i in range(len(self.instances)):
            self.instances[i] = mapping_function(self.instances[i])
            
    def map_nets(self, mapping_function):
        for n in self.nets:
            self.nets[n] = mapping_function(self.nets[n])
    
    def __repr__(self):
        return self.name