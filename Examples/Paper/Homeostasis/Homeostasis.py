from SORNSim.NetworkCore.Behaviour import *

class Homeostasis(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Homeostatic_Mechanism')

        target_act = self.get_init_attr('target_voltage', 0.05, neurons)

        self.max_ta = self.get_init_attr('max_ta', target_act, neurons)
        self.min_ta = self.get_init_attr('min_ta', target_act, neurons)

        self.adj_strength = -self.get_init_attr('eta_ip', 0.001, neurons)

        neurons.exhaustion = neurons.get_neuron_vec()



    def new_iteration(self, neurons):

        greater = ((neurons.voltage > self.max_ta) * -1).astype(t)
        smaller = ((neurons.voltage < self.min_ta) * 1).astype(t)

        greater *= neurons.voltage - self.max_ta
        smaller *= self.min_ta - neurons.voltage

        change = (greater + smaller) * self.adj_strength
        neurons.exhaustion += change

        neurons.voltage -= neurons.exhaustion