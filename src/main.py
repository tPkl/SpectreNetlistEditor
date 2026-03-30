from netlister import *
import parser as p
import argparse

def main():
    # read a netlist file
    file_path = './tests/inputs/blake_netlist_001'
    try:
        with open(file_path, 'r') as file:
            sample = file.read()
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return

    # parse the netlist
    print(f"Parsing netlist from {file_path}...")
    parsed_netlist = p.parse_spectre(sample)
    print("Done parsing.")

    defined_subckts = list(parsed_netlist.subcircuits.keys())
    print("\nDefined Subcircuits: ", defined_subckts)
    
    current_inst_path = "top"
    current_cell = "top"
    
    while True:
        print(f"\n---")
        print(f"Current Instance Path: {current_inst_path}")
        print(f"Current Cell: {current_cell}")
        
        if current_cell == "top":
            print(f"Design Meta: Library={parsed_netlist.library}, Cell={parsed_netlist.cell}, View={parsed_netlist.view}")
            print(f"Analyses: {len(parsed_netlist.analyses)}, Simulator Options: {len(parsed_netlist.simulator_options)}, Includes: {len(parsed_netlist.includes)}")
        else:
            subckt = parsed_netlist.get_subcircuit(current_cell)
            if subckt:
                print(f"Subcircuit Meta: Library={subckt.library}, Cell={subckt.cell}, View={subckt.view}")
        
        print("\nChoose an instance to descend into (or type 'q' to quit):")
        
        options = []
        index = 0
        
        if current_cell == "top":
            for inst in parsed_netlist.top_level_instances:
                if inst.reference in defined_subckts:
                    print(f"{index}) {inst.name} ({inst.reference})")
                    options.append(inst)
                    index += 1
        else:
            print(f"{index}) Back (Up one level)")
            index += 1
            selected_subckt = parsed_netlist.get_subcircuit(current_cell)
            if selected_subckt:
                for inst in selected_subckt.instances:
                    if inst.reference in defined_subckts:
                        print(f"{index}) {inst.name} ({inst.reference})")
                        options.append(inst)
                        index += 1

        selection = input("Choice: ").strip()
        
        if selection.lower() == 'q':
            break

        if not selection.isdigit():
            print("Invalid selection.")
            continue
            
        selection = int(selection)
        
        if current_cell != "top" and selection == 0:
            # Go back up
            parts = current_inst_path.split(".")
            if len(parts) > 1:
                parts.pop()
                current_inst_path = ".".join(parts)
                # re-resolve current_cell
                if current_inst_path == "top":
                    current_cell = "top"
                else:
                    path_without_top = current_inst_path[4:] # remove "top."
                    inst = parsed_netlist.get_instance(path_without_top)
                    current_cell = inst.reference if inst else "top"
        else:
            # Descend
            idx = selection - 1 if current_cell != "top" else selection
            if 0 <= idx < len(options):
                chosen_inst = options[idx]
                current_cell = chosen_inst.reference
                current_inst_path = f"{current_inst_path}.{chosen_inst.name}"
            else:
                print("Invalid selection.")

if __name__ == "__main__":
    main()
