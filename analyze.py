import json

with open("/Users/achirashah/RTLLM/_chatgpt4/t5/netlist.json", "r") as f:
    netlist = json.load(f)

def extract_fanin_fanout(netlist):
    fanin = {}
    fanout = {}

    for module_name, module_content in netlist['modules'].items():
        for cell_name, cell_data in module_content['cells'].items():
            inputs = cell_data.get('connections', {}).keys()
            outputs = cell_data.get('port_directions', {}).keys()

            for inp in inputs:
                fanin[inp] = fanin.get(inp, 0) + 1

            for out in outputs:
                fanout[out] = fanout.get(out, 0) + 1

    return fanin, fanout

fanin, fanout = extract_fanin_fanout(netlist)
print("Fan-in:", fanin)
print("Fan-out:", fanout)


