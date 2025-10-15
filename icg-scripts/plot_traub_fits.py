
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


iontypes = ["K", "Na", "Ca", "IH", "KCa"]
data_dict = {}
for ion in iontypes:
    f = open("/home/chchinta/icg-channels/icg-channels-"+ion+".pkl", "rb")
    data_dict[ion] = pickle.load(f)



# TRAUB FITS

SM_NUM = 2
sm_str = 'SM'+str(SM_NUM)
ss_fit_fcn = modified_sigmoid
tau_fit_fcn = tau_fun3

#cmap = ['#005a32','#005a32','#005a32','#005a32','#4a1486','#4a1486','#b10026','#b10026']
cmap = ['#4d9221','#4d9221','#4d9221','#4d9221','#225ea8','#225ea8','#ce1256','#ce1256','#feb24c']

# kdr, ka, km, k2,
# naf, nap
# cal, cat
# print('kdr',data_dict['K']['20756_kdr.mod']['ICG_SM2_ERROR1']['total'])
# print('ka',data_dict['K']['20756_ka.mod']['ICG_SM2_ERROR1']['total'])
# print('km',data_dict['K']['20756_km.mod']['ICG_SM2_ERROR1']['total'])
# print('k2',data_dict['K']['20756_k2.mod']['ICG_SM2_ERROR1']['total'])
# print('naf',data_dict['Na']['20756_naf.mod']['ICG_SM2_ERROR1']['total'])
# print('nap',data_dict['Na']['20756_nap.mod']['ICG_SM2_ERROR1']['total'])
# print('cat',data_dict['Ca']['20756_cat.mod']['ICG_SM2_ERROR1']['total'])
# print('cal',data_dict['Ca']['20756_cal.mod']['ICG_SM2_ERROR1']['total'])
# print('ar',data_dict['IH']['20756_ar.mod']['ICG_SM2_ERROR1']['total'])

to_plot = ['20756_kdr.mod','20756_ka.mod','20756_km.mod','20756_k2.mod',
          '20756_naf.mod','20756_nap.mod','20756_cal.mod','20756_cat.mod','20756_ar.mod']
ion_to_plot = ['K','K','K','K','Na','Na','Ca','Ca','IH']

f=plt.figure(figsize=(15,15))

for i in range(len(to_plot)):

    gates = data_dict[ion_to_plot[i]][to_plot[i]]['STATES']
    for j in range(len(gates)):
        ax=plt.subplot(9,4,4*i+2*j+1)
        rates = data_dict[ion_to_plot[i]][to_plot[i]]['RATE_VALS_SS'][gates[j]]
        v = data_dict[ion_to_plot[i]][to_plot[i]]['RATE_VALS_V'][gates[j]]
        plt.plot(v,rates,'.',c=cmap[i])
        popt = data_dict[ion_to_plot[i]][to_plot[i]][sm_str+'_PARAMS_SS'][gates[j]]
        print(popt)
        plt.plot(v, ss_fit_fcn(v, *popt), 'k--')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_title(ion_to_plot[i]  + ' ' + to_plot[i] + ' ' + gates[j] + ' inf')
        ax=plt.subplot(9,4,4*i+2*j+2)
        rates = data_dict[ion_to_plot[i]][to_plot[i]]['RATE_VALS_TAU'][gates[j]]
        v = data_dict[ion_to_plot[i]][to_plot[i]]['RATE_VALS_V'][gates[j]]
        plt.plot(v,rates,'.',c=cmap[i])
        popt = data_dict[ion_to_plot[i]][to_plot[i]][sm_str+'_PARAMS_TAU'][gates[j]]
        plt.plot(v, tau_fit_fcn(v, *popt), 'k--')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_title(ion_to_plot[i]  + ' ' + to_plot[i] + ' ' + gates[j] + ' tau')
        
plt.tight_layout()
# plt.show()
f.savefig("traub_fits.pdf")
