import os
import sys

def compile_mod(sub_chan_folder):
    all_folders = os.listdir(os.path.join('.', sub_chan_folder))
    for folder in all_folders:
        if folder in ['.git', 'LICENSE', 'Readme.md', '.gitignore']:
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

if __name__ == '__main__':
    # 'Usage: python complile_nrn_mech.py sub_chan_folder'
    sub_chan_folder = sys.argv[-1]
    compile_mod(sub_chan_folder)

        
