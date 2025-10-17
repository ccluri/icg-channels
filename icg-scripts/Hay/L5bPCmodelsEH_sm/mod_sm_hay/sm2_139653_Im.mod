NEURON
{
  SUFFIX Im 
  USEION k READ ek WRITE ik 
  RANGE gImbar, g, ik
  GLOBAL ek
}

UNITS
{
  (S) = (siemens)
  (mV) = (millivolt)
  (mA) = (milliamp)
}

PARAMETER
{
	gImbar = 0.00001 (S/cm2) 

  am = 0.20000766139197002     (/mV) 
  bm = -7.000345923693324     (1) 
  cm = 0.9999997619713229     (1) 
  dm = 3.924490956638843e-07     (1) 
  vhm = -35.020718086870616     (mV) 
  Am = 102.63399630242182     (/ms) 
  b1m = 0.10008341331342689     (/mV) 
  c1m = -1.9993788584267433e-06     (/mV2) 
  d1m = -1.0042920815343503e-07     (/mV3) 
  b2m = 0.09967447592680621     (/mV) 
  c2m = 1.6371706774670266e-05     (/mV2) 
  d2m = -2.699884076930883e-07     (/mV3) 
}

ASSIGNED
{
  v	(mV)
  ek	(mV)
  ik	(mA/cm2)
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
  g = gImbar*m
  ik = g*(v-ek)
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
