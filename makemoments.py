## run in casa

import os

# -- import fits file without primary beam (PB) correction 
#    This is because the noise+signal is uniform in this data. 
importfits(imagename='13co_sub_sub',fitsimage='13co_sub.fits',overwrite=True)

# -- subtract the same small regions for both data 
imsubimage(imagename="13co_sub_sub",  outfile="zoomin.image",  region='',overwrite=True,chans='20~16364')

# -- names of the images 
img       = 'zoomin.image'
sm_img    = 'zoomin.image_sm'
sm_sm_img = 'zoomin.image_sm_sm'
final_img = 'final.image'


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
up_cutoff = 5  * imstat(sm_sm_img)['rms'][0]

## --  make mask using up_cutoff on the smoothed, non-PB corrected datacube,  and apply the mask to the original, unmasked, PB corrected datacube.
os.system("rm -rf mask*")
ia.open(img)
ia.calcmask(mask=str(sm_sm_img)+" > "+str(up_cutoff),name='masked_img')
ia.close()
#


os.system("rm -rf     zoomin.image.mom0")
immoments( imagename='zoomin.image',chans='10920~10950',outfile='zoomin.image.mom0') 
exportfits(imagename='zoomin.image',fitsimage='output.fits',overwrite=True) 



imsubimage(imagename="13co_sub_sub",  outfile="final.image",  region='',overwrite=True)
os.system("rm -rf newmask.image")
immath(imagename=['final.image','zoomin.image.mom0'],expr='IM0*(IM1*0+1)',outfile='newmask.image')


makemask(mode='expand', inpimage='final.image', inpmask='zoomin.image:masked_img', inpfreqs='', outfreqs='', output='bigmask.im', overwrite=True)

exportfits(imagename='newmask.image',fitsimage='newmask.image.fits',overwrite=True,velocity=True)
#
  
