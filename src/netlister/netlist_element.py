class Netlist_Element():
    def __init__(self,typeof):
        self.typeof = typeof
        self.parent = False
    def __str__(self):
        return(self.typeof)