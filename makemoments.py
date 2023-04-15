# run inside CASA (6.1.2.4)

# USAGE: 
# makemoms(filename,channel_range,Npix)
# Here channel_range is the channel range to make moment maps
# Npix is the number of connected pixels, below which the structure will be flagged 
# Example:: 
# execfile('makemoments.py') 
# makemoms('cube_CO65_contsub_selfcal_image.fits','485~510',20)
# or 
# makemoms('cube_CO65_contsub_selfcal_image.image','485~510',20)

# -- automatically tell the input format -- casa or fits 
# latest update by zhiyuzhang 15 Apr 2023

import os
import glob
from astropy.io import fits
from matplotlib import pyplot as plt
from scipy      import ndimage
from matplotlib import pyplot as plt
from scipy      import ndimage
from astropy.utils.console import ProgressBar
import numpy as np


def flagdwarfs(filename,Npix):

    filename = filename 
    cube     = fits.open(filename)
    header   = cube[0].header
    if len(cube[0].data.shape) ==4:
        sig = cube[0].data[0,:]
        mask= cube[0].data [0,:]> 0 # * noise[0].data
    else:
        sig = cube[0].data
        mask= cube[0].data > 0 # * noise[0].data

   
    # This is to find connected components in an array
    # https://scipy-lectures.org/intro/scipy/auto_examples/plot_connect_measurements.html
    # by default, it is 2-D array. However, I found this to adopt to 3-D cubes
    # https://stackoverflow.com/questions/36917944/label-3d-numpy-array-with-scipy-ndimage-label
    
    str_3D = np.array([[[0, 0, 0],
                        [0, 0, 0],
                        [0, 0, 0]],
                      [[0, 1, 0],
                        [1, 1, 1],
                        [0, 1, 0]],
                      [[0, 0, 0],
                        [0, 0, 0],
                        [0, 0, 0]]],
                      dtype='uint8')
    
    labels, nb = ndimage.label(mask,structure=str_3D)
    print("=========================================================================")
    print("|Eliminating 3-D structures with less than Npix connected pixels (in 3-D).|")
    print("=========================================================================")
    with ProgressBar(nb) as bar:
        for i in range(nb):
            bar.update()
            sl = ndimage.find_objects(labels==i)
        #   print(i)
            if sig[sl[0]].size < Npix:
                sig[sl[0]] = np.NaN
    
    hdu = fits.PrimaryHDU(header=header,data=sig)
    hdu.writeto('flagged.fits',overwrite=True)





def makemoms(fitsfilename,chans,Npix): 
    if fitsfilename[-4:] == '.fits':
        imgname     = fitsfilename[0:-4]+"image"
        outputname  = fitsfilename[0:-5]+"_mom0.fits"
        outputname1 = fitsfilename[0:-5]+"_mom1.fits"
        outputname2 = fitsfilename[0:-5]+"_mom2.fits"
        # -- import fits file without primary beam (PB) correction 

        #    This is because the noise+signal is uniform in this data. 
        importfits(imagename=imgname,fitsimage=fitsfilename,overwrite=True)
    else: 
        imgname     = fitsfilename
        outputname  = fitsfilename+"_mom0.fits"
        outputname1 = fitsfilename+"_mom1.fits"
        outputname2 = fitsfilename+"_mom2.fits"


    # -- names of the images 
    sm_img    = 'sm.image'
    sm_sm_img = 'sm_sm.image'

    # -- read header 
    myhead    = imhead(imgname,mode  = 'list')
    channels  =  myhead['shape'][2] #myhead['perplanebeams']['nChannels'] #  #channels  =  SpecExtrCube.shape[2] The same

    perbmaj =  np.arange(channels)*1.0
    perbmin =  np.arange(channels)*1.0
    perbpa  =  np.arange(channels)*1.0
    
    if 'perplanebeams' in myhead:
        print('perplanebeams')
        for i in range(0, channels):
            print(i)
            perbmaj[i] = myhead['perplanebeams']['*'+str(i)]['major']['value']
            perbmin[i] = myhead['perplanebeams']['*'+str(i)]['minor']['value']
            perbpa[i]  = myhead['perplanebeams']['*'+str(i)]['positionangle']['value']
    
        bmaj = np.nanmean(perbmaj)
        bmin = np.nanmean(perbmin)
        vaxis = 3
    
    else:
        print('Uniform beam')
        bmaj = myhead['beammajor']['value']
        bmin = myhead['beamminor']['value']
        vaxis = 2

    print("vaxis=", vaxis)
 

    # -- define the aimed angular resolution after convolution. It is 1.5 x of the mean original value. 1.5^2 ~ 2.25 x area   
    out_Beam = str(1.5 * max(np.mean(bmaj),np.mean(bmin)))+"arcsec"

    # -- convolve to 1.5 x angular resolution 
    imsmooth(imagename=imgname, outfile=sm_img, kernel='gauss', major=out_Beam, minor=out_Beam, pa="0deg",targetres=True,overwrite=True)

    # -- convolve to 2 x channel width,  2.25 x 2 ~ 4.5 x smoothing 
    specsmooth(imagename=sm_img, outfile=sm_sm_img,  axis=vaxis, dmethod="",width=2,function='hanning',overwrite=True)

    # -- define cutoff to be 3.5 sigma from the convolved datacube  
    #  This can be tuned, for optimising the final moment-0 map. 
    up_cutoff = 3 * imstat(sm_sm_img)['rms'][0]

    # --  make mask using up_cutoff on the smoothed, non-PB corrected datacube,  and apply the mask to the original, unmasked, PB corrected datacube.
    os.system("rm -rf mask*")
    ia.open(imgname)
    ia.calcmask(mask=str(sm_sm_img)+" > "+str(up_cutoff),name='masked_img')
    ia.close()
    
    os.system('rm -rf file_w_dwarfs.fits flagged.fits img_wo_dwarfs.im') 
    exportfits(imagename=imgname,fitsimage='file_w_dwarfs.fits')
    flagdwarfs('file_w_dwarfs.fits',Npix)
    importfits(fitsimage='flagged.fits',imagename='img_wo_dwarfs.im')
    imgname = 'img_wo_dwarfs.im'
    exportfits(imagename=imgname,fitsimage='file_wo_dwarfs.fits',overwrite=True)


    # -- Make moment0 image, using the masked, original resolution, PB-corrected datacube. 
    os.system("rm -rf image.mom0 mom0.fits")
    outputname ='mom0.fits'
    immoments( imagename=imgname,moments=0,chans=chans,outfile='image.mom0') 
    exportfits(imagename='image.mom0',fitsimage=outputname,overwrite=True)

    os.system("rm -rf image.mom1 mom1.fits")
    outputname ='mom1.fits'
    immoments( imagename=imgname,moments=1,chans=chans,outfile='image.mom1',excludepix=[-100.,0.0]) 
    exportfits(imagename='image.mom1',fitsimage=outputname,overwrite=True)

    os.system("rm -rf image.mom2 mom2.fits")
    outputname ='mom2.fits'
    immoments( imagename=imgname,moments=2,chans=chans,outfile='image.mom2',excludepix=[-100.,0.0]) 
    exportfits(imagename='image.mom2',fitsimage=outputname,overwrite=True)
    
      
