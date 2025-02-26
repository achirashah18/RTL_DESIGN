
# RTL Combinational Depth Prediction

This project predicts the combinational logic depth of signals in RTL designs using Machine Learning.

## Project Structure

- `accuracy.py` → Model training and evaluation.
- `analyze.py` → Extracts fan-in, fan-out from netlist.
- `data_extraction.py` → Runs Yosys and extracts RTL features.
- `depth_prediction.py` → Predicts combinational logic depth.
- `rtl_as_graph.py` → Represents RTL as a graph.
- `dataset.csv` → Feature dataset.
- `predicted_combinational_depths.csv` → Final predicted depths.


This repository provides a Machine Learning (ML) pipeline to predict the combinational logic depth of signals in RTL (Register Transfer Level) designs. It utilizes Yosys for synthesis, ABC for logic optimization, and Python for data extraction. The extracted data (Fan-in, Fan-out, Gate count, Logic Complexity, Depth) is stored in a CSV file for training a Graph Neural Network (GNN)-based ML model.

Project Overview

This project follows a structured workflow:

Extract RTL designs from an open-source repository.
Convert RTL to a gate-level netlist using Yosys.
Identify signals for depth prediction.
Extract features (Fan-in, Fan-out, Gate count, Complexity, Depth) using Yosys and ABC.
Store extracted data in CSV (training_data.csv) for ML model training.
Train an ML model (Graph Neural Networks - GNN) for depth prediction.

Directory Structure

├── rtl_files/                      # Folder containing Verilog (.v) files
│   ├── alu.v
│   ├── adder.v
│   ├── counter.v
│   ├── ... (other RTL files)
│
├── yosys_scripts/                  # Contains Yosys scripts for synthesis
│   ├── synth.ys                     # Yosys script to automate synthesis
│   ├── netlist.json                  # Gate-level netlist extracted from Yosys
│
├── scripts/                         # Python scripts for data extraction & ML training
│   ├── extract_yosys_data.py        # Extracts gate count, logic complexity, depth
│   ├── analyze_signals.py           # Extracts Fan-in, Fan-out from netlist
│   ├── rtl_to_graph.py              # Converts netlist to graph representation
│   ├── train_model.py               # ML model training using GNNs
│
├── training_data.csv                 # Final extracted features for ML model training
├── README.md                         # This documentation file
└── requirements.txt                   # Required dependencies

Prerequisites

Ensure you have the following installed:
Yosys (for RTL synthesis)
ABC (for logic optimization)
Python 3+ with dependencies installed
Graph Neural Networks Library (PyTorch Geometric) for ML model training


Install Required Dependencies

Run the following command:
pip install -r requirements.txt

Step-by-Step Guide

1.Clone an Open-Source RTL Repository

git clone https://github.com/RTLLM.git
cd RTLLM
Find the Verilog (.v) or VHDL (.vhd) files in the repository.

2.Extract RTL Netlist Using Yosys

Run Yosys to convert RTL into a gate-level netlist:

yosys -p "read_verilog *.v; synth; stat; write_json netlist.json"
This generates netlist.json, which contains gate-level representations.

3. Identify Signals for Depth Prediction

To identify the signals:
Manually inspect RTL files to find flip-flops (always blocks).
Automate it using Pyverilog:

from pyverilog.vparser.parser import parse
ast, _ = parse(['YOUR_FILE.v'])
print(ast.show())
This extracts signals that serve as inputs to flip-flops.

4.Extract Features Using Yosys & ABC

Run this command to extract logic-depth and gate count:

yosys -p "read_verilog *.v; synth; abc -liberty NangateOpenCellLibrary_typical.lib; dretime; stat; write_json netlist.json"
Gate Count: Extracted from stat command.
Logic Complexity & Depth: Extracted from dretime timing analysis.

5. Automate Extraction with Python

Run the script to extract features and save them to CSV:

python3 scripts/data_extraction.py
This script:
Reads RTL files.
Runs Yosys synthesis.
Extracts gate count, logic depth, and complexity.
Saves the results to dataset.csv.

6.Train the ML Model (Graph Neural Networks - GNNs)

Run the training script:

python3 scripts/data_prediction.py
Uses extracted features (dataset.csv).
Trains a Graph Neural Network (GNN) for depth prediction.


Expected CSV Output

The script data_extraction.py generates dataset.csv with the following format:


Example Run

python3 scripts/extract_yosys_data.py
python3 scripts/train_model.py

Troubleshooting

1.Error: ABC Cannot Open Liberty File

Fix: Make sure your Liberty file is correct:

wget https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/master/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib
Then, update the script to use:

yosys -p "read_verilog *.v; synth; abc -liberty NangateOpenCellLibrary_typical.lib”

2.Gate Count is Zero

Fix: Ensure correct optimization steps:

yosys -p "read_verilog *.v; proc; flatten; opt; synth; stat; write_json netlist.json"




Citation

If you use this project, kindly cite:


@article{RTL_DESIGN,
  title={AI Model for RTL Depth Prediction},
  author={ACHIRA SHAH},
  year={2025},
  journal={GitHub Repository}
}
