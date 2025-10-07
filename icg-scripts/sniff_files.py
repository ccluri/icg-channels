
import os
import pickle
import re
from glob import glob

from textx.exceptions import TextXSyntaxError, TextXSemanticError
from textwrap import dedent
from pynmodl.unparser import Unparser
from pynmodl.lems import mod2lems
from xml.dom import minidom
from scipy.interpolate import interp1d
import numpy as np


sample_txt = '''
TITLE HH channel
: Mel-modified Hodgkin - Huxley conductances (after Ojvind et al.)

NEURON {
	SUFFIX merasd :asdsr
	USEION na READ ena WRITE ina
	USEION k READ ek WRITE ik
	NONSPECIFIC_CURRENT il
	RANGE gnabar, gkbar, gl, el
	RANGE gna,gk
	GLOBAL inf
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

PARAMETER {
	v (mV)
	celsius = 37	(degC)
	dt (ms)

:	gnabar=.20 (mho/cm2)
:	gkbar=.12 (mho/cm2)
:	gl=.0001 (mho/cm2)
	gnabar=0.0 (mho/cm2)
	gkbar=1.0 (mho/cm2)
	gl=0 (mho/cm2)
	ena = 40 (mV)
	ek = -100 (mV)
	el = -70.0 (mV)	: steady state at v = -65 mV
}
STATE {q FROM 0 TO 1
	m h n :test_ses
g
:test 2
asds :ter
asd : t
}

BREAKPOINT {
        SOLVE states METHOD cnexp
        thegna = gbar*m*m*m*h*s
	ina = thegna * (v - ena)
        ik = erers * n**3 * (v-ek)
        g=gbar  *  (g^2)  *  h	
        ik=g  *(g)  * (v-ek)

}

ASSIGNED {
	ina (mA/cm2)
	ik (mA/cm2)
	il (mA/cm2)
	inf[3]
	gna
	gk
}
'''

regex_nrn = re.compile(r'NEURON\s*\{(\s*[\w+,]\s*)*\s\}?')
regex_state = re.compile(r'(?<=STATE)\s*\{(?P<st_txt>[^}]+)(?=\})')
regex_comment = re.compile(r'(:.*)')
regex_breakpoint = re.compile(r'(?<=BREAKPOINT)\s*\{(?P<st_txt>[^}]+)(?=\})')

def remove_comments(txt):
    clear = re.sub(regex_comment, '', txt)
    return clear


def get_states(txt):
    clear_txt = remove_comments(txt)  # Just to be sure!
    #state_grp = re.search(r'(?<=STATE)\s*\{(?P<st_txt>[^}]+)(?=\})', clear_txt)
    state_grp = regex_state.search(clear_txt)
    state_list = []
    try:
        state_txt = state_grp.group('st_txt')
        for state in re.finditer(r'(\w+)', state_txt):
            state_list.append(state.group(0))
        state_list = [x for x in state_list if x not in ['FROM', '0', 'TO', '1', 'to']]
    except AttributeError:      # No states!
        pass
    return state_list

def get_powers(txt, state):
    clear_txt = remove_comments(txt)
    bp_txt = regex_breakpoint.search(clear_txt).group()
    q = bp_txt.replace('\n', ' ').replace(' ', '').replace('**', '^').replace('*', '  *  ')
    if q.find('='+state+'  *') > -1:
        q = q.replace('='+state+'  *', '=1  *  '+state+'  *')  # dirty fix
    occr = re.findall(r'\*  ?\('+state+'\^[\d]?\)|\*  ?\('+state+'?\)|\*  '+state, q, re.MULTILINE)
    count = 0
    for ii in occr:
        k = ii.find('^')
        if k == -1:
            count += 1
        else:
            count += int(ii[k+1])
    if count == 0:
        print('Something is off, zero gates here \n' + q +'\n'+state)
    return count

def get_number_gates(txt):
    states = get_states(txt)
    print('STATES      :', states)
    gates = {}
    counts = 0
    for state in states:
        counts += get_powers(txt, state)
        gates[state] = get_powers(txt, state)
    if len(states) !=  counts:
        states_flag = 4
    else:
        states_flag = 0
    return gates, states_flag

def get_suffix(txt):
    clear_txt = remove_comments(txt)  # Just to be sure!
    #nrn_str = re.search(r'NEURON\s*\{(\s*[\w+,]\s*)*\s\}?', clear_txt).group()
    nrn_str = regex_nrn.search(clear_txt).group()
    try:
        sfx_str = re.search(r'(?<=SUFFIX)\s*(\w+)', nrn_str).group(1)
    except AttributeError:
        sfx_str = False
    return sfx_str


def gate_data(sub_channel, mega_dict):
    abs_path = os.path.abspath('.')
    all_channels = os.listdir(os.path.join('.', sub_channel))
    for channel_folder in all_channels:
        if channel_folder in ['.git', 'LICENSE', 'Readme.md']:
            pass
        else:
            os.chdir(os.path.join(abs_path, sub_channel, channel_folder))
            with open(glob('*.mod')[0]) as dummy_file:
                txt_in_mod = dummy_file.read()
            gates_dict, states_flag = get_number_gates(txt_in_mod)
            if states_flag == 4 :
                add_flag(mega_dict[channel_folder], flag=4)   # HH channels with na or k turned off types
            if len(gates_dict) == 0:
                add_flag(mega_dict[channel_folder], flag=5)   #something aweful
            mega_dict[channel_folder]['gates'] = gates_dict
    os.chdir('../..')
    return mega_dict

def dump_dict(sub_channel, mega_dict):
    with open(sub_channel+'.pkl', 'wb') as handle:
        pickle.dump(mega_dict, handle, protocol=2)
    return


def fetch_dict(sub_channel):
    with open(sub_channel+'.pkl', 'rb') as handle:
        mega_dict = pickle.load(handle)
    return mega_dict


def add_flag(channel_dict, flag):
    if 'red_flag' in channel_dict:
        if flag in channel_dict['red_flag']:
            pass
        else:
            channel_dict['red_flag'].append(flag)
    else:
        channel_dict['red_flag'] = [flag]
    return channel_dict


def clear_flags(channel_dict, flag_list):
    if 'red_flag' in channel_dict:
        for flag in flag_list:
            try:
                channel_dict['red_flag'] = list(filter((flag).__ne__, channel_dict['red_flag']))
                print('Cleared flag in channel:', flag)
            except ValueError:
                pass
    else:
        pass
    return channel_dict


def first_pass_dict(sub_channel):
    abs_path = os.path.abspath('.')
    all_channels = os.listdir(os.path.join('.', sub_channel))
    mega_dict = {}  # Default values dict of dict - to be pickled
    for channel_folder in all_channels:
        if channel_folder in ['.git', 'LICENSE', 'Readme.md']:
            pass
        else:
            mega_dict[channel_folder] = {}
            os.chdir(os.path.join(abs_path, sub_channel, channel_folder))
            with open(glob('*.mod')[0]) as dummy_file:
                txt_in_mod = dummy_file.read()
            sfx = get_suffix(txt_in_mod)
            if not sfx:
                add_flag(mega_dict[channel_folder], flag=1)
            mega_dict[channel_folder]['suffix'] = sfx
            states = get_states(txt_in_mod)
            if not states:
                add_flag(mega_dict[channel_folder], flag=2)
            if 'FROM' in states:
                add_flag(mega_dict[channel_folder], flag=3)
            mega_dict[channel_folder]['states'] = states
            HHanalyse_out = glob('*.dat')  # Output files from HHanalyse
            if not HHanalyse_out:
                mega_dict[channel_folder]['HHAnalyse'] = False
                add_flag(mega_dict[channel_folder], flag=11)
            else:
                mega_dict[channel_folder]['HHAnalyse'] = True
                if len(HHanalyse_out) == 2*len(states):
                    pass
                else:
                    add_flag(mega_dict[channel_folder], flag=19)
            os.chdir('../..')
    return mega_dict


def temperature_dependence(file1, file2):
    test_points = np.array((-80, -60, -40, -20, 0))
    eval_points = np.zeros((2, len(test_points)))
    for ii, f in enumerate([file1, file2]):
        with open(f, 'r') as handle:
            data = np.loadtxt(handle)
            x = data[:, 0]
            y = data[:, 1]
            eval_points[ii] = interp1d(x, y, kind='cubic')(test_points)
    dependence = np.mean(np.subtract(eval_points[0], eval_points[1])) > 0.1
    return dependence


def temperature_effect(sub_channel, mega_dict):
    abs_path = os.path.abspath('.')
    all_channels = os.listdir(os.path.join('.', sub_channel))
    for channel_folder in all_channels:
        if channel_folder in ['.git', 'LICENSE', 'Readme.md']:
            pass
        else:
            mega_dict[channel_folder] = clear_flags(mega_dict[channel_folder], [30, 31, 32, 33]) # reset textx type errors
            os.chdir(os.path.join(abs_path, sub_channel, channel_folder))
            states = mega_dict[channel_folder]['states']
            if states:
                temp_files = {}
                avail_temps = ['6_3', '37'] 
                for deg in avail_temps:
                    temp_list = glob('*.'+states[0]+'.tau.'+deg+'.dat')  # Output files from HHanalyse
                    if temp_list:
                        temp_files[deg]  = temp_list[0] # pick first and only file - pruned at previous step
                mega_dict[channel_folder] = clear_flags(mega_dict[channel_folder], [11])  # reset
                if not temp_files:
                    mega_dict[channel_folder]['HHAnalyse'] = False
                    mega_dict[channel_folder]['Avail Temps'] = []
                    add_flag(mega_dict[channel_folder], flag=11)
                else:
                    mega_dict[channel_folder]['HHAnalyse'] = True
                    mega_dict[channel_folder]['Avail Temps'] = list(temp_files.keys())

                if len(temp_files) >= 2:
                    temp_dependence = temperature_dependence(temp_files[avail_temps[0]],
                                                             temp_files[avail_temps[1]])
                    #print(temp_dependence, channel_folder)
                    if temp_dependence:
                        add_flag(mega_dict[channel_folder], flag=50)   # temp dependence
                    else:
                        add_flag(mega_dict[channel_folder], flag=51)   # No temp dependence
                else:
                    temp_dependence = None
                    add_flag(mega_dict[channel_folder], flag=52)   # unknown dependence - probably
                mega_dict[channel_folder]['Temp dependence'] = temp_dependence
            os.chdir('../..')
    return mega_dict

def test_pynmol_unparser(sub_channel, mega_dict):
    ''' depricated '''
    unp = Unparser().compile
    abs_path = os.path.abspath('.')
    all_channels = os.listdir(os.path.join('.', sub_channel))
    for channel_folder in all_channels:
        if channel_folder in ['.git', 'LICENSE', 'Readme.md']:
            pass
        else:
            os.chdir(os.path.join(abs_path, sub_channel, channel_folder))
            with open(glob('*.mod')[0]) as dummy_file:
                txt_in_mod = dummy_file.read()
            clean_txt = remove_comments(txt_in_mod)
            cln_txt = re.sub(r'\s+', ' ', clean_txt)
            try:
                if unp(dedent(cln_txt)) == cln_txt:
                    mega_dict[channel_folder]['unparser'] = True
                    mega_dict[channel_folder] = clear_flags(mega_dict[channel_folder], [30, 31, 32, 33])
                else:
                    mega_dict[channel_folder]['unparser'] = False
                    add_flag(mega_dict[channel_folder], flag=30)
            except AttributeError:
                mega_dict[channel_folder]['unparser'] = False
                add_flag(mega_dict[channel_folder], flag=33)
            except TextXSyntaxError:
                mega_dict[channel_folder]['unparser'] = False
                add_flag(mega_dict[channel_folder], flag=31)
            except TextXSemanticError:
                mega_dict[channel_folder]['unparser'] = False
                add_flag(mega_dict[channel_folder], flag=32)
            os.chdir('../..')
    print(sub_channel)
    return mega_dict
                
# suffix = get_suffix(sample_txt)
# states = get_states(sample_txt)
# print(states, suffix)
# print(get_powers(sample_txt, 'g'))
# print(get_powers(sample_txt, 'm'))
# print(get_powers(sample_txt, 'n'))
# print(get_powers(sample_txt, 's'))

# sub_channels = ['icg-channels-K', 'icg-channels-Na', 'icg-channels-Ca', 'icg-channels-IH', 'icg-channels-KCa'] 
# # sub_channel = 'icg-channels-K'
# for sub_channel in sub_channels:
#     #mega_dict = first_pass_dict(sub_channel)
#     mega_dict = fetch_dict(sub_channel)
#     new_dict = test_pynmol_unparser(sub_channel, mega_dict)
#     print('Done sniffing: ', sub_channel)
#     dump_dict(sub_channel, new_dict)

# sub_channels = ['icg-channels-Na','icg-channels-Ca', 'icg-channels-IH', 'icg-channels-KCa']
# sub_channels = ['icg-channels-K']
# for sub_channel in sub_channels:
#     mega_dict = fetch_dict(sub_channel)
#     new_dict =  gate_data(sub_channel, mega_dict)
#     print('Done sniffing for gates: ', sub_channel)
#     dump_dict(sub_channel, new_dict)

sub_channels = ['icg-channels-K']
for sub_channel in sub_channels:
    mega_dict = fetch_dict(sub_channel)
    print('Done sniffing for gates: ', sub_channel)
    new_dict = temperature_effect(sub_channel, mega_dict)
    dump_dict(sub_channel, new_dict)
    #print(new_dict)
# file1 = 'icg-channels-K/64229_bgka.mod/borgka.n.tau.6_3.dat'
# file2 = 'icg-channels-K/64229_bgka.mod/borgka.n.tau.37.dat'
# p  = temperature_dependence(file1, file2)
