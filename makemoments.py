# Example:: 
# execfile('makemoments.py') 
# makemoms('cube_CO65_contsub_selfcal_image.fits')

import os
import glob

def makemoms(fitsfilename): 
    imgname     = fitsfilename[0:-4]+"image"
    outputname  = fitsfilename[0:-5]+"_mom0.fits"
    outputname1 = fitsfilename[0:-5]+"_mom1.fits"
    outputname2 = fitsfilename[0:-5]+"_mom2.fits"
    # -- import fits file without primary beam (PB) correction 

    #    This is because the noise+signal is uniform in this data. 
    importfits(imagename=imgname,fitsimage=fitsfilename,overwrite=True)

    # -- names of the images 
    sm_img    = 'sm.image'
    sm_sm_img = 'sm_sm.image'

    # -- read header 
    myhead    = imhead(imgname,mode  = 'list')
    bmaj      = myhead['beammajor']['value']
    bmin      = myhead['beamminor']['value']

    # -- define the aimed angular resolution after convolution. It is 1.5 x of the mean original value. 1.5^2 ~ 2.25 x area   
    out_Beam = str(1.5 * max(np.mean(bmaj),np.mean(bmin)))+"arcsec"

    # -- convolve to 1.5 x angular resolution 
    imsmooth(imagename=imgname, outfile=sm_img, kernel='gauss', major=out_Beam, minor=out_Beam, pa="0deg",targetres=True,overwrite=True)

    # -- convolve to 2 x channel width,  2.25 x 2 ~ 4.5 x smoothing 
    specsmooth(imagename=sm_img, outfile=sm_sm_img,  axis=2, dmethod="",width=2,function='hanning',overwrite=True)

    # -- define cutoff to be 3.5 sigma from the convolved datacube  
    #  This can be tuned, for optimising the final moment-0 map. 
    up_cutoff = 2 * imstat(sm_sm_img)['rms'][0]

    # --  make mask using up_cutoff on the smoothed, non-PB corrected datacube,  and apply the mask to the original, unmasked, PB corrected datacube.
    os.system("rm -rf mask*")
    ia.open(imgname)
    ia.calcmask(mask=str(sm_sm_img)+" > "+str(up_cutoff),name='masked_img')
    ia.close()

    # -- Make moment0 image, using the masked, original resolution, PB-corrected datacube. 
    #  Selecting 16~40 channel number is the velocity range of about from 281~291 km/s  
    os.system("rm -rf image.mom0 ")
    immoments( imagename=imgname,chans='',outfile='image.mom0') 
    exportfits(imagename='image.mom0',fitsimage=outputname,overwrite=True)
    os.system("rm -rf image.mom1 ")
    immoments( imagename=imgname,moments=1,chans='',outfile='image.mom1') 
    exportfits(imagename='image.mom1',fitsimage=outputname,overwrite=True)
    os.system("rm -rf image.mom2 ")
    immoments( imagename=imgname,moments=2,chans='',outfile='image.mom2') 
    exportfits(imagename='image.mom2',fitsimage=outputname,overwrite=True)
    
      
