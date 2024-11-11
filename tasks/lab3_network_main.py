import json
import numpy as np
import matplotlib.pyplot as plt
import sys
import pandas as pd
from pathlib import Path
from core.elements import Network, Signal_information, Node, Line
from core.parameters import c

# Exercise Lab3: Network

ROOT = Path(__file__).parent.parent
INPUT_FOLDER = ROOT / 'resources'
file_input = INPUT_FOLDER / 'nodes.json'

network = Network(json_file=str(file_input))

network.connect()

# Prepare lists to collect data for the DataFrame
path_list = []
latency_list = []
noise_list = []
snr_list = []

# Iterate over all possible pairs of nodes to find all paths
for node1_label in network.nodes:
    for node2_label in network.nodes:
        if node1_label != node2_label:
            paths = network.find_paths(node1_label, node2_label)

            # propagation and collection
            for path in paths:
                # signal power = 1 mW
                signal_info = Signal_information(signal_power=0.001)

                # path assignation
                signal_info.path = path

                # signal propagation
                signal_info = network.propagate(signal_info)

                # SNR
                snr = 10 * np.log10(signal_info.signal_power / signal_info.noise_power)

                # Convert path to string format "A->B->C..."
                path_str = "->".join(path)

                # Append results to lists
                path_list.append(path_str)
                latency_list.append(signal_info.latency)
                noise_list.append(signal_info.noise_power)
                snr_list.append(snr)

# pandas dataframe
df = pd.DataFrame({
    "Path": path_list,
    "Total Latency (s)": latency_list,
    "Total Noise Power (W)": noise_list,
    "SNR (dB)": snr_list
})

# Save the DataFrame to a CSV file named 'weighted_paths.csv'
output_file = INPUT_FOLDER / 'weighted_paths.csv'
df.to_csv(output_file, index=False)

# Optionally, plot the network
network.draw()

print("Network analysis completed. Results saved to 'weighted_paths.csv'.")
# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file
