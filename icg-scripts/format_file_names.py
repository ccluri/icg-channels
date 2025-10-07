from glob import glob
import os
import pickle
import matplotlib.pyplot as plt
import numpy as np

sub_chan_folder = 'icg-channels-IH'


def compile_mod(sub_chan_folder):
    all_folders = os.listdir(os.path.join('.', sub_chan_folder))
    for folder in all_folders:
        if folder in ['.git', 'LICENSE', 'Readme.md']:
            pass
        else:
            os.chdir(sub_chan_folder + '/' + folder)
            try:
                os.system('nrnivmodl')
            except:
                print(folder)
                pass
            os.chdir('../..')
    return

                
def delete_prev_format(sub_chan_folder, cmd='*.png'):
    all_folders = os.listdir(os.path.join('.', sub_chan_folder))
    for folder in all_folders:
        if folder in ['.git', 'LICENSE', 'Readme.md']:
            pass
        else:
            os.chdir(sub_chan_folder + '/' + folder)
            stmt = 'rm ' + cmd
            os.system(stmt)
            os.chdir('../..')
    return


def HHAnalyse_files(sub_chan_folder):
    all_folders = os.listdir(os.path.join('.', sub_chan_folder))
    failed = []
    good_files = 0
    bad_files = 0

    with open(sub_chan_folder + '.pkl', 'rb') as handle:
        mega_dict = pickle.load(handle)

    for ii, folder in enumerate(all_folders):
        if folder in ['.git', 'LICENSE', 'Readme.md']:
            pass
        else:
            os.chdir(sub_chan_folder + '/' + folder)
            try:
                #if not glob('*.dat'):
                fname = glob('*.mod')[0]
                a = 'python /home/chaitanya/pyNeuroML/pyneuroml/neuron/analysis/HHanalyse.py '
                b = mega_dict[fname]['suffix']
                c = ' -modFile='+fname
                d = ' -temperature=37'
                e = ' > log.txt'
                os.system(a + b + c + d + e)
                good_files += 1
            except:
                print('Debug mode')
                # fname = glob('*.mod')[0]
                # a = 'python /home/chaitanya/pyNeuroML/pyneuroml/neuron/analysis/HHanalyse.py '
                # b = mega_dict[fname]['suffix']
                # c = ' -modFile='+fname
                # d = ' -temperature=37'
                # e = ' -v > fail_log.txt'
                # os.system(a + b + c + d)
                failed.append(folder)
                bad_files += 1
            os.chdir('../..')
            print('Doing', folder, ii)

    print('Failed files: ', failed)
    print('good files count: ', good_files)
    print('bad files count: ', bad_files)


# delete_prev_format(sub_chan_folder, '*.png')
# delete_prev_format(sub_chan_folder, '-rf x86_64')
# delete_prev_format(sub_chan_folder, '*.dat')
# compile_mod(sub_chan_folder)
HHAnalyse_files(sub_chan_folder)

