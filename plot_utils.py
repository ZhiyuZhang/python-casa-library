# a collection of plots utils to inspect the data during calibratiion

# by Jianhang Chen
# cjhastro@gmail.com 
# last update: 21 Mar 2019


import os
import random
import numpy as np
from casa import tbtool, plotms, plotants
import analysisUtils as aU


def check_info(vis=None, showgui=False, plotdir='./info', sciencespws='',
             show_ants=True, show_mosaic=True, show_uvcoverage=True,
             show_allobs=True):
    """ plot the basic information of the observation.

    Plots include: antenna positions, UV coverage, mosaic coverage(if possible)

    Parameters
    ----------
    vis : str
        measurement file
    showgui : bool
        show the plot window, (the plotmosaic does not support yet)
    info_dir : str
        the base directory for all the info plots
    sciencespws : str
        the spw related to the science target
    show_mosaic : bool
        plot the relative positions of the mosaic
    show_ants : bool
        plot the positions of the antennae
    show_uvcoverage : bool
        plot the uv coverage of different field, or only the science target if 
        sciencespws is specified
    show_allobs : bool
        plot the all the amp vs time

    """
    os.system('mkdir -p info')

    if show_ants:
        plotants(vis=vis, figfile='{}/antenna_position.png'.format(plotdir), 
                 showgui=showgui)

    if show_mosaic:
        aU.plotmosaic(vis, figfile='{}/mosaic.png'.format(plotdir))

    if show_uvcoverage:
        plotms(vis=vis, xaxis='U', yaxis='V', coloraxis='field', 
               spw=sciencespws, showgui=showgui, 
               plotfile='{}/uvcoverage.png'.format(plotdir),
               overwrite=True)
    if show_allobs:
        plotms(vis=vis, xaxis='time', yaxis='amp', 
               avgchannel='1e8', coloraxis='field', 
               showgui=showgui,
               plotfile='{}/all_observations.png'.format(plotdir),
               overwrite=True)

def check_cal(vis=None, fdmspw=None, tdmspws=None, calibrator_fields=None, 
              refant=None,
              bandpass_calibrator=None, phase_calibrator=None,
              science_field=None, flux_calibrator=None, plot_tsys=False, 
              plot_freq=False, plot_time=False, plot_bandpass=False,
              plot_solutions=False, plot_target=False, plot_uvdist=False,
              overwrite=True, showgui=False, dpi=600, plotdir='./plots'):
    """check the calibrated data after applycal

    Parameters
    ----------
    vis : str
        measurements file
    fdmspw : str
        the spw of frequency domain mode
    tdmspws : list
        the spws of time domain mode, list contain single spw, 
        example: ['1', '3','4']
    calibrator_fields : list
        a list contains all the fields of calibrators
        example: ['0', '2', '3'] or ['J1427-4206', 'Mars']
    science_field : str
        the fields of the science target
        example: 'Cen*' or '4~22'
    refant : str
        the reference antenna, like 'CM03'
    bandpass_calibrator : str
        the field of bandpass calibrator
        example: '0' or 'J1427-4206'
    phase_calibrator : str
        the same as bandpass_calibrator but for bandpass
    flux_calibrator : str
        the same as bandpass_calibrator but for flux calibrator
    plot_tsys : bool
        plot the tsys calibration table, the filename should be vis+'.tsys'
        require: `tdmspws`
    plot_freq : bool
        plot the amplitude-vs-frequency, phase-vs-frequency for both data 
        column and corrected data column
        require: `fdmspw`, `refant`, `calibrator_fields`
    plot_time : bool
        plot the amplitude-vs-time, phase-vs-time for both data column 
        and corrected data column
        require: `fdmspw`, `refant`, `calibrator_fields`
    plot_uvdist : bool
        plot amplitude-vs-uvdist 
        require: `calibrator_fields`
    plot_solutions : bool
        plot bandpass calibration and gain calibration 
        require: `flux_calibrator`, and with vis+'.banpass.cal', 
                 vis+'.phase_inf.cal', vis+'flux.cal' availabe in current 
                 directory
    plot_target : bool
        plot the amplitude-vs-amplitude and amplitude-vs-frequency for the 
        science target
        require: `science_field`
    plot_bandpass : bool
        the plot option to control the plotbandpass task. The default value is
        false since plotbandpass always make casa crash
    overwrite, showgui, dpi 
        the same option for plotms, see casa document for more detail
    plotdir : str
        the root directory to put all the generated plots
    """
    # Extract the antenna list from ms
    tb = tbtool()
    tb.open(vis+'/ANTENNA', nomodify=True)
    ants = tb.getcol('NAME')
    tb.close()
    if refant is None:
        refant = random.choice(ants)
    
    gridrows = int(np.ceil((len(ants)-1)/2))
    baselines = refant + '&*' # all the related baseline

    if bandpass_calibrator:
        calibrator_fields = [bandpass_calibrator]

    # check the frequency based calibration, used be sinificant for Tsys calibration
    if plot_freq:
        print("Plot frequency related calibration for fields: {} ...".format(calibrator_fields))
        os.system('mkdir -p {}/freq/'.format(plotdir))
        for field in calibrator_fields:
            # for amplitude
            plotms(vis=vis, field=field, xaxis='frequency', yaxis='amp',
                   spw=fdmspw, avgtime='1e8', avgscan=True, coloraxis='corr',
                   antenna=baselines, iteraxis='baseline', ydatacolumn='data',
                   showgui=showgui, gridrows=gridrows, gridcols=2,
                   dpi = dpi, overwrite=overwrite,
                   plotfile='{}/freq/field{}_amp_vs_freq.data.png'.format(plotdir, field))
            if not showgui:
                plotms(vis=vis, field=field, xaxis='frequency', yaxis='amp',
                       spw=fdmspw, avgtime='1e8', avgscan=True, coloraxis='corr',
                       antenna=baselines, iteraxis='baseline', ydatacolumn='corrected',
                       showgui=False, gridrows=gridrows, gridcols=2,
                       dpi = dpi, overwrite=overwrite,
                       plotfile='{}/freq/field{}_amp_vs_freq.corrected.png'.format(plotdir, field))


            # for phase
            plotms(vis=vis, field=field, xaxis='frequency', yaxis='phase',
                   spw=fdmspw, avgtime='1e8', avgscan=True, coloraxis='corr',
                   antenna=baselines, iteraxis='baseline', ydatacolumn='data',
                   showgui=showgui, gridrows=gridrows, gridcols=2,
                   dpi = dpi, overwrite=overwrite,
                   plotfile='{}/freq/field{}_phase_vs_freq.data.png'.format(plotdir, field))
            if not showgui:
                plotms(vis=vis, field=field, xaxis='frequency', yaxis='phase',
                       spw=fdmspw, avgtime='1e8', avgscan=True, coloraxis='corr',
                       antenna=baselines, iteraxis='baseline', ydatacolumn='corrected',
                       showgui=False, gridrows=gridrows, gridcols=2,
                       dpi = dpi, overwrite=overwrite,
                       plotfile='{}/freq/field{}_phase_vs_freq.corrected.png'.format(plotdir, field))


    # the phase should be significantly improved after bandpass calibration
    # especially for the phase calibrator
    # if phase_calibrator:
        # calibrator_fields = [phase_calibrator]
        # title = 'phase_calibrator: Amplitude vs Time'
    if plot_time:
        print("Plot time related calibration for fields: {} ...".format(calibrator_fields))
        os.system('mkdir -p {}/time/'.format(plotdir))
        for field in calibrator_fields:
            plotms(vis=vis, field=field, xaxis='time', yaxis='amp',
                   spw=fdmspw, avgchannel='1e8', coloraxis='corr',
                   antenna=baselines, iteraxis='baseline', ydatacolumn='data',
                   showgui=showgui, gridrows=gridrows, gridcols=2,
                   dpi = dpi, overwrite=overwrite,
                   plotfile='{}/time/field{}_amp_vs_time.data.png'.format(plotdir, field))
            plotms(vis=vis, field=field, xaxis='time', yaxis='phase',
                   spw=fdmspw, avgchannel='1e8', coloraxis='corr',
                   antenna=baselines, iteraxis='baseline', ydatacolumn='data',
                   showgui=showgui, gridrows=gridrows, gridcols=2,
                   dpi = dpi, overwrite=overwrite,
                   plotfile='{}/time/field{}_phase_vs_time.data.png'.format(plotdir, field))
            if not showgui:
                plotms(vis=vis, field=field, xaxis='time', yaxis='amp',
                       spw=fdmspw, avgchannel='1e8', coloraxis='corr',
                       antenna=baselines, iteraxis='baseline', ydatacolumn='corrected',
                       showgui=False, gridrows=gridrows, gridcols=2,
                       dpi = dpi, overwrite=overwrite,
                       plotfile='{}/time/field{}_amp_vs_time.corrected.png'.format(plotdir, field))
                plotms(vis=vis, field=field, xaxis='time', yaxis='phase',
                       spw=fdmspw, avgchannel='1e8', coloraxis='corr',
                       antenna=baselines, iteraxis='baseline', ydatacolumn='corrected',
                       showgui=False, gridrows=gridrows, gridcols=2,
                       dpi = dpi, overwrite=overwrite,
                       plotfile='{}/time/field{}_phase_vs_time.corrected.png'.format(plotdir, field))

    if plot_tsys:
        os.system('mkdir -p {}/tsys/'.format(plotdir))
        # plot tsys vs time, to pick out bad antenna
        plotms(vis=vis+'.tsys', xaxis='time', yaxis='tsys', 
               coloraxis='spw',
               gridcols=2, gridrows=gridrows, iteraxis='antenna',
               showgui=showgui,
               plotfile='{}/tsys/Tsys_vs_time.png'.format(plotdir))

        # plot tsys vs frequency
        if tdmspws is None:
            raise ValueError("No tdmspws founded!")
        for spw in tdmspws:
            plotms(vis=vis+'.tsys', xaxis='freq', yaxis='Tsys', spw=spw,
                   gridcols=2, gridrows=gridrows, iteraxis='antenna',
                   coloraxis='corr', showgui=showgui,
                   plotfile='{}/tsys/spw{}_tsys_vs_freq.png'.format(plotdir, spw))
        if plot_bandpass:
            aU.plotbandpass(caltable=vis+'.tsys', overlay='time', 
                    xaxis='freq', yaxis='amp',
                    subplot=22, interactive=False, showatm=True, pwv='auto',
                    chanrange='5~123', showfdm=True, 
                    figfile='{}/tsys/bandpass.png'.format(plotdir))



    if plot_uvdist:
        # well behaved point source should show flat amplitude with uvdist
        print("Plot uvdist related calibration for {} ...".format(calibrator_fields))
        os.system('mkdir -p {}/uvdist/'.format(plotdir))
        for field in calibrator_fields:
            plotms(vis=vis, field=field, xaxis='uvdist', yaxis='amp',
                   avgchannel='1e8', coloraxis='corr', showgui=showgui,
                   dpi=dpi, overwrite=overwrite,
                   plotfile='{}/uvdist/field{}_amp_vs_uvdist.png'.format(plotdir, field))

    if plot_solutions:
        print("Plot calibration solutions ...".format(calibrator_fields))
        os.system('mkdir -p {}/solutions/'.format(plotdir))
        # bandpass
        if plot_bandpass:
            aU.plotbandpass(caltable=vis+'.bandpass.cal', 
                            xaxis='freq', yaxis='both',
                            showatm=True, interactive=showgui, subplot=42,
                            figfile='{}/solutions/bandpasscal.png'.format(plotdir))
        # flux calibrator model
        plotms(vis=vis, xaxis='uvdist', yaxis='amp',
               ydatacolumn='model', field=flux_calibrator, 
               avgtime='1e8', coloraxis='corr',
               showgui=showgui, dpi=dpi, overwrite=overwrite,
               plotfile='{}/solutions/flux_model_amp.png'.format(plotdir))
        plotms(vis=vis, xaxis='uvdist', yaxis='phase',
               ydatacolumn='model', field=flux_calibrator, 
               avgtime='1e8', coloraxis='corr',
               showgui=showgui, dpi=dpi, overwrite=overwrite,
               plotfile='{}/solutions/flux_model_phase.png'.format(plotdir))

        # phase calibration table
        plotms(vis=vis+'.phase_inf.cal', xaxis='time', yaxis='phase',
               coloraxis='corr', iteraxis='antenna', 
               gridcols=2, gridrows=gridrows,
               showgui=showgui, dpi=dpi, overwrite=overwrite, 
               plotfile='{}/solutions/phase_inf_cal.png'.format(plotdir))

        # flux calibration table
        plotms(vis=vis+'.flux.cal', xaxis='time', yaxis='amp',
               coloraxis='corr', iteraxis='antenna',
               gridcols=2, gridrows=gridrows,
               showgui=showgui, dpi=dpi, overwrite=overwrite,
               plotfile='{}/solutions/flux_cal.png'.format(plotdir))
    
    if plot_target:
        print("Giving the science target a glance ...")
        os.system('mkdir -p {}/target/'.format(plotdir))
        if science_field is None:
            raise ValueError("Science field is not specified!")
        plotms(vis=vis, xaxis='uvdist', yaxis='amp',
               ydatacolumn='corrected', field=science_field,
               avgchannel='1e8', coloraxis='corr',
               plotfile = '{}/target/target_amp_vs_uvdist.png'.format(plotdir),
               showgui=showgui, dpi=dpi, overwrite=overwrite)
        plotms(vis=vis, xaxis='freq', yaxis='amp',
               ydatacolumn='corrected', field=science_field,
               avgtime='1e8', avgscan=True, coloraxis='corr',
               plotfile='{}/target/target_amp_vs_freq.png'.format(plotdir),
               showgui=showgui, dpi=dpi, overwrite=overwrite)

