''' Used to generate a mod file out of a supermodel of ion channel'''


def append_var(var_list, var):
    return([ii+var for ii in var_list])
        

def inf_terms(var, sm_type):
    if sm_type == 'OM1':  # Difference between OM1 and OM2 is the sigmoidal fit and modified sigmoidal
        tt = append_var(['a', 'b'], var)
        eq = '1/(1 + exp(-%s*v + %s)) \n' % tuple(tt)
    elif sm_type == 'OM2':
        tt = append_var(['c', 'a', 'b', 'd'], var)
        eq = '(%s/(1 + exp(-%s*v + %s))) + %s \n' % tuple(tt)
    return eq
    

def tau_terms(var):
    '''
    third order tau curve
    '''
    f = append_var(['b1', 'vh', 'c1', 'vh', 'd1', 'vh'], var)
    f_t = 'exp(-(%s*(v-%s) + %s*(v-%s)^2 + %s*(v-%s)^3))' % tuple(f)
    s = append_var(['b2', 'vh', 'c2', 'vh', 'd2', 'vh'], var)
    s_t = 'exp((%s*(v-%s) + %s*(v-%s)^2 + %s*(v-%s)^3))' % tuple(s)
    A = append_var(['A'], var)
    eq = str(A[0]) + ' / ( ' + f_t + ' + ' + s_t + ' ) \n'
    return eq


def neuron_text(channel_name, channel_prefix, gbar_name):
    ln1 = '''NEURON\n{\n'''
    sfx = '  SUFFIX %s \n' % channel_name
    if channel_prefix != 'h':
        ln2 = '''  USEION %s READ e%s WRITE i%s \n  RANGE g, i%s, %s\n'''  % tuple([channel_prefix]*4 + [gbar_name])
        ln3 = '  GLOBAL e%s\n}' % channel_prefix
    elif channel_prefix == 'h':
        ln2 = '''  NONSPECIFIC_CURRENT i\n  RANGE %s, g\n''' % gbar_name
        ln3 = '  GLOBAL eh\n}'
    return ln1+sfx+ln2+ln3


def units_text():
    txt = '''UNITS\n{\n  (S) = (siemens)\n  (mV) = (millivolt)\n  (mA) = (milliamp)\n}'''
    return txt


def parameter_text(var_params_dict, sm_type, gbar_dict):
    # Default is OM1
    param_units = {'a': '(/mV)', 'b': '(1)',
                   'A': '(/ms)', 'vh': '(mV)',
                   'b1': '(/mV)', 'c1': '(/mV2)', 'd1': '(/mV3)',
                   'b2': '(/mV)', 'c2': '(/mV2)', 'd2': '(/mV3)'}
    if sm_type == 'OM2':
        param_units['c'] = '(1)'
        param_units['d'] = '(1)'
    
    ln = '''PARAMETER\n{\n  %s = %f (S/cm2)\n''' % (gbar_dict['name'], gbar_dict['val'])
    for var in var_params_dict.keys():
        ln += '\n'
        for param in var_params_dict[var]:
            if param != 'count':
                ln += '  '+ param+var + ' = ' + str(var_params_dict[var][param]) + '     ' + param_units[param] + ' \n'
    ln += '}'
    return ln


def assigned_text(variables, channel_prefix):
    ln = '''ASSIGNED\n{\n  v\t(mV)\n'''
    if channel_prefix != 'h':
        ln += '  e%s\t(mV)\n  i%s\t(mA/cm2)\n' % tuple([channel_prefix]*2)
    elif channel_prefix == 'h':
        ln += '  eh\t(mV)\n  i\t(mA/cm2)\n'
    ln += '  g\t(S/cm2)\n  celsius\t(degC)\n'
    for var in variables:
        varinf = var+'Inf'
        vartau = var+'Tau'
        ln += '  ' + varinf + ' \n'
        ln += '  ' + vartau + ' \n'
    ln += '}'
    return ln


def state_text(variables):
    eq = '''STATE\n{\n'''
    for var in variables:
        eq += '  ' + var + '\n'
    eq += '}'
    return eq


def breaktxt(variables, counts, channel_prefix, gbar_name):
    ln1 = '''BREAKPOINT\n{\n  SOLVE states METHOD cnexp\n'''
    eq = '  g = %s*' % gbar_name
    for ii,var in enumerate(variables):
        eq += str(var + '*')*counts[ii]
    eq = eq[:-1] + '\n'
    if channel_prefix != 'h':
        ln2 = '  i%s = g*(v-e%s)\n}' % tuple([channel_prefix]*2)
    elif channel_prefix == 'h':
        ln2 = '  i = g*(v-eh)\n}'
    return ln1+eq+ln2


def derivative_states(variables):
    ln = '''DERIVATIVE states\n{\n  rates(v)\n'''
    for var in variables:
        varinf = var+'Inf'
        vartau = var+'Tau'
        vardash = var+"'"
        ln += "  %s = (%s - %s) / %s \n" %tuple([vardash, varinf, var, vartau])
    ln += '}'
    return ln


def init_txt(variables):
    ln = '''INITIAL\n{\n  rates(v)\n'''
    for var in variables:
        varinf = var+'Inf'
        ln += '  %s = %s \n' % tuple([var, varinf])
    ln += '}'
    return ln


def procedure_text(variables, sm_type):
    eq = '''PROCEDURE rates(v(mV))\n{\n'''
    eq += '''  LOCAL qt\n  qt = q10^((celsius - temp)/10)\n'''
    bonus_tau = 'qt*'
    eq += '  UNITSOFF\n'
    eq += '\n'
    for var in variables:
        eq += '    ' + var + 'Inf = ' + inf_terms(var, sm_type)
        eq += '    ' + var + 'Tau = ' + bonus_tau + tau_terms(var)  # temp dependence is added
        eq += '\n'
    eq += '\n'
    eq += '  UNITSON\n}'
    return eq

def sanity_check(var_dict, sm_type):
    gates = list(var_dict.keys())
    try:
        for gate in gates:
            if sm_type == 'SM1':
                assert(len(var_dict[gate]) == 11)
            elif sm_type == 'SM2':
                assert(len(var_dict[gate]) == 13)
    except AssertionError:
        print('Invalid var_dict passed to the Supermodel, Pick one SM already') 
    return

def gen_modfile(channel_name, channel_prefix, var_dict, output_file, sm_type='SM1', gbar_dict={'name':'gbar','val':1.0}):
    variables = list(var_dict.keys())
    sanity_check(var_dict, sm_type)
    counts = []
    for var in variables:
        counts.append(var_dict[var]['count'])
    neuron = neuron_text(channel_name, channel_prefix, gbar_dict['name'])
    units = units_text()
    parameter =  parameter_text(var_dict, sm_type, gbar_dict)
    assigned = assigned_text(variables, channel_prefix)
    state = state_text(variables)
    breakpoint = breaktxt(variables, counts, channel_prefix, gbar_dict['name'])
    derivative = derivative_states(variables)
    init = init_txt(variables)
    procedure = procedure_text(variables, sm_type)
    all_txt = [neuron, units, parameter, assigned, state, breakpoint, derivative, init, procedure]
    with open(output_file, 'w') as h:
        h.write('\n\n'.join(all_txt))
    return


# '''
# scipy curve_fit to supermodel.py
# from 151443_Kdr.mod file at 37 deg
# inf_curve
# array([ 0.06663264, -2.53160293])

# tau_curve
# array([ -6.60352223e+01,   4.89041619e+00,   2.58502846e-02,
#          5.19379914e-05,   3.36770153e-08,   1.52242102e-02,
#          7.93154826e-05,  -2.28101929e-07])
# '''

var_dict = {'n': {'a':0.06663264, 'b':-2.53160293,
                  'A':4.89, 'vh': 66.035,
                  'b1': 0.0258, 'c1': 0.0, 'd1': 0.0,
                  'b2': 0.0152, 'c2': 0.0, 'd2': 0.0,
                  'count': 4}
            }

# '''
# icg-channels-IH/3684_htc.mod
# at 37 degC
# Sigmoidal fit for inf
# [ -0.18161953  13.62356322]

# second order fit for tau
# [ -8.00052964e+01   1.72044770e+03  -6.99598020e-02
#   -1.00140055e-06   8.85011444e-09  -1.30065202e-01
#   -3.62954959e-06  -7.71407778e-08]
# '''

var_dict_2 = {'l': {'a':-0.18161953, 'b':13.62356322,
                    'A':1720, 'vh': -80.0,
                    'b1': -0.0699, 'c1': 0.0, 'd1': 0.0,
                    'b2': -0.130, 'c2': 0.0, 'd2': 0.0,
                    'count': 1}
             }

var_dict_sm2_2 = {'l': {'a':-0.18161953, 'b':13.62356322, 'c':1., 'd':0, 
                    'A':1720, 'vh': -80.0,
                    'b1': -0.0699, 'c1': 0.0, 'd1': 0.0,
                    'b2': -0.130, 'c2': 0.0, 'd2': 0.0,
                    'count': 1}
             }

gbar_dict_0 = {'name':'gbar_test0','val':0.1111}
gbar_dict_1 = {'name':'gbar_test1','val':0.1234}
gbar_dict_2 = {'name':'gbar_test2','val':0.5678}


gen_modfile('Kdr', 'k', var_dict, 'sm_151443_Kdr.mod', gbar_dict=gbar_dict_0)
gen_modfile('htc', 'h', var_dict_2, 'sm_3684_htc.mod', gbar_dict=gbar_dict_1)
gen_modfile('htc', 'h', var_dict_sm2_2, 'sm2_3684_htc.mod', sm_type='SM2', gbar_dict=gbar_dict_2)
