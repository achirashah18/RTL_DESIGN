import json
import networkx as nx

with open("/Users/achirashah/RTLLM/_chatgpt4/t5/netlist.json") as f:
    netlist = json.load(f)

def rtl_to_graph(netlist):
    import networkx as nx
    G = nx.DiGraph()

    for mod, content in netlist["modules"].items():
        for cell_name, cell in content["cells"].items():
            G.add_node(cell_name, type=cell["type"])
            connections = cell.get("connections", {})
            for conn in connections.values():
                for connected_signal in conn:
                    G.add_edge(cell_name, str(connected_signal))

    return G

G = rtl_to_graph(netlist)
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())