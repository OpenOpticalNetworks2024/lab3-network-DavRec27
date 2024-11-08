import json
import numpy as np
import matplotlib.pyplot as plt
from parameters import c


class Signal_information(object):

    def __init__(self, signal_power=1.0, noise_power=0.0, latency=0):
        self._signal_power = float(signal_power)
        self._noise_power = float(noise_power)
        self._latency = float(latency)
        self._path = []

    @property
    def signal_power(self):
        return self._signal_power

    def update_signal_power(self, increment):
        self._signal_power += float(increment)

    @property
    def noise_power(self):
        return self._noise_power

    @noise_power.setter
    def noise_power(self, value):
        self._noise_power = float(value)

    def update_noise_power(self, increment):
        self._noise_power += float(increment)

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, value):
        self._latency = float(value)

    def update_latency(self, increment):
        self._latency += float(increment)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path_new):
        self._path = list(path_new)

    def update_path(self, label):
        self._path.append(label)


class Node(object):
    def __init__(self, input_dict):
        self._label = input_dict.get('label', "")
        self._position = input_dict.get('position', (0.0, 0.0))
        self._connected_nodes = input_dict.get('connected_nodes', [])
        self._successive = {}
        self.signal_information = Signal_information()

    @property
    def label(self):
        return self._label

    @property
    def position(self):
        return self._position

    @property
    def connected_nodes(self):
        return self._connected_nodes

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, new_successive):
        if isinstance(new_successive, dict):
            self._successive.update(new_successive)
        else:
            raise ValueError("Node successive must be a dict")

    def propagate(self):
        if self.signal_information.path:
            current_label = self.signal_information.path[-1]
        else:
            current_label = 'start'
        self.signal_information.update_path(current_label)

        if current_label in self.successive:
            next_node = self.successive[current_label]
            next_node.propagate()


class Line(object):
    def __init__(self, label, length):
        self._label = label
        self._length = float(length)
        self._successive = {}

    @property
    def label(self):
        return self._label

    @property
    def length(self):
        return self._length

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, new_succ):
        if isinstance(new_succ, dict):
            self._successive.update(new_succ)
        else:
            raise ValueError("Node successive must be a dict of Nodes")

    def latency_generation(self):
        speed_in_fiber = 2/3 * c
        latency = float(self._length / speed_in_fiber)
        return latency

    def noise_generation(self, signal_power):
        noise = float(1e-9 * signal_power * self._length)
        return noise

    def propagate(self, signal_information):
        noise_power = self.noise_generation(signal_information.signal_power)
        signal_information.update_noise_power(noise_power)

        latency = self.latency_generation()
        signal_information.update_latency(latency)

        for next_line in self.successive.values():
            next_line.propagate(signal_information)


class Network(object):
    def __init__(self, json_file="nodes.json"):
        with open(json_file, 'r') as f:
            self.network_data = json.load(f)

        self._nodes = {}
        self._lines = {}

# instances of all node and lines

        for label, node_data in self.network_data.items():
            node_specs = {
                'label': label,
                'position': node_data['position'],
                'connections': node_data['connected_nodes']
            }
            node = Node(node_specs)
            self._nodes[label] = node
# lines
            for connected_node_label in node_data['connected_nodes']:
                # first direction A->B
                line_label_1 = f"{label}-{connected_node_label}"
                # opposite direction B->A
                line_label_2 = f"{connected_node_label}-{label}"

                # length computation
                pos1 = np.array(node_data['position'])
                pos2 = np.array(self.network_data[connected_node_label]['position'])
                length = np.linalg.norm(pos2 - pos1)

                if line_label_1 not in self._lines:
                    self._lines[line_label_1] = Line(line_label_1, length)
                    node.successive[line_label_1] = self._lines[line_label_1]

                if line_label_2 not in self._lines:
                    self._lines[line_label_2] = Line(line_label_2, length)
                    self._nodes[connected_node_label].successive[line_label_2] = self._lines[line_label_2]

    @property
    def nodes(self):
        return self._nodes

    @property
    def lines(self):
        return self._lines

    def draw(self):
        plt.figure(figsize=(8, 8))

        for label, node in self._nodes.items():
            x, y = node.position
            plt.scatter(x, y, label=label, color='red', s=100, zorder=5)
            plt.text(x, y, label, fontsize=12, ha='right', color='black')

            for line_label, line in node.successive.items():
                connected_node = line.successive.get(line_label)
                if connected_node:
                    x1, y1 = node.position
                    x2, y2 = connected_node.position
                    plt.plot([x1, x2], [y1, y2], color='black', lw=2, zorder=1)

        plt.title("Network Lab1")
        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        plt.grid(True)
        plt.axis("equal")

        plt.show()

    # find_paths: given two node labels, returns all paths that connect the 2 nodes
    # as a list of node labels. Admissible path only if cross any node at most once
    def find_paths(self, label1, label2):
        paths = []

        def dfs(current_label, destination_label, path):  # depth-first search
            path.append(current_label)

            if current_label == destination_label:
                paths.append(list(path))
            else:
                for line_label, line in self._nodes[current_label].successive.items():
                    # Extract the next node's label from the line's successive nodes
                    next_node_label = line_label.split('-')[1] if line_label.split('-')[0] == current_label else \
                        line_label.split('-')[0]

                    if next_node_label not in path:
                        dfs(next_node_label, destination_label, path)

            path.pop()
        dfs(label1, label2, [])

        return paths

    # connect function set the successive attributes of all NEs as dicts
    # each node must have dict of lines and viceversa
    def connect(self):
        for node_label, node in self._nodes.items():
            for line_label, line in self._lines.items():
                if line_label.startswith(f"{node_label}-"):
                    node.successive[line_label] = line

        for line_label, line in self._lines.items():
            node1_label, node2_label = line_label.split('-')

            line.successive = {
                node1_label: self._nodes[node1_label],
                node2_label: self._nodes[node2_label]
            }

    # propagate signal_information through path specified in it
    # and returns the modified spectral information
    def propagate(self, signal_information):
        path = signal_information.path

        for i in range(len(path) - 1):
            current_label = path[i]
            next_label = path[i + 1]

            line_label = f"{current_label}-{next_label}"

            line = self._lines.get(line_label)

            if line:
                signal_information.update_signal_power()
                signal_information.update_noise_power(line.noise_generation(signal_information.signal_power))
                signal_information.update_latency(line.latency_generation())

        return signal_information

