from netlister import *
import parser as p
import argparse

def main():

    # read a netlist file
    file = open('./tests/inputs/blake_netlist_001','r')
    sample = file.read()

    # parse the netlist
    parsed_netlist = p.parse_spectre(sample)

    # print the top level objects
    # for obj in parsed_netlist:
    #     if(type(obj) == subcircuit.Subcircuit):
    #         print(obj.name)
            
    current_inst = "top"
    current_cell = "top"
    defined_subckts = [obj.name for obj in parsed_netlist if type(obj) == subcircuit.Subcircuit]
    
    print(defined_subckts)
    
    while(True):
            
        print('Current Instance: ' + current_inst + " (" + current_cell + ")")
        print('Choose an instance to descend into:')
        
        options = []
        index = 0
        
        if(current_cell == "top"):
            options = []
            #print(str(index) + ") Back")
            #index = index + 1
            for obj in parsed_netlist:
                if(type(obj) == instance.Instance and obj.reference in defined_subckts):
                    print(str(index) + ") " + obj.name + " (" + obj.reference + ")")
                    index = index + 1
                    options.append(obj)
        else:
            print(str(index) + ") Back")
            index = index + 1
            selected_subckt = [obj for obj in parsed_netlist if type(obj) == subcircuit.Subcircuit and obj.name == current_cell][0]
            for insts in selected_subckt.instances:
                if(insts.reference in defined_subckts):
                    #print(str(insts))
                    print(str(index) + ") " + insts.name + " (" + insts.reference + ")")
                    index = index + 1
                    options.append(insts)
                
        selection = input("Choice: ")
        
        if(selection == "0" and current_cell != "top"):
            current_inst = ".".join(current_inst.split(".")[:-1])
            current_cell = "top"
            for level in current_inst.split("."):
                if(level == "top"):
                    pass
                if(current_cell == "top"):
                    for obj in parsed_netlist:
                        if(type(obj) == instance.Instance and obj.name == level):
                            current_cell = obj.reference
                else:
                    selected_subckt = [obj for obj in parsed_netlist if type(obj) == subcircuit.Subcircuit and obj.name == current_cell][0]
                    for inst in selected_subckt.instances:
                        if(inst.name == level):
                            current_cell = inst.reference
                    
        else:
            if(current_cell != "top"):
                current_cell = options[int(selection)-1].reference
                current_inst = current_inst + "." + options[int(selection)-1].name
            else:
                current_cell = options[int(selection)].reference
                current_inst = current_inst + "." + options[int(selection)].name
    
    


if __name__ == "__main__":
    main()
