# 
# split(vis='uid___A002_Xb0ebd1_Xe3ea.ms.split.cal',outputvis='spw3_split.ms', field='6',spw='3',datacolumn='data') 
# rm -rf spw3_split.ms.con*
# uvcontsub(vis='spw3_split.ms',want_cont=True,fitspw='0:500~1000;3300~3700')  
# 
# flagdata(vis ='spw3_split.ms.contsub',  mode = 'manual', antenna='DV04',flagbackup = F)

# split(vis='uid___A002_Xb0ebd1_Xe3ea.ms.split.cal',outputvis='spw012.ms', field='6',spw='0,1,2',datacolumn='data') 

# flagdata(vis ='spw012',  mode = 'manual', antenna='DV04',flagbackup = F)
# flagdata(vis ='spw3_split.ms.cont',  mode = 'manual', antenna='DV04',flagbackup = F)
# split(vis='spw3_split.ms.cont',outputvis='spw3_split.ms_avg.cont', field='',spw='',width=40, datacolumn='data') 
# concat(vis=['spw3_split.ms_avg.cont', 'spw012.ms'], concatvis='all.ms')

vis_cont_name = 'spw012.ms'
visname       = "spw3_split.ms.contsub"
img1          = 'dirty_image.img.image'
img2          = 'clean_image.img.image'
sm_img1       = 'dirty_image.sm.image'
sm_sm_img1    = 'dirty_image.sm_sm.image'
continuum_img = 'all.continuum.image'


#----------------------------------------
os.system("rm -rf dirty_image*")

default(clean)

clean( vis           = visname,
       imagename     = "dirty_image.img",
       uvrange       = "",
       antenna       = "!DV04",
       mode          = "velocity",
       niter         = 100,
       threshold     = "8mJy",
       psfmode       = "clark",
       imagermode    = "csclean",
       interactive   = False, 
       mask          = "",
       nchan         = 50,
       start         = "-300km/s",
       width         = "15km/s",
       imsize        = [600, 600],
       cell          = "0.06arcsec",
       restfreq      = "483.460GHz",
       weighting     = "briggs",
       robust        = 1.5,
       uvtaper       = False,
       outertaper    = [''],
       restoringbeam = [''],
       usescratch    = False)
#----------------------------------------

os.system("rm -rf dirty_image.sm*")

ia.open(img1)

beam     = ia.restoringbeam()
maj      = beam['major']['value']
mir      = beam['minor']['value']
out_Beam = str(1.5 * max(maj,mir))+"arcsec"

imsmooth(imagename=img1, outfile=sm_img1, kernel='gauss', major=out_Beam, minor=out_Beam, pa="0deg")  
specsmooth(imagename=sm_img1, outfile=sm_sm_img1,  axis=3, dmethod="",function='hanning',overwrite=True)  

up_cutoff = 2 * imstat(sm_sm_img1,box='50,50,150,150')['rms'][0]
threshold = 2 * imstat(sm_sm_img1,box='50,50,150,150')['rms'][0]


os.system("rm -rf sm_dirty_image.fits")
exportfits(imagename=sm_img1,fitsimage='sm_dirty_image.fits',velocity=True)
os.system("rm -rf  smsm_clean_image.fits")
exportfits(imagename=sm_sm_img1,fitsimage='smsm_clean_image.fits',velocity=True)


os.system("rm -rf mask*")

ia.close()


os.system("cp -r "+img1+" mask/")
mask ="mask"

ia.open(mask)
ia.calcmask(mask=str(sm_sm_img1)+">"+str(up_cutoff),name='mask')
ia.close()

os.system("rm -rf mask_0")


makemask( mode='expand', inpimage=mask, inpmask=mask+":"+"mask", output="mask_0", overwrite=True)

exportfits(imagename='mask_0',fitsimage='mask_0.fits',velocity=True)


#----------------------------------------
default(clean)

os.system("rm -rf clean_image*")

clean( vis           = visname,
       imagename     = 'clean_image.img',
       uvrange       = "32klambda:800klambda",
       antenna       = "!DV04",
       mode          = "velocity",
       niter         = 5000,
       threshold     = threshold,
       psfmode       = "clark",
       imagermode    = "csclean",
       mask          = 'mask_0',
       interactive   = False, 
       nchan         = 50,
       start         = "-300km/s",
       width         = "15km/s",
       imsize        = [600, 600],
       cell          = "0.06arcsec",
       restfreq      = "483.460GHz",
       weighting     = "briggs",
       robust        = 1.5,
       uvtaper       = False,
       outertaper    = [''],
       restoringbeam = [''],
       usescratch    = False)

#----------------------------------------

exportfits(imagename=img1,fitsimage='dirty_image.fits',velocity=True)

exportfits(imagename=img2,fitsimage='clean_image.fits',velocity=True)




# -------------- continuum 


os.system("rm -rf cube_spw12*")


clean(vis         = 'spw012.ms',
      imagename   = 'cube_spw12',
      spw         = '1,2',
      mode        = 'channel',
      outframe    = 'BARY',
      interactive = T,
      niter       = 200,
      imsize      = [600,600],
      cell        = '0.06arcsec',
      weighting   = "briggs",
      robust      = 1.5,
      threshold   = '7mJy',
      pbcor       = F)

exportfits(imagename='cube_spw12.image',fitsimage='cube_spw12.fits', overwrite=True)



os.system("rm -rf cube_spw0*")

clean(vis         = 'spw012.ms',
      imagename   = 'cube_spw0',
      spw         = '0',
      mode        = 'channel',
      outframe    = 'BARY',
      interactive = T,
      niter       = 200,
      imsize      = [600,600],
      cell        = '0.06arcsec',
      weighting   = "briggs",
      robust      = 1.5,
      threshold   = '7mJy',
      pbcor       = F)

exportfits(imagename='cube_spw0.image',fitsimage='cube_spw0.fits', overwrite=True)



os.system("rm -rf cube_spw3*")

clean(vis         = 'spw3_split.ms.cont',
      imagename   = 'cube_spw3',
      spw         = '0',
      mode        = 'mfs',
      outframe    = 'BARY',
      interactive = T,
      niter       = 200,
      imsize      = [600,600],
      cell        = '0.06arcsec',
      weighting   = "briggs",
      robust      = 1.5,
      threshold   = '7mJy',
      pbcor       = F)

exportfits(imagename='cube_spw3.image',fitsimage='cube_spw3.fits')





clean(vis         = 'all.ms',
      imagename   = 'all.continuum',
      spw         = '',
      mode        = 'mfs',
      interactive = F,
      niter       = 0,
      imsize      = [600,600],
      cell        = '0.06arcsec',
      weighting   = "briggs",
      robust      = 1.5,
      threshold   = '0.5mJy',
      pbcor       = F)

# rms: 1mJy/beam
continuum_img = 'all.continuum.image'
threshold     = 2 * imstat(continuum_img,box = '100,100,240,240')['rms'][0]



os.system("rm -rf all.continuum*")
clean(vis         = 'all.ms',
      imagename   = 'all.continuum',
      spw         = '',
      mode        = 'mfs',
      interactive = T,
      niter       = 20000,
      imsize      = [600,600],
      cell        = '0.06arcsec',
      weighting   = "briggs",
      robust      = 1.5,
      threshold   = str(threshold)+"Jy",
      pbcor       = F)

exportfits(imagename='all.continuum.image',fitsimage='all.continuum.fits',velocity=True)




os.system("rm -rf all.uvrange.continuum*")
clean(vis         = 'all.ms',
      imagename   = 'all.uvrange.continuum',
      uvrange     = "40~1000klambda",
      spw         = '',
      mode        = 'mfs',
      interactive = T,
      niter       = 20000,
      imsize      = [600,600],
      cell        = '0.06arcsec',
      weighting   = "briggs",
      robust      = 1.5,
      threshold   = str(threshold)+"Jy",
      pbcor       = F)

exportfits(imagename='all.uvrange.continuum.image',fitsimage='all.uvrange.continuum.fits')




os.system("rm -rf all_taper.continuum*")
clean(vis         = 'all.ms',
      imagename   = 'all_taper.continuum',
      spw         = '',
      mode        = 'mfs',
      interactive = T,
      niter       = 20000,
      imsize      = [600,600],
      cell        = '0.06arcsec',
      weighting   = "briggs",
      robust      = 1.5,
      threshold   = str(threshold)+"Jy",
      uvtaper     = T,
      outertaper  = '0.5arcsec',
      pbcor       = F)

exportfits(imagename='all_taper.continuum.image',fitsimage='all_taper.continuum.fits',velocity=True)






