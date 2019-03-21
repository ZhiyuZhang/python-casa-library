import os

# -- import fits file without primary beam (PB) correction 
#    This is because the noise+signal is uniform in this data. 
importfits(imagename='CO_clean_robust2_nopb_niter500',fitsimage='CO_clean_robust2_nopb_niter500.fits',overwrite=True)

# -- import fits file with PB correction -- for creating the final moment map. 
importfits(imagename='CO_clean_robust2_nopb_niter500.pbcor',fitsimage='CO_clean_robust2_nopb_niter500.pbcor.fits',overwrite=True)


# -- subtract the same small regions for both data 
imsubimage(imagename="CO_clean_robust2_nopb_niter500",           outfile="zoomin.image",       chans='20~70',region='box[[250pix,250pix], [1800pix, 1800pix]]',overwrite=True)
imsubimage(imagename="CO_clean_robust2_nopb_niter500.pbcor", outfile="zoomin_pbcor.image", chans='20~70',region='box[[250pix,250pix], [1800pix, 1800pix]]',overwrite=True)

# -- names of the images 
img_pbcor = 'zoomin_pbcor.image'
img       = 'zoomin.image'
sm_img    = 'zoomin.image_sm'
sm_sm_img = 'zoomin.image_sm_sm'


# -- read header 
myhead    = imhead(img,mode  = 'list')
bmaj      = myhead['beammajor']['value']
bmin      = myhead['beamminor']['value']

# -- define the aimed angular resolution after convolution. It is 1.5 x of the mean original value. 1.5^2 ~ 2.25 x area   
out_Beam = str(1.5 * max(np.mean(bmaj),np.mean(bmin)))+"arcsec"

# -- convolve to 1.5 x angular resolution 
imsmooth(imagename=img, outfile=sm_img, kernel='gauss', major=out_Beam, minor=out_Beam, pa="0deg",targetres=True,overwrite=True)

# -- convolve to 2 x channel width,  2.25 x 2 ~ 4.5 x smoothing 
specsmooth(imagename=sm_img, outfile=sm_sm_img,  axis=2, dmethod="",width=2,function='hanning',overwrite=True)

# -- define cutoff to be 3.5 sigma from the convolved datacube  
#  This can be tuned, for optimising the final moment-0 map. 
up_cutoff = 3.5  * imstat(sm_sm_img)['rms'][0]


# --  make mask using up_cutoff on the smoothed, non-PB corrected datacube,  and apply the mask to the original, unmasked, PB corrected datacube.
os.system("rm -rf mask*")
ia.open(img_pbcor)
ia.calcmask(mask=str(sm_sm_img)+" > "+str(up_cutoff),name='masked_img')
ia.close()


# -- Make moment0 image, using the masked, original resolution, PB-corrected datacube. 
#  Selecting 16~40 channel number is the velocity range of about from 281~291 km/s  
os.system("rm -rf zoomin_pbcor.image.mom0")
immoments( imagename='zoomin_pbcor.image',chans='16~40',outfile='zoomin_pbcor.image.mom0') 
exportfits(imagename='zoomin_pbcor.image.mom0',fitsimage='zoomin_pbcor.image.mom0.fits',overwrite=True)

  
