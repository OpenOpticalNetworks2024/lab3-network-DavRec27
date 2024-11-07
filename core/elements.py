import json
from parameters import c


class Signal_information(object):

    def __init__(self, signal_power=1.0, noise_power=0.0, latency=0):
        self._signal_power = float(signal_power)
        self._noise_power = float(noise_power)
        self._latency = float(latency)
        self.path = []

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
    def __init__(self, node_specs):
        self._label = node_specs.get('label', "")
        self._position = node_specs.get('position', (0.0, 0.0))
        self._connected_nodes = node_specs.get('connections', [])
        self.successive = {}
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
        return self.successive

    @successive.setter
    def successive(self, new_successive):
        if isinstance(new_successive, dict):
            self.successive.update(new_successive)
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
        self.successive = {}

    @property
    def label(self):
        return self._label

    @property
    def length(self):
        return self.length

    @property
    def successive(self):
        return self.successive

    @successive.setter
    def successive(self, new_succ):
        if isinstance(new_succ, dict):
            self.successive.update(new_succ)
        else:
            raise ValueError("Node successive must be a dict")

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
    def __init__(self, json_file = "nodes.json"):
        with open(json_file, 'r') as f:
            self.network_data = json.load(f)

        self._nodes = {}
        self._lines = {}

# instances of all node and lines

        for label, node_data in self.network_data.items():
            node_specs ={
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
                if line_label_1 not in self._lines:
                    line_1 = Line(line_label_1, self._nodes[label], self._nodes[connected_node_label])
                    self._lines[line_label_1] = line_1

                    node.successive[line_label_1] = line_1
                    self._nodes[connected_node_label].successive[line_label_1] = line_1
                # opposite direction B->A
                line_label_2 = f"{connected_node_label}-{label}"
                if line_label_2 not in self.lines:
                    line_2 = Line(line_label_2, self._nodes[label], self._nodes[connected_node_label])
                    self._lines[line_label_2] = line_2

                    node.successive[line_label_2] = line_2
                    self._nodes[connected_node_label].successive[line_label_2] = line_2


    @property
    def nodes(self):
        return self._nodes

    @property
    def lines(self):
        return self._lines

    def draw(self):
        pass

    # find_paths: given two node labels, returns all paths that connect the 2 nodes
    # as a list of node labels. Admissible path only if cross any node at most once
    def find_paths(self, label1, label2):
        pass

    # connect function set the successive attributes of all NEs as dicts
    # each node must have dict of lines and viceversa
    def connect(self):
        pass

    # propagate signal_information through path specified in it
    # and returns the modified spectral information
    def propagate(self, signal_information):
        pass
