NEURON
{
  SUFFIX Nap_Et2 
  USEION na READ ena WRITE ina 
  RANGE gNap_Et2bar, g, ina
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
	gNap_Et2bar = 0.00001 (S/cm2)

  am = 0.21739083463104913     (/mV) 
  bm = -11.434755683718919     (1) 
  cm = 1.0000002755608888     (1) 
  dm = -2.79201850890458e-07     (1) 
  vhm = -44.606810672757526     (mV) 
  Am = 2.240299587001929     (/ms) 
  b1m = -0.06721765521212048     (/mV) 
  c1m = 0.0005712618631135841     (/mV2) 
  d1m = -1.8446264026740118e-06     (/mV3) 
  b2m = -0.0914671265646086     (/mV) 
  c2m = -0.001663548195693851     (/mV2) 
  d2m = -1.2878360166873823e-05     (/mV3) 

  ah = -0.09988251523806684     (/mV) 
  bh = 4.875016862865681     (1) 
  ch = 0.9984528002016047     (1) 
  dh = -1.9314320522950166e-05     (1) 
  vhh = -82.85273022427309     (mV) 
  Ah = 3543.2535772210463     (/ms) 
  b1h = -0.02353128036724117     (/mV) 
  c1h = 6.297898314049895e-05     (/mV2) 
  d1h = -4.4757543367567856e-08     (/mV3) 
  b2h = -0.05479247730577955     (/mV) 
  c2h = -0.0021440403720803403     (/mV2) 
  d2h = -6.157122170950965e-05     (/mV3) 
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
  g = gNap_Et2bar*m*m*m*h
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
