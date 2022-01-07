from astropy import constants as const
from astropy import units as u
import numpy as np

# Scoville et al. 2016  http://dx.doi.org/10.3847/0004-637X/820/2/83
# dust continuum 850um - > Lv(850um) 


def Gammar_RJ(T,v_obs,z): 
    h      = const.h.cgs.value
    k      = const.k_B.cgs.value
    Gammar = h * v_obs * (1 + z) / (k * T)  / np.exp(h * v_obs * (1+z) / (k * T) -1)
    return Gammar 



# EQ-10 in Scoville 2016 http://dx.doi.org/10.3847/0004-637X/820/2/83
Lv850 = 1.19E27 * Sv * (v850/v_obs*(1+z) )**3.8 * DL**2 / (1+z) * Gammar_RJ(25,v850,0) / Gammar_RJ(25,v_obs,z) 

Sv        = 6   # mJy
z         = 3.4
v850      = 345  # GHz
v_obs     = 330  # GHz
DL        = 30.1375  # Gpc
alpha_850 = 6.7E19 # ergsec-1 Hz-1 Msun-1



# EQ A-1  in Scoville 2017  https://ui.adsabs.harvard.edu/abs/2017ApJ...837..150S/abstract
M_ISM  = 1.78 * Sv * (1+z)**-4.8 *(v850/v_obs)**3.8 * DL**2 * (6.7E19/alpha_850)* Gammar_RJ(25,v850,0) / Gammar_RJ(25,v_obs,z) * 1E10

N_H2   = M_ISM * 1.98840987e+30 / (1.67262192e-27*2)  / 	(3.08567758e+19 *100 )**2 /np.pi 


