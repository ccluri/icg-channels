NEURON
{
  SUFFIX Ih 
  NONSPECIFIC_CURRENT i
  RANGE gIhbar, g
  GLOBAL eh
}

UNITS
{
  (S) = (siemens)
  (mV) = (millivolt)
  (mA) = (milliamp)
}

PARAMETER
{
	gIhbar = 0.00001 (S/cm2) 
	ehcn =  -45.0 (mV)

  am = -0.10164186234404338     (/mV) 
  bm = 10.949603374277752     (1) 
  cm = 0.8721781759889775     (1) 
  dm = -2.2679264054941582e-05     (1) 
  vhm = -110.38054201549147     (mV) 
  Am = 144.18957974457896     (/ms) 
  b1m = 0.06527417541455983     (/mV) 
  c1m = 0.00011279021035762521     (/mV2) 
  d1m = 1.0858982333197093e-06     (/mV3) 
  b2m = 0.029964828044950577     (/mV) 
  c2m = 2.3588310561083035e-06     (/mV2) 
  d2m = -8.46049048447657e-09     (/mV3) 
}

ASSIGNED
{
  v	(mV)
  eh	(mV)
  i	(mA/cm2)
  g	(S/cm2)
  celsius	(degC)
  mInf 
  mTau 
}

STATE
{
  m
}

BREAKPOINT
{
  SOLVE states METHOD cnexp
  g = gIhbar*m
  i = g*(v-ehcn)
}

DERIVATIVE states
{
  rates(v)
  m' = (mInf - m) / mTau 
}

INITIAL
{
  rates(v)
  m = mInf 
}

PROCEDURE rates(v(mV))
{
  UNITSOFF

    mInf = (cm/(1 + exp(-am*v + bm))) + dm 
    mTau = Am / ( exp(-(b1m*(v-vhm) + c1m*(v-vhm)^2 + d1m*(v-vhm)^3)) + exp((b2m*(v-vhm) + c2m*(v-vhm)^2 + d2m*(v-vhm)^3)) ) 


  UNITSON
}
