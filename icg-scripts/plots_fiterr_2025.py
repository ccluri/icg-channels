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


# style_dict = {
#     'font.family': 'sans-serif',
#     'font.sans-serif': 'Arial',
#     'xtick.labelsize': 6,
#     'xtick.major.size': 2,
#     'xtick.major.width': 0.5,
#     'xtick.major.pad': 1,
#     'xtick.minor.size': 1,
#     'xtick.minor.width': 0.5,
#     'ytick.labelsize': 6,
#     'ytick.major.size': 2,
#     'ytick.major.width': 0.5,
#     'ytick.major.pad': 1,
#     'ytick.minor.size': 1,
#     'ytick.minor.width': 0.5,
#     'font.size': 7,
#     'axes.labelsize': 7,
#     'axes.labelpad': 1,
#     'axes.titlesize': 7,
#     'axes.titlepad': 2,
#     'legend.fontsize': 7,
#     'axes.linewidth': 0.5
# }
# plt.rcParams.update(style_dict)

rc('font', **{'family': 'serif', 'serif': ['Helvetica']})
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
rc('text', usetex=True)


iontypes = ["K", "Na", "Ca", "IH", "KCa"]
data_dict = {}
for ion in iontypes:
    f = open("/home/chchinta/icg-channels/icg-channels-"+ion+".pkl", "rb")
    data_dict[ion] = pickle.load(f)


def set_axis(ax, letter=None):
    ax.text(
        -0.05,
        1.15,
        letter,
        fontsize=16,
        weight='bold',
        transform=ax.transAxes)
    return ax    


# get all errors

SM_NUM = 2
sm_str = "SM"+str(SM_NUM)
ERR_NUM = 3
err_str = "ERROR"+str(ERR_NUM)

ss_fit_fcn = {1: sigmoid, 2: modified_sigmoid, 3: sigmoid, 4: sigmoid, 5: sigmoid}[SM_NUM]
tau_fit_fcn = {1: tau_fun3, 2: tau_fun3, 3: tau_fun2, 4: tau_fun1, 5: tau_fun4}[SM_NUM]

# chann_name = []
# ss_errors = []
tau_data = []
V_data = []
ss_data = []
for ion in data_dict.keys():
    for x in data_dict[ion].keys():  # x is chann name
        if data_dict[ion][x]['RATES'] and data_dict[ion][x][sm_str+'_FIT']:
            for gate in data_dict[ion][x]['GATES'].keys():  # FOR EACH GATE
                tau_data.append(data_dict[ion][x]['RATE_VALS_TAU'][gate])
                ss_data.append(data_dict[ion][x]['RATE_VALS_SS'][gate])
                V_data.append(data_dict[ion][x]['RATE_VALS_V'][gate])

ss_errors = [[list(data_dict[ion][x][sm_str+'_'+err_str+'_SS'].values()) for x in data_dict[ion].keys()
             if (data_dict[ion][x]['RATES'] and data_dict[ion][x][sm_str+'_FIT'])] for ion in data_dict.keys()]
ss_errors = [item2 for sublist2 in [item for sublist in ss_errors for item in sublist] for item2 in sublist2]

chann_name = [[[x+'_'+y for y in data_dict[ion][x][sm_str+'_'+err_str+'_SS'].keys()] for x in data_dict[ion].keys()
               if (data_dict[ion][x]['RATES'] and data_dict[ion][x][sm_str+'_FIT'])] for ion in data_dict.keys()]
chann_name = [item2 for sublist2 in [item for sublist in chann_name for item in sublist] for item2 in sublist2]

tau_errors = [[list(data_dict[ion][x][sm_str+'_'+err_str+'_TAU'].values()) for x in data_dict[ion].keys()
              if (data_dict[ion][x]['RATES'] and data_dict[ion][x][sm_str+'_FIT'])] for ion in data_dict.keys()]
tau_errors = [item2 for sublist2 in [item for sublist in tau_errors for item in sublist] for item2 in sublist2]

# get params and data (for plotting)
ss_popt = [[list(data_dict[ion][x][sm_str+'_PARAMS_SS'].values()) for x in data_dict[ion].keys()
           if (data_dict[ion][x]['RATES'] and data_dict[ion][x][sm_str+'_FIT'])] for ion in data_dict.keys()]
ss_popt = [item2 for sublist2 in [item for sublist in ss_popt for item in sublist] for item2 in sublist2]

tau_popt = [[list(data_dict[ion][x][sm_str+'_PARAMS_TAU'].values()) for x in data_dict[ion].keys()
            if (data_dict[ion][x]['RATES'] and data_dict[ion][x][sm_str+'_FIT'])] for ion in data_dict.keys()]
tau_popt = [item2 for sublist2 in [item for sublist in tau_popt for item in sublist] for item2 in sublist2]


# ss_data = [[list(data_dict[ion][x]['RATE_VALS_SS'].values()) for x in data_dict[ion].keys()
#            if (data_dict[ion][x]['RATES'] and data_dict[ion][x][sm_str+'_FIT'])] for ion in data_dict.keys()]
# ss_data = [item2 for sublist2 in [item for sublist in ss_data for item in sublist] for item2 in sublist2]

# tau_data = [[list(data_dict[ion][x]['RATE_VALS_TAU'].values()) for x in data_dict[ion].keys()
#             if (data_dict[ion][x]['RATES'] and data_dict[ion][x][sm_str+'_FIT'])] for ion in data_dict.keys()]
# tau_data = [item2 for sublist2 in [item for sublist in tau_data for item in sublist] for item2 in sublist2]

# V_data = [[list(data_dict[ion][x]['RATE_VALS_V'].values()) for x in data_dict[ion].keys()
#           if (data_dict[ion][x]['RATES'] and data_dict[ion][x][sm_str+'_FIT'])] for ion in data_dict.keys()]
# V_data = [item2 for sublist2 in [item for sublist in V_data for item in sublist] for item2 in sublist2]

# remove inf and nan error vals
# remove missing tau fits (why is this?)
#print(len(ss_errors), len(tau_errors), len(ss_popt), len(tau_popt), len(ss_data), len(tau_data))

to_remove = []
for i in range(len(ss_errors)):
    if np.isnan(ss_errors[i]) or (ss_errors[i] > 1e20):
        to_remove.append(i)
    if np.isnan(tau_errors[i]) or (tau_errors[i] > 1e20):
        to_remove.append(i)
    if type(tau_data[i]) != np.ndarray:
        to_remove.append(i)

print(len(to_remove), 'Removed')
        
for idx in sorted(to_remove, reverse=True):
    del ss_errors[idx]
    del tau_errors[idx]
    del ss_popt[idx]
    del tau_popt[idx]
    del ss_data[idx]
    del tau_data[idx]
    del V_data[idx]
    del chann_name[idx]

ss_errors = np.array(ss_errors)
tau_errors = np.array(tau_errors)
ss_popt = np.array(ss_popt)
tau_popt = np.array(tau_popt)
ss_data = np.array(ss_data, dtype=object)
tau_data = np.array(tau_data, dtype=object)
V_data = np.array(V_data)
ss_inds = np.flip(ss_errors.argsort(), 0)
tau_inds = np.flip(tau_errors.argsort(), 0)

print('SS errors: ', np.mean(ss_errors), np.var(ss_errors))
print('TAU errors: ', np.mean(tau_errors), np.var(tau_errors))

iontypes = ["K", "Na", "Ca", "IH", "KCa"]
for ion in iontypes:
    tot_files = len(data_dict[ion].keys())
    print('Total mod files for ' + ion + ': ', tot_files)
    skipped_files = [x for x in data_dict[ion].keys() if not data_dict[ion][x]['RATES']]
    print('Nr skipped mod files for ' + ion + ': ', len(skipped_files), 100*len(skipped_files)/tot_files)
    nofit_files = [x for x in data_dict[ion].keys() if (data_dict[ion][x]['RATES'] and not data_dict[ion][x][sm_str+'_FIT'])]
    print('Nr unfitted mod files for ' + ion + ': ', len(nofit_files), 100*len(nofit_files)/tot_files)


# FIG 2 - histogram of errors for all SS and TAU fits, along with some examples
clr1 = '#4575b4'
clr2 = '#d73027'
msize = 12
lw = 2

maxrange = 1.1*np.max(ss_errors)

#fig, axes = plt.subplots(2,2,figsize=(15,10))
#fig = plt.figure(figsize=(17, 10))
fig = plt.figure(figsize=(12, 10))
matplotlib.rcParams.update({'font.size': 14})
ax1_0 = plt.subplot2grid((7, 4), (0, 0), colspan=2, rowspan=1)
h = ax1_0.hist(ss_errors, range=(0, maxrange), bins=100, color=clr1)
plt.sca(ax1_0)
ax1_0.set_ylim([1900, 2100])
ax1_0.spines['right'].set_visible(False)
ax1_0.spines['top'].set_visible(False)
ax1_0.spines['bottom'].set_visible(False)
plt.xticks([], [])
plt.yticks(np.arange(2000, 2100, 100),
           np.arange(2000, 2100, 100))

ax1_1 = plt.subplot2grid((7, 4), (1, 0), colspan=2, rowspan=2)#,sharex=ax1_0)
h = ax1_1.hist(ss_errors, range=(0, maxrange), bins=100, color=clr1)
plt.sca(ax1_1)

plt.xlabel('Mean Squared Error (MSE)', fontsize=14)
ax1_0.set_xlim([-0.05, 1.05])
ax1_1.set_xlim([-0.05, 1.05])
ax1_1.set_xticks(np.around(np.linspace(0, 1, 6), decimals=1),
                 np.around(np.linspace(0, 1, 6), decimals=1))
plt.yticks(np.arange(0, 201, 100),
           np.arange(0, 201, 100))
ax1_1.set_ylim([0, 225])
ax1_1.spines['right'].set_visible(False)
ax1_1.spines['top'].set_visible(False)
# set_axis(ax1_0, 'A')

d = .015  # how big to make the diagonal lines in axes coordinates
# arguments to pass plot, just so we don't keep repeating them
kwargs = dict(transform=ax1_1.transAxes, color='k', clip_on=False)
ax1_1.plot((-d, d), (1-d, 1+d), **kwargs)
kwargs = dict(transform=ax1_0.transAxes, color='k', clip_on=False)
ax1_0.plot((-d, d), (-3*d, +3*d), **kwargs)

# kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
# ax2.plot((-d, +d), (1-d, 1+d), **kwargs)
# ax2.plot((-d, +d), (-d, +d), **kwargs)

    
# INF - plot the good and bad fits

(r, c) = (3, 0)
n_inds = [-1, -10, -15, -20]
n = 0
axs = []


for i in range(2):
    for j in range(2):
        ax = plt.subplot2grid((7, 4), (r, c))
        axs.append(ax)
        ind = ss_inds[n_inds[n]]
        popt = ss_popt[ind]
        data = ss_data[ind]
        V = V_data[ind]
        plt.plot(V, data, '.', label=None, c=clr1)
        plt.plot(V, ss_fit_fcn(V, *popt), 'k--',
                 label='{:.1e}'.format(float(ss_errors[ind])))
        # if r == 3 and c == 0:
        #     # plt.xlabel('mV', fontsize=14)
        #     plt.ylabel('Steady state (1)', fontsize=14)
        #  plt.title('MSE = %f' % ss_errors[ind],fontsize=14)
        plt.legend(frameon=False, loc='upper right')
        # plt.xticks(np.arange(-100, 101, 50),
        #            np.arange(-100, 101, 50))
        plt.xticks(np.arange(-100, 101, 50),
                   [])
        plt.yticks(np.linspace(0, 1, 3),
                   np.linspace(0, 1, 3))
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        n += 1
        c += 1
    r += 1
    c = 0


    
(r, c) = (5, 0)
n = 3
for i in range(2):
    for j in range(2):
        ax = plt.subplot2grid((7, 4), (r, c))
        axs.append(ax)
        ind = ss_inds[n]
        popt = ss_popt[ind]
        data = ss_data[ind]
        V = V_data[ind]
        plt.plot(V, data, '.', label=None, c=clr1)
        plt.plot(V, ss_fit_fcn(V, *popt), 'k--',
                 label='{:.1e}'.format(float(ss_errors[ind])))
        # plt.title('MSE = %f' % ss_errors[ind],fontsize=14)
        plt.legend(frameon=False, loc='upper right')
        # if r == 5 and c == 0:
        #     # plt.xlabel('mV', fontsize=14)
        #     plt.ylabel('Steady state (1)', fontsize=14)
        # plt.xticks(np.arange(-100, 101, 50),
        #            np.arange(-100, 101, 50))
        if i == 1:
            plt.xticks(np.arange(-100, 101, 50),
                       np.arange(-100, 101, 50))
        else:
            plt.xticks(np.arange(-100, 101, 50),
                       [])
        plt.yticks(np.linspace(0, int(np.max(data)*10+1)/10, 3),
                   np.linspace(0, int(np.max(data)*10+1)/10, 3))
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        n += 1
        c += 1
    r += 1
    c = 0

axs[-1].set_xlabel('Membrane potential (mV)')
axs[-2].set_xlabel('Membrane potential (mV)')
# #  TAU

maxrange = 1.1*np.max(tau_errors)

ax2_0 = plt.subplot2grid((7, 4), (0, 2), colspan=2, rowspan=1)
h = ax2_0.hist(tau_errors, range=(0, maxrange), bins=100, color=clr2)
plt.sca(ax2_0)
ax2_0.spines['right'].set_visible(False)
ax2_0.spines['top'].set_visible(False)
ax2_0.spines['bottom'].set_visible(False)
ax2_0.set_ylim([1300, 1500])
plt.xticks([], [])
plt.yticks(np.arange(1400, 1500, 100), np.arange(1400, 1500, 100))
ax2_1 = plt.subplot2grid((7, 4), (1, 2), colspan=2, rowspan=2)#,sharex=ax2_0)
h = ax2_1.hist(tau_errors, range=(0, maxrange), bins=100, color=clr2)
plt.sca(ax2_1)

plt.xlabel('Mean Squared Error (MSE)', fontsize=14)
# plt.ylabel('Number of models', fontsize=14)
plt.xticks(np.around(np.linspace(0, 1, 6), decimals=1),
           np.around(np.linspace(0, 1, 6), decimals=1))
ax2_0.set_xlim([-0.05, 1.05])
ax2_1.set_xlim([-0.05, 1.05])
plt.yticks(np.arange(0, 401, 200),
           np.arange(0, 401, 200))
ax2_1.spines['right'].set_visible(False)
ax2_1.spines['top'].set_visible(False)
ax2_1.set_ylim([0, 450])
# set_axis(ax2_0, 'D')

kwargs = dict(transform=ax2_1.transAxes, color='k', clip_on=False)
ax2_1.plot((-d, d), (1-d, 1+d), **kwargs)
kwargs = dict(transform=ax2_0.transAxes, color='k', clip_on=False)
ax2_0.plot((-d, d), (-3*d, +3*d), **kwargs)

# # TAU plot the good and bad fits

(r, c) = (3, 2)
n_inds = [-1, -150, -200, -210]
maxtick = [60, 3000, 1000, 1000]
n = 0
for i in range(2):
    for j in range(2):
        ax = plt.subplot2grid((7, 4), (r, c))
        axs.append(ax)
        ind = tau_inds[n_inds[n]]
        popt = tau_popt[ind, :]
        V = V_data[ind, :]
        data = tau_data[ind, :]
        plt.plot(V, data, '.', label=None, c=clr2)
        plt.plot(V, tau_fit_fcn(V, *popt), 'k--',
                 label='{:.1e}'.format(float(tau_errors[ind])))
        #plt.title('MSE = %f' % tau_errors[ind],fontsize=14)
        plt.legend(frameon=False, loc='upper right')
        plt.xticks(np.arange(-100, 101, 50),
                   [])
        plt.yticks(np.linspace(0, maxtick[n], 3),
                   np.linspace(0, maxtick[n], 3))
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        n += 1
        c += 1
    r += 1
    c = 2

(r, c) = (5, 2)
n_inds = [17, 19, 50, 56]
maxtick = [2500, 0.05, 0.05, 5000]
n = 0
for i in range(2):
    for j in range(2):
        ax = plt.subplot2grid((7, 4), (r, c))
        axs.append(ax)
        ind = tau_inds[n_inds[n]]
        popt = tau_popt[ind, :]
        data = tau_data[ind, :]
        V = V_data[ind, :]
        plt.plot(V, data, '.', label=None, c=clr2)
        plt.plot(V, tau_fit_fcn(V, *popt), 'k--',
                 label='{:.1e}'.format(float(tau_errors[ind])))
        #plt.title('MSE = %f' % tau_errors[ind],fontsize=14)
        plt.legend(frameon=False, loc='upper right')
        if i == 1:
            plt.xticks(np.arange(-100, 101, 50),
                       np.arange(-100, 101, 50))
        else:
            plt.xticks(np.arange(-100, 101, 50),
                       [])
        plt.yticks(np.linspace(0, maxtick[n], 3),
                   np.linspace(0, maxtick[n], 3))
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # if r == 5 and c == 2:
        #     plt.xlabel('mV', fontsize=14)
        #     plt.ylabel(r'$\tau$ (msec)', fontsize=14)
        n += 1
        c += 1
    r += 1
    c = 2
axs[-1].set_xlabel('Membrane potential (mV)')
axs[-2].set_xlabel('Membrane potential (mV)')
    
rr = plt.gcf()
rr.text(0.008, 0.98, 'A', fontsize=16, weight='bold')
rr.text(0.49, 0.98, 'E',  fontsize=16, weight='bold')
rr.text(0.008, 0.57, 'B',  fontsize=16, weight='bold')
rr.text(0.008, 0.3, 'C',  fontsize=16, weight='bold')
rr.text(0.49, 0.57, 'F',  fontsize=16, weight='bold')
rr.text(0.49, 0.3, 'G',  fontsize=16, weight='bold')

rr.text(0.5, 0.45, r'$\tau$ (ms)', rotation='vertical',
        fontsize=14)
rr.text(0.5, 0.15, r'$\tau$ (ms)', rotation='vertical',
        fontsize=14)
rr.text(0.008, 0.38, 'Steady state', rotation='vertical',
        fontsize=14)
rr.text(0.008, 0.12, 'Steady state', rotation='vertical',
        fontsize=14)

rr.text(0.008, 0.7, 'Number of models', rotation='vertical',
        fontsize=14)
rr.text(0.5, 0.7, 'Number of models', rotation='vertical',
        fontsize=14)

# set_axis(axs[0], 'B')
# set_axis(axs[4], 'C')
# set_axis(axs[8], 'E')
# set_axis(axs[12], 'F')

    
# Insets

left, bottom, width, height = [0.225, 0.7, 0.25, 0.2]
ax1in = fig.add_axes([left, bottom, width, height])
h = ax1in.hist(ss_errors, bins=np.logspace(-8, np.log10(maxrange), 100),
               color=clr1)
ax1in.set_xscale("log")
#plt.xticks([10e-9,10e-7,10e-5,10e-3,10e-1],[r'$10^{-9}$',r'$10^{-7}$',r'$10^{-5}$',r'$10^{-3}$',r'$10^{-1}$'])
plt.yticks(np.arange(0, 201, 100),
           np.arange(0, 201, 100))

left, bottom, width, height = [0.725, 0.7, 0.25, 0.2]
ax2in = fig.add_axes([left, bottom, width, height])
h = ax2in.hist(tau_errors, bins=np.logspace(-8, np.log10(maxrange), 100),
               color=clr2)
ax2in.set_xscale("log")
#plt.xticks([10e-9,10e-7,10e-5,10e-3,10e-1],[r'$10^{-9}$',r'$10^{-7}$',r'$10^{-5}$',r'$10^{-3}$',r'$10^{-1}$'])
plt.yticks(np.arange(0, 201, 100), np.arange(0, 201, 100))


#plt.title('Steady-state curves',fontsize=18)
plt.text(x=0.25, y=0.98, s='Steady-states', fontsize=16, transform=fig.transFigure,  horizontalalignment='center')
plt.text(x=0.75, y=0.98, s='Time-constants', fontsize=16, transform=fig.transFigure,  horizontalalignment='center')

plt.tight_layout()
# plt.show()
fig.savefig("fig2_manual_fit_A.pdf", bbox_inches='tight', dpi=300)
#fig.savefig("fig2_manual_fit_A.pdf", dpi=300)
