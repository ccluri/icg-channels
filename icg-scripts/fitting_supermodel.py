import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
from glob import glob
from os import listdir
from os.path import isfile, isdir, join
import datetime
import time
from termcolor import colored

import re
from supermodel import *
from scipy.optimize import curve_fit
from scipy.interpolate import CubicSpline
from scipy.integrate import quad

# ## IMPORTANT: when specifying more than one fit function for steady-state or tau
# ## ss_transitions and tau_transitions: specifies how parameters of previous fit function relate to current one
# ## ss_identity and tau_identity: specifies how parameters of each fit function relate to the final one

iontype = "K"
SM_NUM = 2

if SM_NUM==1:
    ss_fit_fcn_list = [sigmoid]  # NOTE: supermodel fcns should be in the form of a list
    n_ss_params = [2]
    ss_identity = [np.arange(n_ss_params[-1])]
    tau_fit_fcn_list = [tau_fun1, tau_fun2, tau_fun3]
    n_tau_params = [4, 6, 8]
    tau_transitions = [[0, 1, 2, 4], [0, 1, 2, 3, 5, 6]]
    tau_identity = [[0, 1, 2, 5], [0, 1, 2, 3, 5, 6],
                    np.arange(n_tau_params[-1])]

elif SM_NUM==2:
    ss_fit_fcn_list = [sigmoid, modified_sigmoid]
    n_ss_params = [2, 4]
    ss_transitions = [[0, 1]]
    ss_identity = [[0, 1], np.arange(n_ss_params[-1])]
    tau_fit_fcn_list = [tau_fun1, tau_fun2, tau_fun3]
    n_tau_params = [4, 6, 8]
    tau_transitions = [[0, 1, 2, 4], [0, 1, 2, 3, 5, 6]]
    tau_identity = [[0, 1, 2, 6], [0, 1, 2, 3, 5, 6],
                    np.arange(n_tau_params[-1])]

elif SM_NUM==3:
    ss_fit_fcn_list = [sigmoid]
    n_ss_params = [2]
    ss_identity = [np.arange(n_ss_params[-1])]
    tau_fit_fcn_list = [tau_fun1, tau_fun2]
    n_tau_params = [4, 6]
    tau_transitions = [[0, 1, 2, 4]]
    tau_identity = [[0, 1, 2, 4], np.arange(n_tau_params[-1])]

elif SM_NUM==4:
    ss_fit_fcn_list = [sigmoid]
    n_ss_params = [2]
    ss_identity = [np.arange(n_ss_params[-1])]
    tau_fit_fcn_list = [tau_fun1]
    n_tau_params = [4]
    tau_identity = [np.arange(n_tau_params[-1])]

elif SM_NUM==5:
    ss_fit_fcn_list = [sigmoid]
    n_ss_params = [2]
    ss_identity = [np.arange(n_ss_params[-1])]
    tau_fit_fcn_list = [tau_fun1, tau_fun2, tau_fun3, tau_fun4]
    n_tau_params = [4, 6, 8, 10]
    tau_transitions = [[0, 1, 2, 4], [0, 1, 2, 3, 5, 6],
                       [0, 1, 2, 3, 4, 6, 7, 8]]
    tau_identity = [[0, 1, 2, 6], [0, 1, 2, 3, 6, 7], [0, 1, 2, 3, 4, 6, 7, 8],
                    np.arange(n_tau_params[-1])]


# specify directory and load data file
path = "/media/icg-channels/icg-channels-"+iontype+"/"
mod_files = [f for f in listdir(path) if isdir(join(path, f)) and 'git' not in f]
n_mod_files = len(mod_files)

# load the dict file
f = open("/media/icg-channels/icg-channels-"+iontype+".pkl","rb")
data_dict = pickle.load(f)

# immediately save a backup just in case
st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
f = open("/media/icg-channels/backup/icg-channels-"+iontype+"-"+st+".pkl",'wb')
pickle.dump(data_dict,f)

print("Running for",iontype,"models.")
print("Number of mod files: ",n_mod_files)

# specify error functions
def err1(data,fun,v,params):
    rmse = np.sqrt(np.mean((np.asarray(data)-np.asarray(fun(v, *params)))**2))
    stdev = np.std(np.asarray(data))
    return rmse / stdev

def err2(data,fun,v,params):
    P = CubicSpline(v,np.asarray(data))
    def area_diff_fun(x):
        return (P(x)-fun(x, *params))**2
    def area_fun(x):
        return P(x)**2
    x = quad(area_diff_fun,v[0],v[-1])
    x_norm = quad(area_fun,v[0],v[-1])
    return x[0] / x_norm[0]

def err3(data,fun,v,params):
    return np.linalg.norm(np.asarray(data)-np.asarray(fun(v, *params)))/np.linalg.norm(np.asarray(data))


# loop through all models and fit curves

maxfev = 20000  # maximum number of iterations for scipy nonlinear fit fcn
sm_str = "SM"+str(SM_NUM)

for i in range(n_mod_files):
    mod_name = mod_files[i]    
    rate_path = path+mod_name+"/RATES/"
    # rate_files = [f for f in listdir(rate_path) if isfile(join(rate_path, f))]
    try:
        if len(data_dict[mod_name]['ERROR_FLAGS']) == 0:
            rate_files = []
            valid_states = list(data_dict[mod_name]['GATES'].keys())
            for kk in valid_states:
                fs = glob(rate_path + '*.' + kk + '.*.dat')
                for fff in fs:
                    rate_files.append(os.path.basename(fff))

            if not data_dict[mod_name]['RATES']:
                print(colored('%d %s: rates not found.' %(i, mod_name), 'red'))
                continue

            data_dict[mod_name][sm_str+'_FIT'] = True
            data_dict[mod_name][sm_str+'_PARAMS_SS'] = {}
            data_dict[mod_name][sm_str+'_PARAMS_TAU'] = {}
            data_dict[mod_name][sm_str+'_ERROR1_SS'] = {}
            data_dict[mod_name][sm_str+'_ERROR1_TAU'] = {}
            data_dict[mod_name][sm_str+'_ERROR2_SS'] = {}
            data_dict[mod_name][sm_str+'_ERROR2_TAU'] = {}
            data_dict[mod_name][sm_str+'_ERROR3_SS'] = {}
            data_dict[mod_name][sm_str+'_ERROR3_TAU'] = {}
            data_dict[mod_name]['RATE_VALS_SS'] = {}
            data_dict[mod_name]['RATE_VALS_TAU'] = {}
            data_dict[mod_name]['RATE_VALS_V'] = {}

            # loop through all rate files in this mod directory
            for j in range(len(rate_files)):
                
                rfile = rate_files[j]
                fsplit = rfile.split(".")
                varname = fsplit[1]
                #if varname not in data_dict[mod_name]['STATES']:   # WHY!!!?
                #    data_dict[mod_name]['STATES'].append(varname)
                curve_type = fsplit[2]
                d = np.loadtxt(rate_path+rfile)
                V = d[:,0]
                rate_data = d[:,1]

                if (curve_type == 'inf'):

                    if (np.max(rate_data) < 0.1 or np.min(rate_data) < 0.0 or np.std(rate_data) < 1e-6):
                        print(colored('%d %s: weird INF for rate %s' %(i, mod_name, rfile), 'magenta'))
                        data_dict[mod_name][sm_str+'_FIT'] = False
                        data_dict[mod_name][sm_str+'_PARAMS_SS'][varname] = []
                        data_dict[mod_name][sm_str+'_ERROR1_SS'][varname] = []
                        data_dict[mod_name][sm_str+'_ERROR2_SS'][varname] = []
                        data_dict[mod_name][sm_str+'_ERROR3_SS'][varname] = []
                        data_dict[mod_name]['RATE_VALS_SS'][varname] = []
                        print('REACHING WEIRD HERE')
                        continue
                    else:
                        for k in range(len(ss_fit_fcn_list)):
                            ss_fit_fcn = ss_fit_fcn_list[k]
                            if (k==0):
                                p0 = np.random.rand(n_ss_params[k])
                                if rate_data[0] > rate_data[-1]:
                                    p0[0] *= -1.
                            else:
                                p0 = np.zeros((n_ss_params[k]))
                                p0[ss_transitions[k-1]] = popt
                            try:
                                popt, _ = curve_fit(ss_fit_fcn, V, rate_data, p0=p0, maxfev=maxfev)
                                popt_full = np.zeros((n_ss_params[-1],))
                                popt_full[ss_identity[k]] = popt
                                data_dict[mod_name][sm_str+'_PARAMS_SS'][varname] = popt_full
                                data_dict[mod_name][sm_str+'_ERROR1_SS'][varname] = err1(rate_data,ss_fit_fcn,V,popt)
                                data_dict[mod_name][sm_str+'_ERROR2_SS'][varname] = err2(rate_data,ss_fit_fcn,V,popt)
                                data_dict[mod_name][sm_str+'_ERROR3_SS'][varname] = err3(rate_data,ss_fit_fcn,V,popt)
                                print('WAAAAAAAAAAAA')
                                print(err3(rate_data,ss_fit_fcn,V,popt))
                                data_dict[mod_name]['RATE_VALS_SS'][varname] = rate_data
                                data_dict[mod_name]['RATE_VALS_V'][varname] = V

                            except RuntimeError as err:
                                print(colored('%d %s: INF runtime error for rate %s' %(i, mod_name, rfile), 'blue'))
                                data_dict[mod_name][sm_str+'_FIT'] = False
                                data_dict[mod_name][sm_str+'_PARAMS_SS'][varname] = []
                                data_dict[mod_name][sm_str+'_ERROR1_SS'][varname] = []
                                data_dict[mod_name][sm_str+'_ERROR2_SS'][varname] = []
                                data_dict[mod_name][sm_str+'_ERROR3_SS'][varname] = []
                                data_dict[mod_name]['RATE_VALS_SS'][varname] = []
                                print('RUNTIME ERRORS')
                                break

                elif (curve_type == 'tau'):

                    if (np.max(rate_data) < 0.001):
                        print(colored('%d %s: weird TAU for rate %s' %(i, mod_name, rfile), 'green'))
                        data_dict[mod_name][sm_str+'_FIT'] = False
                        data_dict[mod_name][sm_str+'_PARAMS_TAU'][varname] = []
                        data_dict[mod_name][sm_str+'_ERROR1_TAU'][varname] = []
                        data_dict[mod_name][sm_str+'_ERROR2_TAU'][varname] = []
                        data_dict[mod_name][sm_str+'_ERROR3_TAU'][varname] = []
                        data_dict[mod_name]['RATE_VALS_TAU'][varname] = []
                        continue

                    else:
                        # first fit with a straight line as a control and make sure the real fit does better
                        popt_line = np.zeros((n_tau_params[-1],))
                        popt_line[1] = np.mean(rate_data)
                        data_dict[mod_name][sm_str+'_PARAMS_TAU'][varname] = popt_line
                        data_dict[mod_name][sm_str+'_ERROR1_TAU'][varname] = err1(rate_data,tau_fit_fcn_list[-1],V,popt_line)
                        data_dict[mod_name][sm_str+'_ERROR2_TAU'][varname] = err2(rate_data,tau_fit_fcn_list[-1],V,popt_line)
                        data_dict[mod_name][sm_str+'_ERROR3_TAU'][varname] = err3(rate_data,tau_fit_fcn_list[-1],V,popt_line)
                        data_dict[mod_name]['RATE_VALS_TAU'][varname] = rate_data
                        data_dict[mod_name]['RATE_VALS_V'][varname] = V

                        # actual fitting
                        for k in range(len(tau_fit_fcn_list)):
                            tau_fit_fcn = tau_fit_fcn_list[k]
                            if (k==0):  # initialize differently for first fit
                                p0 = [V[np.argmax(rate_data)],np.mean(rate_data)] + [0]*(n_tau_params[k]-2)
                            else:       # use previous fit and zeros for new params
                                p0 = np.zeros((n_tau_params[k]))
                                p0[tau_transitions[k-1]] = popt
                            try:
                                popt, _ = curve_fit(tau_fit_fcn, V, rate_data, p0=p0, maxfev=maxfev)  
                                popt_full = np.zeros((n_tau_params[-1],))
                                popt_full[tau_identity[k]] = popt
                                # check if fit is better than line (using ERROR3, arbitrarily)
                                if (err3(rate_data,tau_fit_fcn,V,popt) < data_dict[mod_name][sm_str+'_ERROR3_TAU'][varname]):  
                                    data_dict[mod_name][sm_str+'_PARAMS_TAU'][varname] = popt_full
                                    data_dict[mod_name][sm_str+'_ERROR1_TAU'][varname] = err1(rate_data,tau_fit_fcn,V,popt)
                                    data_dict[mod_name][sm_str+'_ERROR2_TAU'][varname] = err2(rate_data,tau_fit_fcn,V,popt)
                                    data_dict[mod_name][sm_str+'_ERROR3_TAU'][varname] = err3(rate_data,tau_fit_fcn,V,popt)

                                    data_dict[mod_name]['RATE_VALS_TAU'][varname] = rate_data
                                    data_dict[mod_name]['RATE_VALS_V'][varname] = V

                            except RuntimeError as err:
                                print(colored('%d %s: TAU runtime error for rate %s' %(i, mod_name, rfile), 'cyan'))
                                data_dict[mod_name][sm_str+'_FIT'] = False
                                data_dict[mod_name][sm_str+'_PARAMS_TAU'][varname] = []
                                data_dict[mod_name][sm_str+'_ERROR1_TAU'][varname] = []
                                data_dict[mod_name][sm_str+'_ERROR2_TAU'][varname] = []
                                data_dict[mod_name][sm_str+'_ERROR3_TAU'][varname] = []
                                data_dict[mod_name]['RATE_VALS_TAU'][varname] = []
                                break
            print('%d %s: all good.' %(i, mod_name))
        else:
            print('%d %s: Fix errors first' %(i, mod_name), data_dict[mod_name]['ERROR_FLAGS'])
    except KeyError:
        print('%d %s: Error flags undefined' %(i, mod_name))

# re-save data dict, and a backup copy
st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
f = open("/media/icg-channels/backup/icg-channels-"+iontype+"-"+st+".pkl",'wb')
pickle.dump(data_dict,f)
f = open("/media/icg-channels/icg-channels-"+iontype+".pkl",'wb')
pickle.dump(data_dict,f)


# print summary results
err_num = 3
err_str = 'ERROR'+str(err_num)
ss_errors = [list(data_dict[x][sm_str+'_'+err_str+'_SS'].values()) for x in data_dict.keys() 
             if (data_dict[x]['RATES'] and data_dict[x][sm_str+'_FIT'])]
print(ss_errors)
ss_errors = [item for sublist in ss_errors for item in sublist]

tau_errors = [list(data_dict[x][sm_str+'_'+err_str+'_TAU'].values()) for x in data_dict.keys()
              if (data_dict[x]['RATES'] and data_dict[x][sm_str+'_FIT'])]
tau_errors = [item for sublist in tau_errors for item in sublist]

print('SS errors: ',np.mean(ss_errors),np.var(ss_errors))
print('TAU errors: ',np.mean(tau_errors),np.var(tau_errors))
skipped_files = [x for x in data_dict.keys() if not data_dict[x]['RATES']]
print('Nr skipped mod files: ', len(skipped_files))
nofit_files = [x for x in data_dict.keys() if (data_dict[x]['RATES'] and not data_dict[x][sm_str+'_FIT'])]
print('Nr unfitted mod files: ', len(nofit_files))
