NEURON
{
  SUFFIX Ca_LVAst 
  USEION ca READ eca WRITE ica 
  RANGE gCa_LVAstbar, g, ica
  GLOBAL eca
}

UNITS
{
  (S) = (siemens)
  (mV) = (millivolt)
  (mA) = (milliamp)
}

PARAMETER
{
  gCa_LVAstbar = 0.00001 (S/cm2)

  am = 0.1666663364477572     (/mV) 
  bm = -6.666648000384755     (1) 
  cm = 1.000000095432488     (1) 
  dm = -1.0424538542655167e-07     (1) 
  vhm = -50.3304168843984     (mV) 
  Am = 16.661235913003388     (/ms) 
  b1m = 0.0638924029646585     (/mV) 
  c1m = 0.001963653224152778     (/mV2) 
  d1m = 1.934011384576897e-05     (/mV3) 
  b2m = 0.09066907482947975     (/mV) 
  c2m = -0.0010504902317461874     (/mV2) 
  d2m = 3.7129746181257e-06     (/mV3) 

  ah = -0.15624949058402665     (/mV) 
  bh = 14.062464348786175     (1) 
  ch = 0.9999846471082863     (1) 
  dh = 1.9030188138486538e-08     (1) 
  vhh = -74.23461818319801     (mV) 
  Ah = 46.57223439504385     (/ms) 
  b1h = -0.05983580987792313     (/mV) 
  c1h = 0.0005642746849123131     (/mV2) 
  d1h = -1.6553740591666873e-06     (/mV3) 
  b2h = -0.060445304185541775     (/mV) 
  c2h = -0.0025923743254568214     (/mV2) 
  d2h = -4.511046564421266e-05     (/mV3) 
}

ASSIGNED
{
  v	(mV)
  eca	(mV)
  ica	(mA/cm2)
  g	(S/cm2)
  celsius	(degC)
  mInf 
  mTau 
  hInf 
  hTau 
}

STATE
{
  m
  h
}

BREAKPOINT
{
  SOLVE states METHOD cnexp
  g = gCa_LVAstbar*m*m*h
  ica = g*(v-eca)
}

DERIVATIVE states
{
  rates(v)
  m' = (mInf - m) / mTau 
  h' = (hInf - h) / hTau 
}

INITIAL
{
  rates(v)
  m = mInf 
  h = hInf 
}

PROCEDURE rates(v(mV))
{
  UNITSOFF

    mInf = (cm/(1 + exp(-am*v + bm))) + dm 
    mTau = Am / ( exp(-(b1m*(v-vhm) + c1m*(v-vhm)^2 + d1m*(v-vhm)^3)) + exp((b2m*(v-vhm) + c2m*(v-vhm)^2 + d2m*(v-vhm)^3)) ) 

    hInf = (ch/(1 + exp(-ah*v + bh))) + dh 
    hTau = Ah / ( exp(-(b1h*(v-vhh) + c1h*(v-vhh)^2 + d1h*(v-vhh)^3)) + exp((b2h*(v-vhh) + c2h*(v-vhh)^2 + d2h*(v-vhh)^3)) ) 


  UNITSON
}
