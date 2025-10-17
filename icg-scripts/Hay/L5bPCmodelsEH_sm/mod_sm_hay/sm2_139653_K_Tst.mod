NEURON
{
  SUFFIX K_Tst 
  USEION k READ ek WRITE ik 
  RANGE gK_Tstbar, g, ik
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
	gK_Tstbar = 0.00001 (S/cm2)

  am = 0.05263150619085115     (/mV) 
  bm = -0.52631057376621     (1) 
  cm = 0.9999999481428964     (1) 
  dm = 3.5070208452402047e-08     (1) 
  vhm = -50.20385787903797     (mV) 
  Am = 0.7150360731273069     (/ms) 
  b1m = -0.04324622363802804     (/mV) 
  c1m = 0.00034545411697221406     (/mV2) 
  d1m = -9.104902001242219e-07     (/mV3) 
  b2m = -0.019699948614482155     (/mV) 
  c2m = -0.0003241107443844526     (/mV2) 
  d2m = -3.1112004658999076e-06     (/mV3) 

  ah = -0.09999903260520099     (/mV) 
  bh = 7.5999422381154655     (1) 
  ch = 0.9999969049844445     (1) 
  dh = -8.277778971238323e-08     (1) 
  vhh = -81.8873370759951     (mV) 
  Ah = 38.54984961466215     (/ms) 
  b1h = 0.08362665818323702     (/mV) 
  c1h = 0.003154660362047457     (/mV2) 
  d1h = 0.00010330341722326696     (/mV3) 
  b2h = 0.08453321496871312     (/mV) 
  c2h = -0.0007966714758647297     (/mV2) 
  d2h = 2.306459501810497e-06     (/mV3) 
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
  g = gK_Tstbar*m*m*m*m*h
  ik = g*(v-ek)
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
