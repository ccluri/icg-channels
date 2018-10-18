import os
from glob import glob
import subprocess

def switch_python2():
    text = '''export PATH="/home/chaitanya/anaconda2/bin:$PATH" &
    export PATH="/home/chaitanya/neuron/nrn/py2/x86_64/bin:$PATH"  &
    export PYTHONPATH=$PYTHONPATH:$HOME/neuron/nrn/py2/lib/python2.7/site-packages'''
    os.system(text)
    return

channel_type = 'K'
sub_channels = ['icg-channels-'+channel_type]
# save_as = 'False' #'gvals_'+channel_type+'.pkl'
save_as = 'gvals_'+channel_type+'.pkl'
for sub_channel in sub_channels:
    abs_path = os.path.abspath('.')
    all_channels = os.listdir(os.path.join('.', sub_channel))
    for channel_folder in all_channels:
        if channel_folder in ['.git', 'LICENSE', 'Readme.md']:
            pass
        else:
            #print('!'*30, channel_folder)
            abs_ch_folder = os.path.abspath(os.path.join('.', sub_channel, channel_folder))
            mod_files = glob(abs_ch_folder + '/*.mod')
            for mod_file in mod_files:
                if not mod_file.startswith('sm'):
                    orig_file = mod_file
            switch_python2()
            path = ['python', 'sniff.py', channel_type, orig_file, save_as]
            subprocess.call(path)
            #print(orig_file)
