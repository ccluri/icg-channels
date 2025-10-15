from generate_mod import gen_modfile
import pickle

with open('supermodel_data.pickle', 'rb') as h:
    data = pickle.load(h)


channels = ['101629_naxn.mod']
for channel in channels:
    var_dict = {}
    var_dict['m'] = {}
    var_dict['m']['a'], var_dict['m']['b'] = data[channel]['INF_ACT']
    var_dict['m']['vh'], var_dict['m']['A'] = data[channel]['TAU_ACT'][0:2]
    var_dict['m']['b1'], var_dict['m']['c1'], var_dict['m']['d1'] = data[channel]['TAU_ACT'][2:5] * 1000.
    var_dict['m']['b2'], var_dict['m']['c2'], var_dict['m']['d2'] = data[channel]['TAU_ACT'][5:] * 1000.
    var_dict['m']['count'] = 3
    var_dict['h'] = {}
    var_dict['h']['a'], var_dict['h']['b'] = data[channel]['INF_INACT']
    var_dict['h']['vh'], var_dict['h']['A'] = data[channel]['TAU_INACT'][0:2]
    var_dict['h']['b1'], var_dict['h']['c1'], var_dict['h']['d1'] = data[channel]['TAU_INACT'][2:5] * 1000.
    var_dict['h']['b2'], var_dict['h']['c2'], var_dict['h']['d2'] = data[channel]['TAU_INACT'][5:] * 1000.
    var_dict['h']['count'] = 1

gen_modfile('Naxn', 'na', var_dict, 'sm_' + channel)

# params_labels = [r'$a$', r'$b$', r'$V_H$', r'$A$', r'$b_1$', r'$c_1$', r'$d_1$', r'$b_2$', r'$c_2$', r'$d_2$']

