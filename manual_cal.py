# seting the working direction


#######################################################
#                  Data Prepare
#######################################################

# reduce the size
# split out the emission line spw
split(vis='', outputvis='', spw='')

# define the global variables
msfile = 'AGC242019_HI.ms'
fcal = '0'
bcal = '0'
gcal = '1'
allcal = bcal + ',' + gcal
targets = '2'

update_antpos = False
myrefant = 'ea24'
mysolint = '6s'
mycalwt = False
spw_bpphase ='0:1800~2000,1:800~1000' 

# clearcal(vis=msfile)



#######################################################
#                  Data Pre-inspection
#######################################################
# listobs
default(listobs)
listobs(vis=msfile, listfile=msfile+'.listobs.txt')

# Checking antenna position, choosing the reference antenna
plotants(vis=msfile, figfile='plots/antspos.png')

# Checking the evevation, determine the need of elivation calibration
default(plotms)
plotms(vis=msfile, xaxis='time', yaxis='elevation', avgchannel='1e6', coloraxis='field', plotfile='plots/elevation.png', showgui=False)

# checking the valid timerange of data
plotms(vis=msfile, xaxis='time', yaxis='amplitude', avgchannel='1e6', coloraxis='field', plotfile='plots/amp_time.png', showgui=False)

# checking the
plotms(vis=msfile, xaxis='channel', yaxis='amplitude', avgtime='1e6', coloraxis='field', plotfile='plots/amp_channel.png', showgui=False)



#######################################################
#                  Prior Calibration
#######################################################

##Atenna Poistion
if update_antpos:
    # Correction for antenna position, automatic fetch from online database
    gencal(vis=msfile, caltable='antpos.cal', caltype='antpos', antenna='')

## Antenna efficiency and Gain curve (VLA only)
gencal(vis=msfile, caltable='gaincurve.cal', caltype='gceff')

## Opacity correction 
#for high frequency (e.g., Ku, K, Ka, & Q band)
myTau = plotweather(vis=msfile, doPlot=True) #it will generate the weather plot
gencal(vis=msfile, caltable='opacity.cal', caltype='opac', spw='0', parameter=myTau)

## set flux density
# list all the avaible model
# setjy(vis=msfile ,listmodels=True)
setjy(vis=msfile, field=fcal) #, spw='0',scalebychan=True, model='3C286_L.im')



#######################################################
#                  Prior Flagging
#######################################################
flagdata(vis=msfile, autocorr=True, flagbackup=False)
flagdata(vis=msfile, mode='shadow', flagbackup=False)
#> remove zero data
flagdata(vis=msfile, mode='clip', clipzeros=True, flagbackup=False)
#> remove the first 5s and the end 5s data (optional, see the amp_vs_time)
# flagdata(vis=msfile, mode='quack', quackinterval=3.0, quackmode='beg', flagbackup=False)
# flagdata(vis=msfile, mode='quack', quackinterval=3.0, quackmode='endb', flagbackup=False)
#> saving prior flags 
flagmanager(vis=msfile, mode='save', versionname='Prior')

## Additional manual flagging
# put additional flagging in stand-alone flags.py
try: execfile('./flags.py') 
except: pass



#######################################################
#             Bandpass and Gain Calibration
#######################################################
print("\n==============> Start Calibration <=============\n")
print("\n==============> Generating Bandpass Calibration <=============\n")
# delay calibration
os.system('rm -rf delays.cal')
default(gaincal)
gaincal(vis=msfile, caltable='delays.cal', field=bcal, refant=myrefant, 
        gaintype='K', solint='inf', combine='scan', minsnr=2.0, 
        gaintable=['gaincurve.cal']) # antpos.cal and opacity.cal if applicable

# integration bandpass calibration
os.system('rm -rf bpphase.gcal')
default(gaincal)
gaincal(vis=msfile, caltable="bpphase.gcal", field=bcal, spw=spw_bpphase, 
        solint=mysolint, refant=myrefant, minsnr=2.0, gaintype='G', calmode="p",
        gaintable=['gaincurve.cal', 'delays.cal'])

# bandpass calinration
os.system('rm -rf bandpass.bcal')
default(bandpass)
bandpass(vis=msfile, caltable='bandpass.bcal', field=bcal, spw='', refant=myrefant, 
         combine='scan', solint='inf', bandtype='B', minsnr=2.0,
         gaintable=['bpphase.gcal', 'gaincurve.cal', 'delays.cal'])

# applycal(vis=msfile, field=bcal, calwt=False,
        # gaintable=['gaincurve.cal', 'delays.cal', 'bandpass.bcal'],
        # gainfield=['' ,bcal, bcal])


print("\n==============> Generating Gain Calibration <=============\n")
# phase calibration for quick time variation
os.system('rm -rf phase_int.gcal')
default(gaincal)
gaincal(vis=msfile, caltable='phase_int.gcal', field=allcal, refant=myrefant, 
        calmode='p', solint=mysolint, minsnr=2.0, spw='',
        gaintable=['gaincurve.cal', 'delays.cal', 'bandpass.bcal'])

# phase calibration for long time variation
os.system('rm -rf phase_scan.gcal')
default(gaincal)
gaincal(vis=msfile, caltable='phase_scan.gcal', field=allcal, refant=myrefant, 
        calmode='p', solint='inf', minsnr=2.0, spw='',
        gaintable=['gaincurve.cal', 'delays.cal', 'bandpass.bcal'])

# amplitude calibration
os.system('rm -rf amp.gcal')
default(gaincal)
gaincal(vis=msfile, caltable='amp.gcal', field=allcal, refant=myrefant, 
        calmode='ap', solint='inf', minsnr=2.0, spw='',
        gaintable=['gaincurve.cal','delays.cal','bandpass.bcal','phase_int.gcal'])

# fluxscale
os.system('rm -rf flux.cal')
default(fluxscale)
myscale = fluxscale(vis=msfile, caltable='amp.gcal', fluxtable='flux.cal',
                    reference=fcal, incremental=True)
print(myscale)


print("\n==============> Applying the Calibration <=============\n")
# Applying the caltable to the calibrators
for cal_field in [bcal, gcal]: #[bcal, gcal, fcal]
    default(applycal)
    applycal(vis=msfile, field=cal_field,
             gaintable=['gaincurve.cal', 'delays.cal','bandpass.bcal', 
                        'phase_int.gcal', 'amp.gcal', 'flux.cal'],
             gainfield=['', bcal, bcal, cal_field, cal_field, cal_field],  
             interp = ['', '', 'nearest', '', '', ''],
             calwt=mycalwt)

# apply the caltable to the targets
default(applycal)
applycal(vis=msfile, field=targets,
         gaintable=['gaincurve.cal', 'delays.cal','bandpass.bcal', 
                    'phase_scan.gcal', 'amp.gcal','flux.cal'],
         gainfield=['', bcal, bcal, gcal, gcal, gcal],  
         interp = ['', '', 'nearest', '', '', ''],
         calwt=mycalwt)


# split out the calibrated targets
os.system('rm -rf {}.calibrated'.format(msfile))
split(vis=msfile, field=targets, datacolumn='corrected', outputvis=msfile+'.calibrated')
