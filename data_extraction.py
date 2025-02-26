import os
import json
import pandas as pd
import subprocess

# Folder containing the RTL files
INPUT_FOLDER = "/Users/achirashah/RTLLM/_chatgpt4/t5"
OUTPUT_CSV = "/Users/achirashah/Desktop/logic_depth_dataset.csv"

def run_yosys(verilog_file, output_json):
    """
    Runs Yosys synthesis on the given Verilog file and generates a JSON report.
    """
    if not os.path.exists(verilog_file):
        print(f"Error: Verilog file '{verilog_file}' not found.")
        return False

    yosys_script = f"""
    read_verilog {verilog_file}
    synth
    write_json {output_json}
    """

    script_name = "run_yosys.ys"
    with open(script_name, "w") as f:
        f.write(yosys_script)

    # Run Yosys
    result = subprocess.run(["yosys", "-s", script_name], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error running Yosys on {verilog_file}:\n{result.stderr}")
        return False

    if not os.path.exists(output_json):
        print(f"Error: Yosys report file '{output_json}' was not generated.")
        return False

    return True


def extract_features(json_report, filename):
    """
    Extracts fan-in, fan-out, gate count, and logic depth from Yosys JSON report.
    """
    if not os.path.exists(json_report):
        print(f"Error: Report file '{json_report}' not found.")
        return None

    with open(json_report, "r") as f:
        yosys_data = json.load(f)

    features = {"File": [], "Signal": [], "Fan-in": [], "Fan-out": [], "Gate Count": [], "Logic Depth": []}

    for module in yosys_data.get("modules", {}).values():
        for cell_name, cell_data in module.get("cells", {}).items():
            signal_name = cell_name
            gate_type = cell_data["type"]

            fan_in = len(cell_data["connections"])  # Count of input connections
            fan_out = sum(len(conns) for conns in cell_data["connections"].values())  # Total outputs

            logic_depth = fan_in * 2 if gate_type in ["AND", "OR", "NAND", "NOR"] else fan_in

            features["File"].append(filename)
            features["Signal"].append(signal_name)
            features["Fan-in"].append(fan_in)
            features["Fan-out"].append(fan_out)
            features["Gate Count"].append(len(cell_data["connections"]))
            features["Logic Depth"].append(logic_depth)

    return pd.DataFrame(features)


# ---- MAIN EXECUTION ----
all_data = []

# Ensure the folder exists
if not os.path.exists(INPUT_FOLDER):
    print(f"Error: Input folder '{INPUT_FOLDER}' not found.")
    exit()

# Iterate through all Verilog files in the folder
for file in os.listdir(INPUT_FOLDER):
    if file.endswith(".v"):  # Process only Verilog files
        verilog_path = os.path.join(INPUT_FOLDER, file)
        json_report = f"{file}_yosys.json"

        print(f"Processing: {file}")

        # Step 1: Run Yosys
        if run_yosys(verilog_path, json_report):
            # Step 2: Extract features
            data = extract_features(json_report, file)
            if data is not None:
                all_data.append(data)

# Combine all data and save to CSV
if all_data:
    final_dataset = pd.concat(all_data, ignore_index=True)
    final_dataset.to_csv(OUTPUT_CSV, index=False)
    print(f"Dataset successfully created and saved as '{OUTPUT_CSV}'.")
else:
    print("No valid data was extracted.")