from neuron import h
from matplotlib import pyplot as plt
from numpy import array, interp, arange, savez

h.load_file("stdrun.hoc")
h.load_file('critical_frequency.hoc')
h.init()
h.run()

time_vals_orig = array(h.vsoma_t)
time_vals = array(arange(0, time_vals_orig[-1],0.025))

vsoma = interp(time_vals, time_vals_orig, h.vsoma)
vdend = interp(time_vals, time_vals_orig, h.vdend)

savez('citical_freq.npz', soma=vsoma, vdend=vdend, time=time_vals)

# fig1 = plt.figure()
# ax1 = fig1.add_subplot(111)
# ax1.plot(time_vals, vsoma, label='soma')
# ax1.plot(time_vals, vdend, label='dend')
# plt.legend()
# plt.show()
