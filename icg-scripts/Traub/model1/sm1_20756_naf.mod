NEURON
{
  SUFFIX naf 
  USEION na READ ena WRITE ina 
  RANGE gbar, g, ina
  GLOBAL ena
}

UNITS
{
  (S) = (siemens)
  (mV) = (millivolt)
  (mA) = (milliamp)
}

PARAMETER
{
  gbar = 1 (S/cm2)

  am = 0.09999850787303223     (/mV) 
  bm = -3.4500284154031133     (1) 
  vhm = -29.340734524519377     (mV) 
  Am = 0.27021780863584755     (/ms) 
  b1m = -0.10589057028159318     (/mV) 
  c1m = 0.0014665917680544616     (/mV2) 
  d1m = -6.148227666056209e-06     (/mV3) 
  b2m = -0.15963567667799655     (/mV) 
  c2m = -0.0036751659999904934     (/mV2) 
  d2m = -2.6703950081047487e-05     (/mV3) 

  ah = -0.09345683301311901     (/mV) 
  bh = 5.878440540259069     (1) 
  vhh = -28.176414154889578     (mV) 
  Ah = 1.1256349406938961     (/ms) 
  b1h = -0.06382266843886739     (/mV) 
  c1h = 0.0006899067093472695     (/mV2) 
  d1h = -2.440556280327623e-06     (/mV3) 
  b2h = -0.0018211259568393832     (/mV) 
  c2h = -0.000129907786087784     (/mV2) 
  d2h = -1.0960328705789923e-06     (/mV3) 
}

ASSIGNED
{
  v	(mV)
  ena	(mV)
  ina	(mA/cm2)
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
  g = gbar*m*m*m*h
  ina = g*(v-ena)
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

    mInf = 1/(1 + exp(-am*v + bm)) 
    mTau = Am / ( exp(-(b1m*(v-vhm) + c1m*(v-vhm)^2 + d1m*(v-vhm)^3)) + exp((b2m*(v-vhm) + c2m*(v-vhm)^2 + d2m*(v-vhm)^3)) ) 

    hInf = 1/(1 + exp(-ah*v + bh)) 
    hTau = Ah / ( exp(-(b1h*(v-vhh) + c1h*(v-vhh)^2 + d1h*(v-vhh)^3)) + exp((b2h*(v-vhh) + c2h*(v-vhh)^2 + d2h*(v-vhh)^3)) ) 


  UNITSON
}