# HI selfcal

# Define the initial parameter
calfile = 'AGC242019_HI.ms.calibrated'
myspw = '0,1' 
myimsize = 400
mycell = '7arcsec'
myrestfreq = '1.420405752GHz'
mythreshold = '5.0mJy'
mystart = '1700km/s'
mynchan = 40
mywidth = ''
int_time = '10min'

######################### Initial clean

myimagename = 'target_cube'
rmtables(tablenames=myimagename + '.*')
# For dirty image, used for determining the size of cell and clean threshold
tclean(vis=calfile, spw=myspw, imagename=myimagename+'.dirty',
       imsize=myimsize, cell=mycell, specmode='cube',
       start=mystart, nchan=mynchan, width=mywidth,
       outframe='LSRK', restfreq=myrestfreq, veltype='optical',
       perchanweightdensity=True, pblimit=-0.0001, weighting='briggs', 
       robust=0.5, niter=0)

# start the clean
tclean(vis=calfile, spw=myspw,imagename=myimagename,
       imsize=myimsize, cell=mycell, specmode='cube',
       start=mystart, nchan=mynchan,width=mywidth,
       outframe='LSRK', restfreq=myrestfreq, veltype='optical',
       perchanweightdensity=True, pblimit=-0.0001, weighting='briggs', 
       robust=0.5, niter=10000, threshold=mythreshold, 
       interactive=False, savemodel='modelcolumn')

########################### loop of self-calibration

# calculate the gain table
mycaltable = 'pcal_{}.gcal'.format(int_time)
gaincal(vis=calfile, caltable=mycaltable, spw='0:1900~2000', calmode='p',
        solint='10min',combine='scan', refant='refant', minsnr=3.0)

# check the solution, the gain phase normally within 10~20 degree
plotms(vis=mycaltable, xaxis='time', yaxis='phase', iteraxis='antenna', 
       showgui=True)

applycal(vis=calfile, field='', spw='0,1', gaintable=mycaltable, calwt=False)

# clean the calibrated table again
imagename = 'selfcal_cube'
tclean(vis=calfile, spw=myspw,imagename=myimagename,
       imsize=myimsize, cell=mycell, specmode='cube',
       start=mystart, nchan=mynchan,width=mywidth,
       outframe='LSRK', restfreq=myrestfreq, veltype='optical',
       perchanweightdensity=True, pblimit=-0.0001, weighting='briggs', 
       robust=0.5, niter=10000, threshold=mythreshold, 
       interactive=False, savemodel='modelcolumn')

