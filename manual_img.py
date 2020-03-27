msfile = ''
myspw = '' 
myimsize = 400
mycell = '7arcsec'
myrestfreq = '1.420405752GHz'
mythreshold = '5.0mJy'
mystart = '1700km/s'
mynchan = 40
mywidth = ''

# Continuum subtraction for emission lines
default(uvcontsub)
uvcontsub(vis=msfile, fitspw='0~1:15~50', excludechans=True, want_cont=True)




# image the continuum
myimagename = msfile + '.mfs'
rmtables(tablenames=myimagename + '.*')
tclean(vis=msfile, spw=myspw, imagename=myimagename,
       imsize=myimsize, cell=mycell, specmode='mfs',
       weighting='briggs', robust=0, 
       niter=10000, interactive=True)


####################### Datacube ##############################
myimagename = 'target_cube'
rmtables(tablenames=myimagename + '.*')
# First run for dirty image to determine the cell and threshold
tclean(vis=msfile, spw=myspw, imagename=myimagename+'.dirty',
       imsize=myimsize, cell=mycell, specmode='cube',
       start=mystart, nchan=mynchan, width=mywidth,
       outframe='LSRK', restfreq=myrestfreq, veltype='optical',
       perchanweightdensity=True, pblimit=-0.0001, weighting='briggs', 
       robust=0.5, niter=0, savemodel='modelcolumn')

# start the clean
tclean(vis=msfile, spw=myspw,imagename=myimagename,
       imsize=myimsize, cell=mycell, specmode='cube',
       start=mystart, nchan=mynchan,width=mywidth,
       outframe='LSRK', restfreq=myrestfreq, veltype='optical',
       perchanweightdensity=True, pblimit=-0.0001, weighting='briggs', 
       robust=0.5, niter=10000, threshold=mythreshold, 
       interactive=False, savemodel='modelcolumn')
# check modelcolumn is generated
#niter=0; calcres=False; calcpsf=False

# Moments
immoments(imagename=myimagename, [0], 
          chans='11~40', 
          # box = '0,0,400,400',
          outfile=myimagename+'.mom0')

immoments(imagename=myimagename, moments=[1],
          chans='11~40', 
          # box = '0,0,400,400',
          excludepix=[-100,0.01],
          outfile=myimagename+'.mom1')
