from PymoNNto.Exploration.Network_UI.Basic_Tabs.sidebar_activity_module import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.sidebar_fast_forward_module import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.sidebar_save_load_module import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.multi_group_plot_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.hist_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.info_tabs import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.single_group_plot_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.stability_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.weight_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.fourier_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.partition_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.spiketrain_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.individual_weight_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.PCA_tab import *


def get_default_UI_modules(neuron_parameters=['output'], synapse_parameters=['W']):
    return [
    UI_sidebar_activity_module(1, add_color_dict={neuron_parameters[0]:(255, 255, 255)}),
    multi_group_plot_tab(neuron_parameters),#['output', 'TH', 'weight_norm_factor', 'nox', 'refractory_counter']
    spiketrain_tab(parameter=neuron_parameters[0]),
    weight_tab(weight_attrs=synapse_parameters),#, 'W_temp', 'W_stable'
    partition_tab(),
    PCA_tab(parameter=neuron_parameters[0]),
    #individual_weight_tab(),
    hist_tab(weight_attr=synapse_parameters[0]),
    single_group_plot_tab({neuron_parameters[0]:(0, 0, 0)}),#, 'excitation':(0, 0, 255), 'inhibition':(255, 0, 0), 'input_act':(255, 0, 255), 'TH':(0, 255, 0)}),
    stability_tab(parameter=neuron_parameters[0]),
    fourier_tab(parameter=neuron_parameters[0]),
    info_tab(),
    sidebar_fast_forward_module(),
    sidebar_save_load_module()
]