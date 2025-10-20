import numpy as np

# functions to approximate steady states and time constants
def sigmoid(x,a,b):
    return 1/(1+np.exp(-a*x+b))

def modified_sigmoid(x,a,b,c,d):
    return c/(1+np.exp(-a*x+b)) + d

def tau_fun1(x,a,b,c,d):
    y = (x - a)
    return b/(np.exp(-(c*y)) + np.exp(d*y))

def tau_fun2(x,a,b,c,d,e,f):
    y = (x - a)
    return b/(np.exp(-(c*y+d*y**2)) + np.exp(e*y+f*y**2))

def tau_fun3(x,a,b,c,d,e,f,g,h):
    y = (x - a)
    return b/(np.exp(-(c*y+d*y**2+e*y**3)) + np.exp(f*y+g*y**2+h*y**3))

def tau_fun4(x,a,b,c,d,e,f,g,h,i,j):
    y = (x - a)
    return b/(np.exp(-(c*y+d*y**2+e*y**3+f*y**4)) + np.exp(g*y+h*y**2+i*y**3+j*y**4))