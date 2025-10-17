NEURON
{
  SUFFIX NaTs2_t 
  USEION na READ ena WRITE ina 
  RANGE gNaTs2_tbar, g, ina
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
	gNaTs2_tbar = 0.00001 (S/cm2)

  am = 0.16666650134875585     (/mV) 
  bm = -5.717044767303569     (1) 
  cm = 0.9999999328002422     (1) 
  dm = 4.3810911133558966e-08     (1) 
  vhm = -37.42170391642882     (mV) 
  Am = 0.38173805114004294     (/ms) 
  b1m = 0.08284436955755971     (/mV) 
  c1m = 0.0013239736974354425     (/mV2) 
  d1m = 8.58494656809321e-06     (/mV3) 
  b2m = 0.06973709756871933     (/mV) 
  c2m = -0.0006620825367451223     (/mV2) 
  d2m = 2.3401769098415116e-06     (/mV3) 

  ah = -0.1666664060130945     (/mV) 
  bh = 9.99998371331471     (1) 
  ch = 1.0000001019407274     (1) 
  dh = 1.1096303080665746e-08     (1) 
  vhh = -65.86622219501776     (mV) 
  Ah = 3.5138641372855433     (/ms) 
  b1h = 0.10491119884143797     (/mV) 
  c1h = 0.0024400400716513802     (/mV2) 
  d1h = 2.7074605814638898e-05     (/mV3) 
  b2h = 0.05562428015303498     (/mV) 
  c2h = -0.0004010809872008586     (/mV2) 
  d2h = 1.1098748103618525e-06     (/mV3) 
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
  g = gNaTs2_tbar*m*m*m*h
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

    mInf = (cm/(1 + exp(-am*v + bm))) + dm 
    mTau = Am / ( exp(-(b1m*(v-vhm) + c1m*(v-vhm)^2 + d1m*(v-vhm)^3)) + exp((b2m*(v-vhm) + c2m*(v-vhm)^2 + d2m*(v-vhm)^3)) ) 

    hInf = (ch/(1 + exp(-ah*v + bh))) + dh 
    hTau = Ah / ( exp(-(b1h*(v-vhh) + c1h*(v-vhh)^2 + d1h*(v-vhh)^3)) + exp((b2h*(v-vhh) + c2h*(v-vhh)^2 + d2h*(v-vhh)^3)) ) 


  UNITSON
}
