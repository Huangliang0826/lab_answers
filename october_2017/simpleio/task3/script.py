"""
Synfirechain-like example
"""
import spynnaker8 as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import sys

runtime = 5000
p.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
nNeurons = 200  # number of neurons in each population
p.set_number_of_neurons_per_core(p.IF_curr_exp, nNeurons / 2)

cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 5.0,
                   'tau_syn_I': 5.0,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -50.0
                   }

populations = list()
projections = list()

weight_to_spike = 2.0
delay = 17

loopConnections = list()
for i in range(0, nNeurons):
    singleConnection = ((i, (i + 1) % nNeurons, weight_to_spike, delay))
    loopConnections.append(singleConnection)

injectionConnection = [(0, 0)]
spikeArray = {'spike_times': [[0]]}
populations.append(
    p.Population(nNeurons, p.IF_curr_exp(**cell_params_lif), label='pop_1'))
populations.append(
    p.Population(1, p.external_devices.SpikeInjector(
        database_notify_port_num=int(sys.argv[1])), label='inputSpikes_1'))

projections.append(p.Projection(
    populations[0], populations[0], p.FromListConnector(loopConnections),
    p.StaticSynapse(weight=weight_to_spike, delay=delay)))
projections.append(p.Projection(
    populations[1], populations[0], p.FromListConnector(injectionConnection),
    p.StaticSynapse(weight=weight_to_spike, delay=1)))

populations[0].record(['v', 'gsyn_exc', 'gsyn_inh', 'spikes'])

p.external_devices.activate_live_output_for(
    populations[0], database_notify_port_num=int(sys.argv[2]))

p.run(runtime)

# get data (could be done as one, but can be done bit by bit as well)
spikes = populations[0].get_data('spikes')

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.2, xlim=(0, runtime)),
    title="Simple synfire chain example",
    annotations="Simulated with {}".format(p.name())
)
plt.show()

p.end()
