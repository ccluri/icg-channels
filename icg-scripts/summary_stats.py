import json
import pickle
import numpy as np

json_loc = '2025_Panos/'
ics_order = ['K', 'Na', 'Ca', 'IH', 'KCa']
# ics_files = ['icg-channels-K.pkl', 'icg-channels-Na.pkl',
#              'icg-channels-Ca.pkl', 'icg-channels-IH.pkl',
#              'icg-channels-KCa.pkl']

count = 0
unique_names = 0
all_analyzed_icgids = {}
unique_icgids = {}
all_new_icgids = {}

for ff in ics_order:
    if ff == 'IH':
        ffx = 'Ih'
    else:
        ffx = ff
    filename = 'icg-channels-' + ff + '.pkl'
    json_filename = json_loc + ffx + '.json'
    all_analyzed_icgids.update({ff:[]})
    unique_icgids.update({ff:[]})
    all_new_icgids.update({ff:[]})
    with open(json_filename, 'r') as p:
        data_nodes = json.load(p)
        print(ff, ' unique :', len(data_nodes['nodes'])) 
        for nn in data_nodes['nodes']:
            unique_icgids[ff].append(int(nn['name'].split('_')[0]))
            for ix in nn['unique_ids']:
                all_new_icgids[ff].append(int(ix.split('_')[0]))
        unique_names += len(data_nodes['nodes'])
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        print(ff, ' : ', len(data))
        for nn in data:
            all_analyzed_icgids[ff].append(int(nn.split('_')[0]))
        count += len(data)
print('Total : ', count)
print('Unique :', unique_names)

for ff in ics_order:
    uni_but_not_ana = list(set(unique_icgids[ff]) - set(all_analyzed_icgids[ff]))
    print(uni_but_not_ana)
    print(ff, ' unique, but not analyzed :', len(uni_but_not_ana))

# RATES exist
count_rates = 0
for ff in ics_order:
    filename = 'icg-channels-' + ff + '.pkl'
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        channel_rates = 0
        for ii in data:
            try:
                if data[ii]['RATES']:
                    channel_rates += 1
            except KeyError:
                pass
        print(ff, '(rates) : ', channel_rates)
        count_rates += channel_rates
print('Total rates extracted : ', count_rates)

# TEMPERATURE q10tau
count_q10tau = 0
names_q10tau = []
temps = []
for ff in ics_order:
    filename = 'icg-channels-' + ff + '.pkl'
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        channel_q10tau = 0
        for ii in data:
            try:
                x_ = data[ii]['Q10_TAU']
                if not np.isclose(x_, 1, rtol=0.01) and not np.isnan(x_):
                    temps.append(x_)
                    names_q10tau.append(ii)
                    channel_q10tau += 1
            except KeyError:
                pass
        print(ff, '(temp q10tau) : ', channel_q10tau)
        count_q10tau += channel_q10tau
print('Total gates with q10tau, % :', count_q10tau, count_q10tau/count_rates)
#print(temps)  # Sanity check, should be all != 1

# TEMPERATURE q10g
count_q10g = 0
names_q10g = []
temps = []
for ff in ics_order:
    filename = 'icg-channels-' + ff + '.pkl'
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        channel_q10g = 0
        for ii in data:
            try:
                x_ = data[ii]['Q10_G']
                if not np.isclose(x_, 1, rtol=0.01) and not np.isnan(x_):
                    temps.append(x_)
                    names_q10g.append(ii)
                    channel_q10g += 1
            except KeyError:
                pass
        print(ff, '(temp q10g) : ', channel_q10g)
        count_q10g += channel_q10g
print('Total gates with q10g, % : ', count_q10g, count_q10g/count_rates)
#print(temps)  # Sanity check, should be all != 1


# TEMPERATURE q10g or qtau
q10all = set(names_q10tau + names_q10g)
print('Atleast some temp dep., % :', len(q10all), len(q10all)/count_rates )


# count states exist / gates
count_gates = 0
count_inactivating = 0
count_activating = 0
count_missing = 0
sort_these = []
states_all = []
all_good = {}
for ff in ics_order:
    filename = 'icg-channels-' + ff + '.pkl'
    all_good.update({filename:[]})
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        channel_gates = 0
        for ii in data:
            if 'RATES' in data[ii]:
                if 'ERROR_FLAGS' in data[ii]: 
                    if len(data[ii]['ERROR_FLAGS']) > 0:
                        sort_these.append(filename+ '__' + ii)
                    else:
                        if 'STATES' in data[ii]:
                            states_x = data[ii]['STATES']
                            states_all.extend(states_x)
                            for ss in states_x:
                                channel_gates += 1
                                if any(k in data[ii]['RATE_VALS_SS'] for k in [ss+'_6.3', ss]):
                                    all_good[filename].append(ii)
                                    try:
                                        ssinf = data[ii]['RATE_VALS_SS'][ss+'_6.3']
                                    except KeyError:
                                        ssinf = data[ii]['RATE_VALS_SS'][ss]
                                    if len(ssinf) > 0:
                                        if ssinf[0] <= ssinf[-1]:
                                            count_activating += 1
                                        else:
                                            count_inactivating += 1
                                    else:
                                        count_missing += 1
                                        print('missing gate', ii)
                                else:
                                    print('RATE_VALS_SS not found', ii)
                        else:
                            print('No states found', ii)
                else:
                    print('No errror flag marker', ii)
            else:
                print('No rates found', ii)
        print(ff, '(gates) : ', channel_gates)
        count_gates += channel_gates
print('Total gates : ', count_gates)
print('Total activating : ', count_activating)
print('Total inactivating : ', count_inactivating)
print('Total missing : ', count_missing)
# print(len(states_all))
# print(states_all) # sanity check

count_om = 0
for ff in ics_order:
    filename = 'icg-channels-' + ff + '.pkl'
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        channel_om = 0
        for chan in list(set(all_good[filename])):
            if 'SM1_FIT' in data[chan]:
                if data[chan]['SM1_FIT']:
                    channel_om += 1
            else:
                print('Missing Omni model', ii)
        print(ff, 'OMs :', channel_om)
        count_om += channel_om
print('Total OM, % : ', count_om, count_om/count_rates)
