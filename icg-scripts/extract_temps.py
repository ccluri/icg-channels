import os
import pickle
import sys
from glob import glob
from scipy.interpolate import interp1d
import numpy as np

def dump_dict(sub_channel, data_dict):
    with open(sub_channel+'.pkl', 'wb') as handle:
        pickle.dump(data_dict, handle)
    return

def fetch_dict(sub_channel):
    with open(sub_channel+'.pkl', 'rb') as handle:
        data_dict = pickle.load(handle)
    return data_dict

def add_flag(channel_dict, flag):
    if 'ERROR_FLAGS' in channel_dict:
        if flag in channel_dict['ERROR_FLAGS']:
            pass
        else:
            channel_dict['ERROR_FLAGS'].append(flag)
    else:
        channel_dict['ERROR_FLAGS'] = [flag]
    return channel_dict

def update_dict(sub_channel):
    if sub_channel == 'icg-channels-KCa':
        fac_kca = 3*2  # three conc. inf and tau
    else:
        fac_kca = 1*2  # only inf and tau
    data_dict = fetch_dict(sub_channel)
    abs_path = os.path.abspath('.')
    for channel_folder in data_dict.keys():
        os.chdir(os.path.join(abs_path, sub_channel, channel_folder))
        try:
            states = data_dict[channel_folder]['STATES']
            HHanalyse_out = glob('*.dat')  # Output files from HHanalyse
            if not HHanalyse_out:
                data_dict[channel_folder]['RATES'] = False
                add_flag(data_dict[channel_folder], flag=11)
            elif len(HHanalyse_out) < 3*fac_kca*len(states):
                # Not all states/concs/temps recovered
                data_dict[channel_folder]['RATES'] = True
                add_flag(data_dict[channel_folder], flag=19)
                print('This channel is missing some rates', channel_folder, states)
            else:
                # everything recovered
                data_dict[channel_folder]['RATES'] = True
        except KeyError:
            data_dict[channel_folder]['RATES'] = False
            pass
        os.chdir('../..')
    return data_dict


def temperature_dependence(sub_channel, state, temps):
    eval_points = []
    for temp in temps:
        ff = glob('*.'+state+'*.tau.'+temp+'.dat')
        if sub_channel == 'icg-channels-KCa':
            ff = glob('*.'+state+'.5e-04.tau.'+temp+'.dat')
        with open(ff[0], 'r') as handle:
            data = np.loadtxt(handle)
            eval_points.append(data[:, 1])
    return eval_points


def temperature_effect(sub_channel, data_dict):
    avail_temps = ['6.3', '37']  # Order of Temp important
    abs_path = os.path.abspath('.')
    for chann in data_dict.keys():
        os.chdir(os.path.join(abs_path, sub_channel, chann))
        print('Processing : ', os.getcwd())
        if data_dict[chann]['RATES'] and 19 not in data_dict[chann]['ERROR_FLAGS'] and len(data_dict[chann]['I_VALS'])>0 :
            states = data_dict[chann]['STATES']
            eval_points = temperature_dependence(sub_channel, states[0], avail_temps)            
            tadj_tau = np.median(eval_points[0][:20] / eval_points[1][:20])
            temp_diff = (float(avail_temps[-1]) - float(avail_temps[0])) / 10
            Q10_tau = np.exp(np.log(tadj_tau) / temp_diff)
            ivals = data_dict[chann]['I_VALS']
            tadj_ratio = ivals[float(avail_temps[-1])] / ivals[float(avail_temps[0])]
            Q10_cond = np.exp(np.log(tadj_ratio) / temp_diff)
            data_dict[chann]['Q10_TAU'] = Q10_tau
            data_dict[chann]['Q10_G'] = Q10_cond
            print('Q10_tau :', Q10_tau, 'Q10_G :', Q10_cond, chann)
        else:
            print('Skipping file due to missing data')
        os.chdir('../..')
    return data_dict

if __name__ == '__main__':
    # 'Usage: python extract_temps.py subchan_folder'
    subchan = sys.argv[-1]
    data_dict = update_dict(subchan)
    data_dict = temperature_effect(subchan, data_dict)
    dump_dict(subchan, data_dict)
    print('Finished updating with temperation Q10 factors')
