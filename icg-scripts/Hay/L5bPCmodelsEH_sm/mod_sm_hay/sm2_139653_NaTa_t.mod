NEURON
{
  SUFFIX NaTa_t 
  USEION na READ ena WRITE ina 
  RANGE gNaTa_tbar, g, ina
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
	gNaTa_tbar = 0.00001 (S/cm2)

  am = 0.16666637840497564     (/mV) 
  bm = -6.717040736129723     (1) 
  cm = 0.9999998763687157     (1) 
  dm = 5.841755027961537e-08     (1) 
  vhm = -44.85864259136966     (mV) 
  Am = 0.3794707494451536     (/ms) 
  b1m = -0.06677527713635831     (/mV) 
  c1m = 0.0005880166130177411     (/mV2) 
  d1m = -1.9005347815404982e-06     (/mV3) 
  b2m = -0.0939506912648036     (/mV) 
  c2m = -0.0018313751321935657     (/mV2) 
  d2m = -1.4751428395496e-05     (/mV3) 

  ah = -0.16666628785170734     (/mV) 
  bh = 10.999974999398434     (1) 
  ch = 1.0000002830932104     (1) 
  dh = -8.25192098873107e-08     (1) 
  vhh = -72.16228708579123     (mV) 
  Ah = 3.483069636156768     (/ms) 
  b1h = -0.05460884127059624     (/mV) 
  c1h = 0.0003834128081126095     (/mV2) 
  d1h = -1.03059922901717e-06     (/mV3) 
  b2h = -0.10671587278588505     (/mV) 
  c2h = -0.0027020606768863946     (/mV2) 
  d2h = -3.538684920275163e-05     (/mV3) 
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
  g = gNaTa_tbar*m*m*m*h
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
