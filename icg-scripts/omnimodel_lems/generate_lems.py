import lems.api as lems
import neuroml

model = lems.Model()
model.add(lems.Dimension('voltage', m=1, l=2, t=-3, i=-1))
model.add(lems.Dimension('per_voltage', m=-1, l=-2, t=3, i=1))
model.add(lems.Dimension('per_voltage2', m=-2, l=-4, t=6, i=2))
model.add(lems.Dimension('per_voltage3', m=-3, l=-6, t=9, i=3))
model.add(lems.Dimension('time', t=1))
model.add(lems.Dimension('per_time', t=-1))
model.add(lems.Dimension('conductance', m=-1, l=-2, t=3, i=2))
model.add(lems.Dimension('current', i=1))

ss = lems.ComponentType('baseInfSM')
tau = lems.ComponentType('baseTauSM')
gate = lems.ComponentType('baseGateSM')
channel = lems.ComponentType('IonChannelSM')

model.add(ss)
model.add(tau)
model.add(gate)
model.add(channel)

ss.add(lems.Parameter('a', 'per_voltage'))
ss.add(lems.Parameter('b', 'none'))
ss.add(lems.Parameter('c', 'none'))
ss.add(lems.Parameter('d', 'none'))
ss.add(lems.Requirement('v', 'voltage'))
ss.add(lems.Exposure('qinf', 'none'))
ss.dynamics.add(lems.DerivedVariable('qinf', value='(c / (1 + exp((b - (a * v)))) + d'))

tau.add(lems.Parameter('A', 'time'))
tau.add(lems.Parameter('b1', 'per_voltage'))
tau.add(lems.Parameter('b2', 'per_voltage'))
tau.add(lems.Parameter('c1', 'per_voltage2'))
tau.add(lems.Parameter('c2', 'per_voltage2'))
tau.add(lems.Parameter('d1', 'per_voltage3'))
tau.add(lems.Parameter('d2', 'per_voltage3'))
tau.add(lems.Parameter('vh', 'voltage'))
tau.add(lems.Requirement('v', 'voltage'))
tau.add(lems.Exposure('tauq', 'time'))
tau.dynamics.add(lems.DerivedVariable('diffV', value='v-vh'))
tau.dynamics.add(lems.DerivedVariable('NegSum', value='(b1 * diffV) + (c1* diffV^2) + (d1*diffV^3)'))
tau.dynamics.add(lems.DerivedVariable('PosSum', value='(b2 * diffV) + (c2* diffV^2) + (d2*diffV^3)'))
tau.dynamics.add(lems.DerivedVariable('tauq', value='A / (exp(-NegSum) + exp(posSum))'))

gate.add(lems.Parameter('instances', 'none'))
gate.add(lems.Exposure('fcond', 'none'))
gate.add(lems.Exposure('q', 'none'))
gate.add(lems.Exposure('inf', 'none'))
gate.add(lems.Exposure('tau', 'time'))
gate.add_children(ss)
gate.add_children(tau)
gate.dynamics.add(lems.StateVariable('q', 'none', exposure='q'))
gate.dynamics.add(lems.DerivedVariable('inf', value='qinf'))
gate.dynamics.add(lems.DerivedVariable('tau', value='tauq'))
gate.dynamics.add(lems.DerivedVariable('fcond', value='q^instances'))
gate.dynamics.add(lems.TimeDerivative('q', value='(inf-q) / tau'))
# gate.dynamics.add(lems.OnStart(lems.StateAssignment('q', value='inf')))   # Fix this?

channel.add(lems.Parameter('conductance', 'conductance'))
channel.add(lems.Requirement('v', 'voltage'))
channel.add(lems.Requirement('E', 'voltage'))
channel.add(lems.Exposure('fopen', 'none'))
channel.add(lems.Exposure('g', 'conductance'))
channel.add(lems.Exposure('I', 'current'))

channel.add_children(gate)
# channel.dynamics.add(lems.DerivedVariable('fopen', value=))
channel.dynamics.add(lems.DerivedVariable('g', value='conductance * fopen * (v-E)'))
channel.dynamics.add(lems.DerivedVariable('I', value='g * (v-E)'))

            
        
