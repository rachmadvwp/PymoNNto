from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

import matplotlib.pyplot as plt
from Exploration.Visualization.Visualization_Helper import *

#from X_Experimental.Functions import *


class hist_tab():

    def __init__(self, title='hist', timesteps=1000, mask_param='Input_Mask', mask_color_add=(-100, -100, -100)):#mask_param=None #
        self.title = title
        self.timesteps = timesteps
        self.mask_param = mask_param
        if self.mask_param is not None:
            self.compiled_param = compile('n.'+self.mask_param, '<string>', 'eval')
            self.inverted_compiled_param = compile('np.invert(n.' + self.mask_param+')', '<string>', 'eval')
            self.mask_color_add = mask_color_add


    def add_recorder_variables(self, neuron_group, Network_UI):
        if hasattr(neuron_group, 'output'):
            Network_UI.add_recording_variable(neuron_group, 'n.output', self.timesteps)

    def initialize(self, Network_UI):
        self.additionaltab = Network_UI.Next_Tab(self.title)

        _, self.isi_plt = Network_UI.Add_plot_curve('neuron inter spike interval hist', True, False, legend=False, x_label='ISI', y_label='Frequency')
        _, self.net_avg_hist_plt = Network_UI.Add_plot_curve('net avg activities (1000 steps)', True, False, legend=False, x_label='average activity', y_label='Frequency')
        if self.mask_param is not None:
            _, self.input_avg_hist_plt = Network_UI.Add_plot_curve('input avg activities (1000 steps)', True, False, legend=False, x_label='average activity', y_label='Frequency')

        self.weight_hist_plots = {}
        self.net_weight_hist_plots = {}
        if self.mask_param is not None:
            self.net_inp_weight_hist_plots = {}

        for transmitter in Network_UI.transmitters:
            Network_UI.Next_H_Block()
            _, self.weight_hist_plots[transmitter] = Network_UI.Add_plot_curve(transmitter + ' weight hist', True, False, legend=False, x_label=transmitter + ' synapse size', y_label='Frequency')
            _, self.net_weight_hist_plots[transmitter] = Network_UI.Add_plot_curve(transmitter + ' network weight hist', True, False, legend=False, x_label=transmitter + ' synapse size', y_label='Frequency')
            if self.mask_param is not None:
                _, self.net_inp_weight_hist_plots[transmitter] = Network_UI.Add_plot_curve(transmitter + ' network input weight hist', True, False, legend=False, x_label=transmitter + ' synapse size', y_label='Frequency')

        #Network_UI.Next_H_Block()
        #_, self.gaba_weight_hist_plt = Network_UI.Add_plot_curve('GABA weight hist', True, False, legend=False)
        #_, self.gaba_net_weight_hist_plt = Network_UI.Add_plot_curve('GABA network weight hist', True, False, legend=False)
        #_, self.gaba_net_inp_weight_hist_plt = Network_UI.Add_plot_curve('GABA network input weight hist', True, False, legend=False)

        Network_UI.Next_H_Block()
        self.min_hist_slider = QSlider(1)  # QtCore.Horizontal
        self.min_hist_slider.setMinimum(-1)
        self.min_hist_slider.setMaximum(10)
        self.min_hist_slider.setSliderPosition(0)
        self.min_hist_slider.mouseReleaseEvent = Network_UI.static_update_func
        self.min_hist_slider.setToolTip('slide to cut away smallest weights')
        Network_UI.Add_element(self.min_hist_slider)  # , stretch=0.1

        # self.Next_H_Block()

        #def wnwi_click(event):
        #    image = get_whole_Network_weight_image(Network_UI.network[Network_UI.exc_group_name, 0], neuron_src_groups=None, individual_norm=True, exc_weight_attr='W', inh_weight_attr='W', activations=Network_UI.network[Network_UI.exc_group_name, 0].output)
        #    plt.imshow(image, interpolation="nearest")
        #    plt.show()

        #self.wnwi_btn = QPushButton('whole network weight image', Network_UI.main_window)
        #self.wnwi_btn.clicked.connect(wnwi_click)
        #Network_UI.Add_element(self.wnwi_btn)

        # self.Next_H_Block()

        # def ttp1_click(event):
        #    plot_t_vs_tp1(np.mean(np.array(self.network[self.neuron_select_group,0]['n.output', 0][-1000:]), axis=1))
        # self.ttp1_btn = QPushButton('net t vs t+1 plot (1k)', self.main_window)
        # self.ttp1_btn.clicked.connect(ttp1_click)
        # self.Add_element(self.ttp1_btn)

        # def ives_click(event):
        #    inh=np.array(self.network[self.neuron_select_group, 0]['n.inhibition', 0][-1000:])
        #    exc=np.array(self.network[self.neuron_select_group, 0]['n.excitation', 0][-1000:])
        #    inhibition_excitation_scatter(inh,exc)
        # self.ives_btn = QPushButton('net inhibition vs excitation scatter (1k)', self.main_window)
        # self.ives_btn.clicked.connect(ives_click)
        # self.Add_element(self.ives_btn)

    def update_ISI(self, Network_UI, group):
        #rec = Network_UI.rec(group, self.timesteps)
        self.neuron_act_data = group['n.output', 0, 'np'][-self.timesteps:, Network_UI.neuron_select_id]
        self.isi_plt.clear()
        y, x = np.histogram(SpikeTrain_ISI(self.neuron_act_data), bins=15)
        curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=Network_UI.neuron_select_color)
        self.isi_plt.addItem(curve)

    def update_Mean_Activity(self, Network_UI, group, input_mask, not_input_mask, net_color_input):
        #rec = Network_UI.rec(group, self.timesteps)

        self.net_avg_hist_plt.clear()
        avg_acts = np.mean(group['n.output', 0, 'np'][-self.timesteps:, not_input_mask], axis=0)  # 1000
        y, x = np.histogram(avg_acts, bins=25)
        curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=group.color)
        self.net_avg_hist_plt.addItem(curve)

        if self.mask_param is not None:
            self.input_avg_hist_plt.clear()
            if input_mask is not False:
                input_avg_acts = np.mean(group['n.output', 0, 'np'][:, input_mask], axis=0)  # 1000
                y, x = np.histogram(input_avg_acts, bins=25)
                curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=net_color_input)  # todo:make faster!
                self.input_avg_hist_plt.addItem(curve)  # todo:make faster!

    def update_Synapse_Historgrams(self, Network_UI, group, input_mask, not_input_mask, net_color_input):
        msl = self.min_hist_slider.sliderPosition() * 0.001

        for transmitter in Network_UI.transmitters:
            if self.mask_param is not None:
                self.net_inp_weight_hist_plots[transmitter].clear()
            self.net_weight_hist_plots[transmitter].clear()
            self.weight_hist_plots[transmitter].clear()

            glu_syns = group[transmitter]
            if len(glu_syns) > 0:
                GLU_syn = Network_UI.get_combined_syn_mats(glu_syns)
                if len(GLU_syn) > 0:
                    GLU_syn = GLU_syn[list(GLU_syn.keys())[0]]
                    selected_neuron_GLU_syn = GLU_syn[Network_UI.neuron_select_id]
                    # print(GLU_syn.shape, selected_neuron_GLU_syn.shape)

                    # self.hist_plt.clear()
                    # y, x = np.histogram(np.sum(GLU_syn.transpose() > (np.max(GLU_syn, axis=1) * (1 / 2)), axis=0), bins=10)
                    # curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 255))
                    # self.hist_plt.addItem(curve)

                    if input_mask is not False and self.mask_param is not None:
                        self.net_inp_weight_hist_plots[transmitter].clear()
                        y, x = np.histogram(GLU_syn[input_mask][GLU_syn[input_mask] > msl], bins=50)
                        curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=net_color_input)
                        self.net_inp_weight_hist_plots[transmitter].addItem(curve)

                    self.net_weight_hist_plots[transmitter].clear()
                    y, x = np.histogram(GLU_syn[not_input_mask][GLU_syn[not_input_mask] > msl], bins=50)
                    curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=group.color)
                    self.net_weight_hist_plots[transmitter].addItem(curve)

                    self.weight_hist_plots[transmitter].clear()
                    y, x = np.histogram(selected_neuron_GLU_syn[selected_neuron_GLU_syn > msl], bins=50)
                    curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=Network_UI.neuron_select_color)
                    self.weight_hist_plots[transmitter].addItem(curve)


    def update(self, Network_UI):
        if self.additionaltab.isVisible():

            group = Network_UI.network[Network_UI.neuron_select_group, 0]
            n=group#for eval comand

            if self.mask_param is not None and hasattr(group, self.mask_param):
                input_mask = eval(self.compiled_param)
                not_input_mask = eval(self.inverted_compiled_param)
                mca = self.mask_color_add
            else:
                input_mask = False
                not_input_mask = True
                mca = (0,0,0)

            net_color_input = np.clip([group.color[0] + mca[0], group.color[1] + mca[1], group.color[2] + mca[2], 255], 0, 255)

            if hasattr(group, 'output'):
                self.update_ISI(Network_UI, group)
                self.update_Mean_Activity(Network_UI, group, input_mask, not_input_mask, net_color_input)

            self.update_Synapse_Historgrams(Network_UI, group, input_mask, not_input_mask, net_color_input)