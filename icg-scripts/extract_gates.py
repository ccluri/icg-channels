
import sys
import os
import subprocess
import re

from glob import glob

regex_nrn = re.compile(r'NEURON\s*\{(\s*[\w+,]\s*)*\s\}?')
regex_comment = re.compile(r'(:.*)')

def remove_comments(txt):
    clear = re.sub(regex_comment, '', txt)
    return clear

def get_suffix(txt):
    clear_txt = remove_comments(txt)  # Just to be sure!
    nrn_str = regex_nrn.search(clear_txt).group()
    try:
        sfx_str = re.search(r'(?<=SUFFIX)\s*(\w+)', nrn_str).group(1)
    except AttributeError:
        sfx_str = False
    return sfx_str

def call_subprocess(L):
    print(*L)
    result = subprocess.run(['python']+L,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE,
                            universal_newlines=True)
    with open('log.txt', 'a') as ff:
        ff.write(result.stdout)
    return result


def HHAnalyse_files(sub_chan_folder, path_to_hhanalyse,
                    ca_depd=False):
    all_folders = os.listdir(os.path.join('.', sub_chan_folder))
    failed = []
    good_files = 0
    bad_files = 0
    for ii, folder in enumerate(all_folders):
        if folder in ['.git', 'LICENSE', 'Readme.md', '.gitignore']:
            pass
        else:
            os.chdir(sub_chan_folder + '/' + folder)
            try:
                fname = glob('*.mod')[0]
                print(fname)
                with open(fname) as dummy_file:
                    txt_in_mod = dummy_file.read()
                suffix = get_suffix(txt_in_mod)
                if suffix:
                    a = path_to_hhanalyse
                    b = suffix
                    c = '-modFile='+fname
                    d = '-temperature=[6.3,23,37]'  # purposefully no spaces in list here!
                    e = '-nogui'
                    if ca_depd:
                        for caconc in [5e-5, 5e-4, 5e-3]:
                            f = '-caConc='+str(caconc)
                            result = call_subprocess([a, b, c, d, e, f])
                    else:
                        result = call_subprocess([a, b, c, d, e])
                    if result.stderr == '':
                        good_files += 1
                    else:
                        print('Something else is wrong with this ion channel')
                        failed.append(folder)
                        bad_files += 1
                else:
                    print('No suffix found for this ion channel')
                    failed.append(folder)
                    bad_files += 1
            except:
                print('Debug mode')
                failed.append(folder)
                bad_files += 1
            os.chdir('../..')
            print('Processed :', folder, ii)
    print('Failed files: ', failed)
    print('Good files count: ', good_files)
    print('Bad files count: ', bad_files)

if __name__ == '__main__':
    # 'Usage: python extract_gates.py subchan_folder'
    sub_chan_folder = sys.argv[-1]
    path_to_hhanalyse = '../../HHanalyse.py'
    if sub_chan_folder == 'icg-channels-KCa':
        ca_depd = True
    else:
        ca_depd = False
    HHAnalyse_files(sub_chan_folder,
                    path_to_hhanalyse, ca_depd)

