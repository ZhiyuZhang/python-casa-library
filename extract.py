## extract spectra from a datacube using a small aperture 
# use: change the file name in the filelist,  the location of the aperture, and the diameter of the aperture 
# k is the number of the desired datacube in the filelist. 

#-----------------------------------------------------------
# Setup: 
#

# 1). install the package supports 
#  
#  from setuptools.command import easy_install
#  easy_install.main(['--user', 'pip'])
#  import subprocess, sys
#  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'astropy'])
#  import astropy
#  subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'photutils'])

#-----------------------------------------------------------

# usage: 
# change the filenames in filelist and, corresponding locations, and select your circular Aperture diameter, and k (which file )
# then
# execfile('extract.py') 
#
# --written by Zhiyu Zhang  pmozhang@gmail.com 
# last update: 15 Apr. 2023   -- now it reads headers with multiple beams (or without)



import numpy as np
import copy
import astropy.units as u
import matplotlib.pyplot as plt
from   astropy.io          import fits
from   astropy             import wcs
from   photutils           import aperture_photometry, CircularAperture
from   matplotlib.patches  import Ellipse

os.system("rm -rf *fit_beam*")

# -----------   list of the files     ---------- 
#filelist=[ 'spw25.cube.im',   # 0 
#           'spw27.cube.im',   # 1 
#           'spw29.cube.im',
#           'spw31.cube.im',
#           ]                 
#
#location=['19h10m13.148s, 09d06m12.970s', # 0
#          '19h10m13.148s, 09d06m12.970s', # 1
#          '19h10m13.148s, 09d06m12.970s', # 2
#          '19h10m13.148s, 09d06m12.970s', # 3
#           ] 

# -----------   list of the files     ----------
filelist=[ 'IRAS13120_spw25.image.fits',   # 0
          ]

location=['13:15:06.315,-55.09.22.764',#  14h13m09.9415s,-65d20m21.0279s', # 0
           ]


AperDiameter = 0.6 # arcsec 
k            = 0 # the number in the filelist and associated location 


#----------------------- do not change below -------------------


# ------read header file --------
myhead    =  imhead(filelist[k],mode='list')
channels  =  myhead['shape'][2] #myhead['perplanebeams']['nChannels'] #  #channels  =  SpecExtrCube.shape[2] The same 

# --------- the regions for spectral subtraction ------- 
region            =  'circle[['+location[k]+'], '+str(AperDiameter/2.)+'arcsec]'

# Make circular apertures with diameter of xxx arcsec, centralised in (R.A. Dec. J2000)
# --------- extract spectra from the defined region ----
xval         =  imval(imagename=filelist[k], region=region)
SpecExtrCube =  xval['data']
SpecExtrMask =  xval['mask']


# --------------------------------
# get the extracted spectral cube from the selected region  
# This is a 3-D cube, with a dimension something like (15x15x127) 
# So, the spectral values are in box, rather than in circles or in Ellipses
# Xval goes with a mask array to turn the box into circles or Ellipses 
# Xval['data'] is the cube
# Xval['mask'] is the mask cube 
# -------------------------------

#--------------------------------------------
# apply mask to the extracted spectra 
SpecExtrCube[np.where(SpecExtrMask==False)] = np.NaN
# from now on, SpecExtrCube is the cube of the mask-applied extracted spectra 
#--------------------------------------------

f0       = float(myhead['crval3'])          # reference freq in Hz
df       = float(myhead['cdelt3'])          # channel width in Hz
i0       =       myhead['crpix3']           # reference pixel
freqspec = ((np.arange(channels))*df + f0)  # channel array of the observing frequencies in Hz
xdat     =  freqspec /1E9                   # Convert from Hz to GHz

# -------------------------------------------
# Obtain the average flux density (Jy/beam) within the masked region, using the mask-applied extracted spectra 
Flux_jy_p_mean = np.nanmean(SpecExtrCube,axis=(0,1))
# -------------------------------------------


perbmaj =  np.arange(channels)*1.0 
perbmin =  np.arange(channels)*1.0 
perbpa  =  np.arange(channels)*1.0 




if 'perplanebeams' in myhead: 
#   print('yes') 
    for i in range(0, channels):
        print(i)
        perbmaj[i] = myhead['perplanebeams']['*'+str(i)]['major']['value']
        perbmin[i] = myhead['perplanebeams']['*'+str(i)]['minor']['value']
        perbpa[i]  = myhead['perplanebeams']['*'+str(i)]['positionangle']['value']

    bmaj = np.nanmean(perbmaj) 
    bmin = np.nanmean(perbmin) 

else: 
    print('no')
    bmaj = myhead['beammajor']['value']
    bmin = myhead['beamminor']['value']




# --- Read and assign beam values to the arrays
#     Obtain beamsize/shape of each channel varies.
#get pixel size in arcsec
pixelsize    = np.abs((myhead['cdelt1']* u.rad).to(u.arcsec).value)
# beam area calculated from a 2-D Gaussian  in arcsec^2
MyBeamArea     = np.pi*  bmaj * bmin / ( 4 * np.log(2) )
# How many pixels in one beam
MyBeamPixels   = MyBeamArea / (pixelsize**2 )
#------------------

# Area of the aperture for line extraction in arcsec^2 (Area = pi * r^2 )
MyAperArea     =  np.pi*(AperDiameter/2.)**2
# How many pixels in one aperture
MyAperPixels   = MyAperArea/ pixelsize**2
#  ---------------------------------

# ----- Flux density in the masked aperture -----
Flux           = Flux_jy_p_mean * MyAperPixels / MyBeamPixels
# -----------------------------------------------

# From Jy/b to K 
# https://science.nrao.edu/facilities/vla/proposing/TBconv
# note that the unit of the flux density is mjy/beam. Therefore, we need another 1E3

Tb            = 1.222E3 * Flux_jy_p_mean * 1E3 / (xdat**2 * bmaj * bmin) 

plt.clf()
ax1        =  plt.subplot(111) 
ax1.set_xlabel('Frequency (GHz)', fontsize=18)
ax1.set_ylabel('Flux density (Jy)', fontsize=16)
ax1.plot(xdat,Flux,drawstyle='steps-mid')
plt.savefig(filelist[k]+'test.pdf')
os.system('open '+filelist[k]+'test.pdf')

plt.clf()
ax1        =  plt.subplot(111) 
ax1.plot(xdat,Tb,drawstyle='steps-mid')
ax1.set_xlabel('Frequency (GHz)', fontsize=18)
ax1.set_ylabel('Tb (K)', fontsize=16)
plt.savefig(filelist[k]+'Tb.pdf')
os.system('open '+filelist[k]+'Tb.pdf')

plt.clf()
ax1        =  plt.subplot(111) 
ax1.plot(xdat, Flux_jy_p_mean,drawstyle='steps-mid')
ax1.set_xlabel('Frequency (GHz)', fontsize=18)
ax1.set_ylabel('Flux density (Jy/b)', fontsize=16)
plt.savefig(filelist[k]+'Flux_jy_p_mean.pdf')
os.system('open '+filelist[k]+'Flux_jy_p_mean.pdf')




import sys
from astropy.io import ascii
from astropy.table import Table, Column, MaskedColumn
header="W49N western core spectrum"
data = Table([xdat,Tb], names=['#freq(GHz)', 'Tb(K)'] )
ascii.write(data, filelist[k]+'_Tb.dat', format='csv', comment=header)

