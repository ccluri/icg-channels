from neuron import h
from matplotlib import pyplot as plt
from numpy import array, interp, arange, savez

h.load_file("stdrun.hoc")
h.load_file('BAC_firing.hoc')
h.init()
h.run()

time_vals_orig = array(h.tvec)
time_vals = array(arange(0,600,0.025))

vsoma = interp(time_vals, time_vals_orig, h.vsoma)
vdend = interp(time_vals, time_vals_orig, h.vdend)
vdend2 = interp(time_vals, time_vals_orig, h.vdend2)


savez('BAC_firing.npz', soma=vsoma, dend=vdend, dend2=vdend2, time=time_vals)

# fig1 = plt.figure()
# ax1 = fig1.add_subplot(111)
# ax1.plot(time_vals, vsoma, label='soma')
# ax1.plot(time_vals, vdend, label='comp_high')
# ax1.plot(time_vals, vdend2, label='comp_low')
# plt.legend()
# plt.show()
