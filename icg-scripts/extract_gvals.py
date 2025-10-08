''' This is used to call the sniff.py function to evaluate the gbar maximums
from a given mod file - this is  useful to run the processes quickly

This saves the output as an additional dictionary - so as to not mess with the original dictionary
Dirty way of doing things - but it works for now. Unlikely that this will be re-used.
To merge the two dictionaries - with the py2/py3 compatibility blues see merge_icg_dicts.py'''

import sys
import os
from glob import glob
import subprocess
import re

# save_as = 'False' #'gvals_'+channel_type+'.pkl'
# for sub_channel in sub_channels:
def process_subtype(sub_channel, channel_type):
    save_as = sub_channel+'.pkl'
    abs_path = os.path.abspath('.')
    try:
        os.remove(save_as)
        print('Deleting previous version')
    except:
        pass
    all_channels = os.listdir(os.path.join('.', sub_channel))
    for channel_folder in all_channels:
        if channel_folder in ['.git', 'LICENSE', 'Readme.md', '.gitignore']:
            pass
        else:
            abs_ch_folder = os.path.abspath(os.path.join('.', sub_channel, channel_folder))
            mod_files = glob(abs_ch_folder + '/*.mod')
            for mod_file in mod_files:
                if not mod_file.startswith('sm'):
                    orig_file = mod_file
            path = ['python', 'sniff.py', channel_type, orig_file, save_as]
            result = subprocess.run(path)
            #print(orig_file)

if __name__ == '__main__':
    # 'Usage: python extract_gvals.py sub_chan_folder'
    subchan_folder = sys.argv[-1]
    channel_type = subchan_folder.strip().split('-')[-1]
    process_subtype(subchan_folder, channel_type)
