import pickle
import os
import sys
from glob import glob
import numpy as np

def generate_dict(sub_chan_folder,
                  ca_depd=False):
    new_dict = {}
    all_folders = os.listdir(os.path.join('.', sub_chan_folder))
    failed = []
    good_files = 0
    bad_files = 0
    for ii, folder in enumerate(all_folders):
        if folder in ['.git', 'LICENSE', 'Readme.md', '.gitignore']:
            pass
        else:
            os.chdir(os.path.join(sub_chan_folder,
                                  folder))
            fnames = glob('*.dat')
            new_dict[folder] = {'RATE_VALS_TAU' :{},
                                'RATE_VALS_SS' : {}}
            if len(fnames) > 0:
                for fname in fnames:
                    fsplit = fname.split('.')
                    varname = fsplit[1]  # m, h, n
                    if ca_depd :
                        ca_conc = fsplit[2]  # ca conc 
                        name = fsplit[3]
                        temp = fsplit[4]
                    else:
                        ca_conc = None
                        name = fsplit[2] # inf or tau
                        temp = fsplit[3] # 6(.3), 23, 37
                    d = np.loadtxt(fname)
                    vs = d[:, 1]
                    if temp == '6':
                        temp = '6.3'
                    if ca_conc is None:
                        if name == 'tau':
                            new_dict[folder]['RATE_VALS_TAU'] = new_dict[folder]['RATE_VALS_TAU'] | {varname+'_'+temp : vs}
                        else:
                            new_dict[folder]['RATE_VALS_SS'] = new_dict[folder]['RATE_VALS_SS'] | {varname+'_'+temp : vs}
                    else:
                        if name == 'tau':
                            new_dict[folder]['RATE_VALS_TAU'] = new_dict[folder]['RATE_VALS_TAU'] |{varname+'_'+
                                                                                   ca_conc+ '_' +
                                                                                   temp : vs}
                        else:
                            new_dict[folder]['RATE_VALS_SS'] = new_dict[folder]['RATE_VALS_SS'] | {varname+'_'+
                                                                                   ca_conc+ '_' +
                                                                                   temp : vs}
            os.chdir('../..')
    return new_dict
            
if __name__ == '__main__':
    # 'Usage: python extract_gates.py subchan_folder'
    sub_chan_folder = sys.argv[-1]
    if sub_chan_folder in ['icg-channels-KCa', 'icg-channels-Ca']:
        ca_depd = True
    else:
        ca_depd = False
    new_dict = generate_dict(sub_chan_folder,
                             ca_depd)
    with open(sub_chan_folder+'.pkl', 'rb') as ff:
        old_dict = pickle.load(ff)
    for ii in old_dict.keys():
        try:
            old_dict[ii]['RATE_VALS_TAU'] = old_dict[ii]['RATE_VALS_TAU'] | new_dict[ii]['RATE_VALS_TAU']
            old_dict[ii]['RATE_VALS_SS'] = old_dict[ii]['RATE_VALS_SS'] | new_dict[ii]['RATE_VALS_SS']
        except KeyError:
            old_dict[ii]['RATE_VALS_TAU'] = new_dict[ii]['RATE_VALS_TAU']
            old_dict[ii]['RATE_VALS_SS'] = new_dict[ii]['RATE_VALS_SS']
            print('$'*10, ii, 'Inconsistency')
            pass
    with open(sub_chan_folder+'.pkl', 'wb') as ff:
        pickle.dump(old_dict, ff)
