import sys
import os
import pickle
import re
from glob import glob
from scipy.interpolate import interp1d
from shutil import copyfile, rmtree
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

def get_states(txt, suffix, channel_type):
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
    if suffix.lower().find('hh') > -1:
        if channel_type == 'K':
            state_list = list(set(state_list).difference(set(['m', 'h'])))
        elif channel_type == 'Na':
            state_list = list(set(state_list).difference(set(['n'])))
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

def get_number_gates(txt, states):
    gates = {}
    counts = 1
    for state in states:
        counts *= get_powers(txt, state)  # checking if zero
        gates[state] = get_powers(txt, state)
    return gates, counts

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
            mega_dict[channel_folder] = clear_flags(mega_dict[channel_folder], [50, 51, 52]) # reset textx type errors
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


def create_temp_dir(filepath):
    pres_dir = os.path.abspath('.')
    temp_dir = os.path.join(pres_dir, 'temp_sniff')
    try:
        os.mkdir(temp_dir)
    except OSError:
        rmtree(temp_dir)
        os.mkdir(temp_dir)
    copyfile(filepath, os.path.join(temp_dir, 'test.mod'))
    os.chdir(temp_dir)
    os.system('nrnivmodl test.mod')
    return  pres_dir, temp_dir

def delete_dir(pres_dir, temp_dir):
    os.chdir(pres_dir)
    rmtree(temp_dir)
    return

def load_neuron(temp_dir, custom_dir, custom_files):
    pres_dir = os.path.abspath('.')
    os.chdir(temp_dir)
    from neuron import h
    for cust in custom_files:
        #os.chdir(custom_dir)
        #h('load("'+cust+'")')
        print('Loading custom files', '||'*30)
        h.load_file(cust)
    return h


def run_sim_at_temp(temp, h, channel_type, suffix, gates):
    chan_suff = {'K':'ik', 'Na':'ina', 'Ca':'ica', 'IH':'i'}[channel_type]
    erev_def = {'K': -86.7, 'Na': 50.0, 'Ca': 135.0, 'KCa': -86.7, 'IH': -45.0}[channel_type]
    erev_label = {'K':'ek', 'Na':'ena', 'Ca':'eca', 'IH':'eh'}[channel_type]
    from nrnutils import Section, Mechanism
    rr = np.sqrt(100/np.pi)
    mech = Mechanism(suffix)
    soma = Section(L=rr, diam=rr, mechanisms=[mech])
    setattr(soma, erev_label, erev_def)
    h.dt = 0.0001
    h.tstop = 1
    h.celsius = temp
    i = h.Vector()
    i_flag = False
    n_flag = False
    ws_flag = False
    try:
        i.record(eval('soma(0.5)._ref_'+chan_suff))
    except NameError:
        if chan_suff != 'ih':
            i.record(eval('soma(0.5)._ref_'+chan_suff+'_'+suffix))
        else:
            i.record(eval('soma(0.5)._ref_i_'+suffix))
    except:
        i_flag = True
    h.run()
    i_last = np.array(i)[-1]
    prod = 1.
    gval = None
    try:
        for gate, count in gates.items():
            if chan_suff != 'ih':
                gate_val = eval('soma(0.5).'+gate+'_'+suffix)
            else:
                gate_val = eval('soma.'+gate+'_'+suffix)
            prod *= gate_val**count
        vm = soma.v
        erev = eval('soma.'+erev_label)
        try:
            gval = i_last / ((vm-erev)*(prod))
        except RuntimeError:
            n_flag = True
    except:
        n_flag = True
    return gval, i_flag, n_flag
        
def fetch_gvals_curr(h ,channel_type, suffix, gates):
    i_vals = {}
    i_vals[37], i_flag, n_flag = run_sim_at_temp(37, h, channel_type, suffix, gates)
    i_vals[6.3], i_flag, n_flag = run_sim_at_temp(6.3, h, channel_type, suffix, gates)
    return i_vals, i_flag, n_flag

def fetch_gvals(h, suffix):
    neuron_items = dir(h)
    candidate = []
    for name in neuron_items:
        namel = name.lower()
        if name.endswith('_'+suffix) and namel.startswith('g'):
            if namel.find('bar') > -1 or namel.find('max') > -1:
                candidate.append(name)
    from nrnutils import Section, Mechanism
    rr = np.sqrt(100/np.pi)
    soma = Section(L=rr, diam=rr)
    mech = Mechanism(suffix)
    mech_flag = 0
    try:
        mech.insert_into(soma)
    except:
        print('Couldnt load mechanism ', '!'*30) 
        mech_flag = 1
    g_dict = {}
    for cand in candidate:
        try:
            g_dict[cand] = eval('soma(0.5).'+cand)  # When defined as range
        except:
            g_dict[cand] = eval('h.'+cand)  # Perhaps defined as a global
    return g_dict, candidate, mech_flag


if __name__ == '__main__':
    #path = ['python', 'gspecific.py', channel_type, orig_file, save_as]
    save_as = sys.argv[-1]
    filepath = sys.argv[-2]
    channel_type = sys.argv[-3]
    custom_dir = '/home/chaitanya/icg-channels-customcode'
    filename = os.path.basename(filepath)
    fname_hoc = filename.replace('.mod', '.hoc')
    #pres_dir, temp_dir = create_temp_dir(filepath)
    flags = []
    custom_files = []
    for ff in os.listdir(os.path.abspath(custom_dir)):
        if ff.endswith(fname_hoc):
            custom_files.append(os.path.join(custom_dir, ff))
    #h = load_neuron(temp_dir, custom_dir, custom_files)
    try:
        h = load_neuron(os.path.dirname(filepath), custom_dir, custom_files)
    except RuntimeError:
        flags.append(1)
    with open(filepath, 'r') as f:
        txt = f.read()
    suffix = get_suffix(txt)
    likely_gbar_str = None
    if suffix:
        g_dict, gbar_strs, mech_flag = fetch_gvals(h, suffix)
        if mech_flag == 0:
            if len(g_dict) != len(gbar_strs):
                flags.append(9) # found candidates but not their values
            if len(g_dict) == 0:
                flags.append(5)
            else:
                if len(g_dict) > 1:
                    num_nonzero = [key for key, value in g_dict.items() if value != 0.]
                    if len(num_nonzero) > 1:
                        flags.append(7)
                    else:
                        likely_gbar_str = num_nonzero[0]
                else: # g_dict is of length 1
                    likely_gbar_str = g_dict.keys()[0]
                print(g_dict, '$'*30)
                if likely_gbar_str: # For one gbar cases
                    states = get_states(txt, suffix, channel_type)
                    if len(states) == 0:
                        flags.append(3)
                    else:
                        gates, counts = get_number_gates(txt, states)
                        if counts < 1:
                            flags.append(4)
                        else:
                            print(gates, filepath)
                            i_vals, i_flag, n_flag = fetch_gvals_curr(h, channel_type, suffix, gates)
                            if i_flag :
                                flags.append(10)
                            if n_flag :
                                flags.append(6)
                            if not i_flag and not n_flag:
                                if i_vals[37] / g_dict[likely_gbar_str] > 100:
                                    flags.append(8)
                                else:
                                    print(i_vals)
                            
        else:
            flags.append(1)            
    else:
        flags.append(2)
    print(flags,  filepath, suffix, likely_gbar_str)
    print('~'*100)
    #delete_dir(pres_dir, temp_dir)
