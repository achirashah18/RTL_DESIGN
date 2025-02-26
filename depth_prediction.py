import os
import subprocess
import json
import networkx as nx
import joblib
import pandas as pd

# Paths
YOSYS_SCRIPT = "/Users/achirashah/Desktop/run_yosys.ys"
MODEL_FILE = "/Users/achirashah/Desktop/combinational_depth_model.pkl"
FEATURE_CSV = "/Users/achirashah/Desktop/logic_depth_dataset.csv"  # CSV contains File (RTL), Signal, Fan-in, Fan-out, Gate Count
OUTPUT_CSV = "predicted_combinational_depths.csv"  # Final results stored here

def run_yosys(verilog_file, output_json):
    """ Runs Yosys to extract the gate-level representation. """
    yosys_script = f"""
    read_verilog {verilog_file}
    synth
    write_json {output_json}
    """

    with open(YOSYS_SCRIPT, "w") as f:
        f.write(yosys_script)

    result = subprocess.run(["yosys", "-s", YOSYS_SCRIPT], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Yosys Error for {verilog_file}:\n{result.stderr}")
        return False

    return os.path.exists(output_json)


def build_logic_graph(json_report):
    """ Builds a directed graph from Yosys output. """
    if not os.path.exists(json_report):
        print(f"Error: Report file '{json_report}' not found.")
        return None

    with open(json_report, "r") as f:
        yosys_data = json.load(f)

    graph = nx.DiGraph()

    for module in yosys_data.get("modules", {}).values():
        for cell_name, cell_data in module.get("cells", {}).items():
            gate_type = cell_data["type"]
            inputs = cell_data["connections"]

            # Add nodes (logic gates)
            graph.add_node(cell_name, gate_type=gate_type)

            # Add edges (signal connections)
            for input_signal, sources in inputs.items():
                for source in sources:
                    graph.add_edge(source, cell_name)

    print(f"Nodes in graph: {len(graph.nodes)}")
    print(f"Edges in graph: {len(graph.edges)}")

    return graph


def find_combinational_depth(graph, signal_name):
    """ Finds longest combinational depth for the given signal. """
    if not graph:
        print(f"Error: No logic graph available.")
        return None

    flip_flop_outputs = [
        node for node, attrs in graph.nodes(data=True)
        if "FF" in attrs.get("gate_type", "").upper() or "REG" in attrs.get("gate_type", "").upper()
    ]

    if not flip_flop_outputs:
        print("No flip-flop outputs detected. Ensure the design has sequential elements.")
        return None

    max_depth = 0

    for start_node in flip_flop_outputs:
        try:
            if nx.has_path(graph, start_node, signal_name):
                path = nx.shortest_path(graph, start_node, signal_name)
                num_gates = sum(1 for node in path if graph.nodes[node].get("gate_type") in ["AND", "OR", "NOT", "NAND", "XOR"])
                max_depth = max(max_depth, num_gates)
        except nx.NetworkXNoPath:
            continue

    return max_depth


def predict_depth(features):
    """ Predicts combinational depth using trained ML model. """
    if not os.path.exists(MODEL_FILE):
        print(f"Error: Model file '{MODEL_FILE}' not found.")
        return None

    model = joblib.load(MODEL_FILE)
    features_df = pd.DataFrame([features], columns=["Fan-in", "Fan-out", "Gate Count"])
    return model.predict(features_df)[0]


def process_all_signals():
    """ Runs depth prediction for all signals in the CSV and stores results. """
    if not os.path.exists(FEATURE_CSV):
        print(f"Error: Feature file '{FEATURE_CSV}' not found.")
        return None

    df = pd.read_csv(FEATURE_CSV)

    # Ensure required columns exist
    required_columns = {"File", "Signal", "Fan-in", "Fan-out", "Gate Count"}
    if not required_columns.issubset(df.columns):
        print("Error: CSV file missing required columns.")
        return None

    results = []

    for _, row in df.iterrows():
        rtl_path = os.path.join("/Users/achirashah/RTLLM/_chatgpt4/t5", row["File"])  # Prefix with t5/ to get full path
        signal_name = row["Signal"]
        features = [row["Fan-in"], row["Fan-out"], row["Gate Count"]]

        print(f"\nProcessing RTL: {rtl_path}, Signal: {signal_name}...")

        json_output = f"{rtl_path}_yosys.json"

        print(f"Running Yosys for {rtl_path}...")
        if not run_yosys(rtl_path, json_output):
            print(f"Skipping {rtl_path} due to Yosys failure.")
            continue

        print("Building logic graph...")
        logic_graph = build_logic_graph(json_output)

        print(f"Finding combinational depth for signal '{signal_name}'...")
        logic_depth = find_combinational_depth(logic_graph, signal_name)

        if logic_depth is None:
            print(f"Skipping {signal_name} due to missing depth information.")
            continue

        print(f"Extracted combinational depth: {logic_depth}")

        print("Predicting final depth using AI model...")
        predicted_depth = predict_depth(features)

        print(f"Predicted Combinational Depth: {predicted_depth}")

        results.append({
            "RTL File": row["File"],
            "Signal": signal_name,
            "Extracted Depth": logic_depth,
            "Predicted Depth": predicted_depth
        })

    # Store results in CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nAll results saved to '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    process_all_signals()