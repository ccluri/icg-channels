import matplotlib.pyplot as plt
from palettable.colorbrewer.qualitative import Paired_10
from cycler import cycler
import pickle
import os
import numpy as np


plt.rcParams.update({
    'xtick.labelsize': 20,
    'xtick.major.size': 10,
    'ytick.labelsize': 20,
    'ytick.major.size': 10,
    'font.size': 20,
    'axes.labelsize': 20,
    'axes.titlesize': 20,
    'legend.fontsize': 14,
    'figure.subplot.wspace': 0.4,
    'figure.subplot.hspace': 0.4,
    'figure.subplot.left': 0.1,
})

subtypes = ['K', 'Na', 'Ca', 'IH']
# subtypes = ['Ca']
channel_path = os.path.abspath('.')
error_dict = {}

tot_chans = []
tot_gates = []
for chan in subtypes:
    #with open(os.path.join(channel_path, 'icg-channels-'+chan+'.pkl'), 'rb') as f:
    with open(os.path.join(channel_path, 'gvals_'+chan+'.pkl'), 'r') as f:
        data = pickle.load(f)
    tot_chans.append(len(data))
    tot_gates.append(0)
    for key, val in data.items():
        flags = val['ERROR_FLAGS']
        if len(flags) == 0:
            tot_gates[-1] += len(val['STATES'])
        try:
            error_dict[chan].extend(flags)
        except KeyError:
            error_dict[chan] = flags
print(tot_chans, sum(tot_chans), tot_gates, sum(tot_gates), subtypes)

def error_type(error_num):
    formatted_counts = []
    for key in subtypes:
        formatted_counts.append(error_dict[key].count(error_num))
    return formatted_counts

errors_all = [error_type(1), error_type(2), error_type(3), error_type(4),
              error_type(5), error_type(6), error_type(7), error_type(8),
              error_type(9), error_type(10)]

err_np = np.array(errors_all)
err_sum = np.zeros_like(err_np)
err_sum[0, :] =  err_np[0, :]
for ii in range(1, err_np.shape[0]):
    err_sum[ii, :] = err_sum[ii-1, :] + err_np[ii, :]

print(err_np, err_sum)
errors_overall = err_sum[-1, :]
fail_ratio = [ float(errors_overall[ii]) / float(tot_chans[ii]) for ii in range(len(subtypes))]
print(tot_chans, fail_ratio)
subtypes_pass = [val + '_' + str(int(100*(1-fail_ratio[ii])))+'%' for ii, val in enumerate(subtypes)]

fig = plt.figure(figsize=(5,5))
ax = fig.gca()
ax.set_color_cycle(Paired_10.mpl_colors)

ind = np.arange(len(subtypes))
width = 0.35
bs = []
bs.append(plt.bar(ind, err_np[0], width))
for ii in range(1, err_np.shape[0]):
    bs.append(plt.bar(ind, err_np[ii], width, bottom=err_sum[ii-1]))
# p1 = plt.bar(ind, errors_all[0], width)
# p2 = plt.bar(ind, errors_all[1], width, bottom=err_np[:1, :])
# p3 = plt.bar(ind, errors_all[3], width, bottom=err_np[:2, :].sum()))
# p4 = plt.bar(ind, errors_all[4], width, bottom=errors_all[3))
# p5 = plt.bar(ind, errors_all[5], width, bottom=errors_all[4))
# p6 = plt.bar(ind, errors_all[6], width, bottom=errors_all[5))
# p7 = plt.bar(ind, errors_all[7], width, bottom=errors_all[6))
# p8 = plt.bar(ind, errors_all[8], width, bottom=errors_all[7))
plt.ylim(0, 250)
plt.ylabel('Number of channels')
plt.title('Errors in parsing')
plt.xticks(ind, subtypes_pass)
plt.legend([jj[0] for jj in bs],
           ('Mechanism', 'no Suffix', 'no States',
            '>1 Gates=0', 'no gbar in h', 'Neuron',
            'Many gBar', 'Wrong states', 'gbar != g_dict',
            '_ref_i'))
plt.show()
