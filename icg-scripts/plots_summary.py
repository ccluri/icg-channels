import numpy as np
import random
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rc
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pickle
# import os
# from os import listdir
# from os.path import isfile, isdir, join

# import re
# import sys

from supermodel import *
# from scipy.optimize import curve_fit
# from scipy.interpolate import CubicSpline
# from scipy.integrate import quad

rc('font', **{'family': 'serif', 'serif': ['Helvetica']})
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
rc('text', usetex=True)


# load data

iontypes = ["K", "Na", "Ca", "IH", "KCa"]
alphabets = ['A', 'B', 'C', 'D', 'E']
data_dict = {}
for ion in iontypes:
    f = open("/home/chchinta/icg-channels/icg-channels-"+ion+".pkl", "rb")
    data_dict[ion] = pickle.load(f)

# get some nice examples of inf and tau rates from each iontype
# NOTE: assumes v array is the same for all rates


inf_examples = {}
tau_examples = {}
max_tau = 0
n_examples = 3

    
# K examples = [879 440 659]
#  [879, 440, 659]}

choose_random = False
examples_seed = {'K': 10, 'Na': 33, 'Ca': 21,
                 'IH': 7, 'KCa': 19}   # kca 20
seed = 13
max_taus = []

def set_axis(ax, letter=None):
    ax.text(
        -0.05,
        1.15,
        letter,
        fontsize=16,
        weight='bold',
        transform=ax.transAxes)
    return ax


for ion in iontypes:
    if choose_random:
        rn = np.random.default_rng(seed)
        print(seed)
    else:
        try:
            rn = np.random.default_rng(examples_seed[ion])
        except KeyError:
            print('Not finalized yet')
            rn = np.random.default_rng(seed)
            print(seed)

    inf_examples[ion] = []
    tau_examples[ion] = []

    # if ion == 'KCa':
    #     files = [f for f in data_dict[ion].keys() if (data_dict[ion][f]['RATES'])]
    # else:
    #     files = [f for f in data_dict[ion].keys() if (data_dict[ion][f]['RATES'] and data_dict[ion][f]['SM1_FIT'])]
    files = [f for f in data_dict[ion].keys() if (data_dict[ion][f]['RATES'] and data_dict[ion][f]['SM1_FIT'])]
    f_inds = rn.permutation(len(files))
    c = 0
    while (c < n_examples):
        f = files[rn.integers(0, len(files))]
        g = rn.choice(data_dict[ion][f]['STATES'])
        # if ion == 'KCa':
        #     g += '_5e-03_6.3'
        tau = data_dict[ion][f]['RATE_VALS_TAU'][g]
        if (np.array(tau).any() and data_dict[ion][f]['RATES']
            and (np.max(tau) < 200.0) and (np.max(tau) > 10.0)):
            inf_examples[ion].append(data_dict[ion][f]['RATE_VALS_SS'][g])
            tau_examples[ion].append(data_dict[ion][f]['RATE_VALS_TAU'][g])
            # if ion == 'KCa':
            #     g = g.split('_')[0]
            v = data_dict[ion][f]['RATE_VALS_V'][g]
            c += 1
    max_taus.append(int(round(np.max(np.array(tau_examples[ion]).flatten()), -1)))


for ii in f_inds[0:n_examples]:
    print(files[ii])
# graded colors for each iontype
cmap = {'K': '#4d9221',  # ['#005a32','#238443','#41ab5d','#78c679','#addd8e'],
        'Na': '#225ea8',   # ['#4a1486','#6a51a3','#807dba','#9e9ac8','#bcbddc'],
        'Ca': '#ce1256',   # ['#b10026','#e31a1c','#fc4e2a','#fd8d3c','#feb24c'],
        'IH': '#feb24c',   # ['#034e7b','#0570b0','#3690c0','#74a9cf','#a6bddb']}
        'KCa': '#3690c0'}

msize = 12
lw = 2
print(max_taus)
f = plt.figure(figsize=(12, 5))
matplotlib.rcParams.update({'font.size': 14})
gs = matplotlib.gridspec.GridSpec(2, 5)
for ii, ion in enumerate(iontypes):
    # ax = plt.subplot(1, 2, 1)
    ax = f.add_subplot(gs[0, ii])
    plt.plot(v, inf_examples[iontypes[ii]][0], c=cmap[iontypes[ii]],
             label=iontypes[ii])
    for j in range(1, n_examples):
        plt.plot(v, inf_examples[iontypes[ii]][j], c=cmap[iontypes[ii]],
                 label=None)
    # plt.legend(frameon=False)
    if ii == 0:
        plt.ylabel(r'Steady-state (1)', fontsize=14)
    # plt.xlabel('Membrane potential (mV)', fontsize=16)
    # plt.xticks(v[::10], v[::10])
    plt.yticks(np.linspace(0, 1, 3), np.linspace(0, 1, 3))
    # plt.xtick(np.linspace(0, 1, 3), np.linspace(0, 1, 3))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_title(ion + ' gates', fontsize=14)
    set_axis(ax, letter=alphabets[ii])
    # ax = plt.subplot(1, 2, 2)
    ax2 = f.add_subplot(gs[1, ii], sharex=ax)
    plt.plot(v, tau_examples[iontypes[ii]][0], c=cmap[iontypes[ii]],
             label=iontypes[ii])
    for j in range(1, n_examples):
        plt.plot(v, tau_examples[iontypes[ii]][j],
                 c=cmap[iontypes[ii]], label=None)
    # plt.legend(frameon=False)
    if ii == 0:
        plt.ylabel(r'Time constant (ms)', fontsize=14)
    plt.xlabel('Memb. potential (mV)', fontsize=14)
    # plt.xticks(v[::10], v[::10])
    plt.yticks(np.linspace(0, max_taus[ii], 3)) # , np.linspace(0, max_taus[ii], 3))
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)

plt.tight_layout()
#plt.show()
f.savefig("fig1_rate_examplesA.pdf", dpi=300)

