# User Interface

If we want to controll and evaluate our model in realtime we can replace the `pyplot` functions, the `recorder` and the `simulate_iterations` with the following Code lines. Similar to the NeuronGroup, the Network_UI is also modular and consists of multiple UI_modules. We can choose them ourselfes or, like in this case, take some default_modules, which should work with most networks. One addition we have to make is to give NeuronGroup some shape with the help of the `get_squared_dim(100)` function, which returns a 10x10 grid `NeuronDimension` object. The neuron-behaviours are not affected by this. The NeuronGroup only receives some additional values like width, height, depth and the vectors x, y, z. The neurons positions can be plotted with `plt.scatter(My_Neurons.x, My_Neurons.y)`



```python
from PymoNNto.Exploration.Network_UI.TabBase import *

class MyUITab(TabBase):

    def __init__(self, title='myTab'):
        super().__init__(title)

    def add_recorder_variables(self, net_obj, Network_UI):
        #if hasattr(net_obj, 'activity'):
        Network_UI.add_recording_variable(net_obj, 'np.mean(n.voltage)', timesteps=1000)

    def initialize(self, Network_UI):
        self.my_Tab = Network_UI.Next_Tab(self.title)
        self.my_curve = Network_UI.Add_plot_curve(x_label='t', y_label='mean voltage')

    def update(self, Network_UI):
        if self.my_Tab.isVisible():
            data = Network_UI.network['np.mean(n.voltage)', 0, 'np'][-1000:]
            iterations = Network_UI.network['n.iteration', 0, 'np'][-1000:]
            self.my_curve.setData(iterations, data)

        #...
#ui_modules = [MyUITab()] + get_default_UI_modules()
#Network_UI(my_network, modules=ui_modules, ...).show()
```


![User interface example](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/UI.png)