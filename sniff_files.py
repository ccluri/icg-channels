
import os
import pickle
import re
from glob import glob

from textx.exceptions import TextXSyntaxError, TextXSemanticError
from textwrap import dedent
from pynmodl.unparser import Unparser
from pynmodl.lems import mod2lems
from xml.dom import minidom


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
STATE {q FROM 0 to 1
	m h n :test_ses
g
:test 2
asds :ter
asd : t
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
        state_list = [x for x in state_list if x not in ['FROM', '0', 'TO', '1']]
    except AttributeError:      # No states!
        pass
    return state_list


def get_suffix(txt):
    clear_txt = remove_comments(txt)  # Just to be sure!
    #nrn_str = re.search(r'NEURON\s*\{(\s*[\w+,]\s*)*\s\}?', clear_txt).group()
    nrn_str = regex_nrn.search(clear_txt).group()
    try:
        sfx_str = re.search(r'(?<=SUFFIX)\s*(\w+)', nrn_str).group(1)
    except AttributeError:
        sfx_str = False
    return sfx_str


def dump_dict(sub_channel, mega_dict):
    with open(sub_channel+'.pkl', 'wb') as handle:
        pickle.dump(mega_dict, handle, protocol=2)
    return


def add_flag(channel_dict, flag):
    if 'red_flag' in channel_dict:
        channel_dict['red_flag'].append(flag)
    else:
        channel_dict['red_flag'] = [flag]
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

def test_pynmol_unparser(sub_channel, mega_dict):
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
                else:
                    mega_dict[channel_folder]['unparser'] = False
                    add_flag(mega_dict[channel_folder], flag=30)
            except TextXSyntaxError:
                mega_dict[channel_folder]['unparser'] = False
                add_flag(mega_dict[channel_folder], flag=31)
            except TextXSemanticError:
                mega_dict[channel_folder]['unparser'] = False
                add_flag(mega_dict[channel_folder], flag=32)
            os.chdir('../..')
    return mega_dict
                
# suffix = get_suffix(sample_txt)
# states = get_states(sample_txt)
# print(states, suffix)

sub_channel = 'icg-channels-Ca'
mega_dict = first_pass_dict(sub_channel)
# with open(sub_channel+'.pkl', 'rb') as handle:
#     mega_dict = pickle.load(handle)
new_dict = test_pynmol_unparser(sub_channel, mega_dict)
dump_dict(sub_channel, new_dict)
