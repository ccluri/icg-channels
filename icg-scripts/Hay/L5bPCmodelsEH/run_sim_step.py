from neuron import h
from matplotlib import pyplot as plt
from numpy import array, interp, arange, savez

h.load_file("stdrun.hoc")
h.load_file('Step_current_firing.hoc')
h.init()
h.run()

time_vals_orig = array(h.tvec)
time_vals = array(arange(0, time_vals_orig[-1],0.025))

vsoma = interp(time_vals, time_vals_orig, h.vvec)

savez('Step_current_firing.npz', soma=vsoma, time=time_vals)

# fig1 = plt.figure()
# ax1 = fig1.add_subplot(111)
# ax1.plot(time_vals, vsoma, label='soma')
# plt.legend()
# plt.show()
