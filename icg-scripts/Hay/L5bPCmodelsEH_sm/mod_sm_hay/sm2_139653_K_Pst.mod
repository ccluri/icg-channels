NEURON
{
  SUFFIX K_Pst 
  USEION k READ ek WRITE ik 
  RANGE gK_Pstbar, g, ik
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
	gK_Pstbar = 0.00001 (S/cm2)

  am = 0.08333323585307917     (/mV) 
  bm = -0.9166577778775975     (1) 
  cm = 0.9999999716634634     (1) 
  dm = 5.3492161802377286e-08     (1) 
  vhm = -71.59695865999169     (mV) 
  Am = 24.993195398418298     (/ms) 
  b1m = -0.0308599192870671     (/mV) 
  c1m = 7.00498459743512e-05     (/mV2) 
  d1m = -9.388831042778649e-08     (/mV3) 
  b2m = -0.09657588650961603     (/mV) 
  c2m = -0.0038130228062920697     (/mV2) 
  d2m = -7.297273450529574e-05     (/mV3) 

  ah = -0.09088868218001238     (/mV) 
  bh = 5.817446869429546     (1) 
  ch = 0.9998604745457104     (1) 
  dh = -2.162930563961813e-06     (1) 
  vhh = -50.522570024711705     (mV) 
  Ah = 794.4535556550212     (/ms) 
  b1h = -0.051126533676958304     (/mV) 
  c1h = 0.00045573771047294995     (/mV2) 
  d1h = -1.326961325102506e-06     (/mV3) 
  b2h = -0.03443848008734899     (/mV) 
  c2h = -0.000544050732985451     (/mV2) 
  d2h = -9.491896105776484e-06     (/mV3) 
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
  g = gK_Pstbar*m*m*h
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
