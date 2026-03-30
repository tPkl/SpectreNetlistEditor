from netlister.netlist_element import Netlist_Element

class Netlist(Netlist_Element):
    def __init__(self):
        super().__init__('netlist')
        self.library = None
        self.cell = None
        self.view = None
        self.subcircuits = {}
        self.top_level_instances = []
        self.global_nets = []
        self.parameters = {}
        self.includes = []
        self.simulator_options = []
        self.analyses = []
        
    def get_subcircuit(self, name: str):
        return self.subcircuits.get(name)

    def get_instance(self, path: str):
        # Resolve dot-separated path like "I1.I2.M1" starting from top_level
        parts = path.split('.')
        current_instances = self.top_level_instances
        inst = None

        for part in parts:
            inst = next((i for i in current_instances if i.name == part), None)
            if inst is None:
                return None
            
            # If there are more parts, descend but only if inst references a subckt
            if part != parts[-1]:
                subckt = self.get_subcircuit(inst.reference)
                if subckt:
                    current_instances = subckt.instances
                else:
                    return None
                    
        return inst
