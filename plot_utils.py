# a collection of plots utils to inspect the data during calibratiion

# by Jianhang Chen
# cjhastro@gmail.com 
# last update: 21 Mar 2019


import os
import random
import numpy as np
from casa import tbtool, plotms, plotants
import analysisUtils as aU

def spw_expand(spwstr):
    """expand the spw string into a list

    Parameters
    ----------
    spwstr : str or list
        example: '1,3,4', '1~3', ['1','3','4']

    Returns
    -------
    a list of single spws

    """
    if '~' in spwstr:
        try: 
            spw_range = spwstr.split('~')
            spw_nums = list(range(int(spw_range[0]), int(spw_range[-1])+1))
            spw_list = map(str, spw_nums)
        except:
            raise ValueError("Invalide steps parameter! Checking the doc.")
    elif ',' in spwstr:
        spw_list = spwstr.split(',')
    else:
        spw_list = spwstr

    return spw_list

def spw_join(spw_list):
    """do the oposite things as `spw_expand`
    
    Parameters
    ----------
    spw_list : list
        example: ['1','2','4'], ['J1427-4206', 'Titan', 'Centaurus_A']
    """
    spwstr = ''
    for spw in spw_list:
        spwstr += spw+','

    return spwstr[:-1]

def group_antenna(antenna_list=[], refant=None, subgroup_num=6):
    """group a large number of antenna into small subgroup for plot procedures

    Parameters
    ----------
    
    Returns
    -------
    A list of subgroups
    """
    if refant is not None:
        refant_idx = np.where(antenna_list == refant)
        # remove the refant from antenna_list
        antenna_list_new = np.delete(antenna_list, refant_idx)
        subgroups = []
        for i in range(0, len(antenna_list_new), subgroup_num):
            antbaseline = ''
            for j in range(0, subgroup_num):
                try:
                    antbaseline += '{}&{};'.format(refant, antenna_list_new[i+j])
                except:
                    pass
            subgroups.append(antbaseline[:-1])
    else:
        subgroups = []
        for i in range(0, len(antenna_list), subgroup_num):
            antbaseline = ''
            for j in range(0, subgroup_num):
                try:
                    antbaseline += '{},'.format(antenna_list[i+j])
                except:
                    pass
            subgroups.append(antbaseline[:-1])
 

    return subgroups

def check_info(vis=None, showgui=False, plotdir='./plots', sciencespws='',
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
    os.system('mkdir -p {}/info'.format(plotdir))
    plotdir = plotdir + '/info'

    if show_ants:
        plotants(vis=vis, figfile='{}/antenna_position.png'.format(plotdir))

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

def plot_tsys(vis=None, tdmspws=None, antenna=None, gridcols=None, gridrows=None, plotdir='./plots'):
    """the stand alone plot function for tsys
    """
    # Extract the antenna list from ms
    tb = tbtool()
    tb.open(vis+'/ANTENNA', nomodify=True)
    ants = tb.getcol('NAME')
    tb.close()
    
    gridrows = int(np.ceil((len(ants)-1)/2))
    subgroup_num = 6
    gridrows = subgroup_num / 2
    ants_subgroups = group_antenna(ants, subgroup_num=subgroup_num)

    if plot_tsys:
        os.system('mkdir -p {}/tsys/'.format(plotdir))
        # plot tsys vs time, to pick out bad antenna
        for page,antenna in enumerate(ants_subgroups):
            plotms(vis=vis+'.tsys', xaxis='time', yaxis='Tsys', 
                   coloraxis='spw', antenna=antenna,
                   gridcols=2, gridrows=gridrows, iteraxis='antenna',
                   showgui=showgui,
                   plotfile='{}/tsys/Tsys_vs_time.page{}.png'.format(plotdir, page))

            # plot tsys vs frequency
            if tdmspws is None:
                raise ValueError("No tdmspws founded!")
            for spw in spw_expand(tdmspws):
                plotms(vis=vis+'.tsys', xaxis='freq', yaxis='Tsys', spw=spw,
                       gridcols=2, gridrows=gridrows, iteraxis='antenna',
                       coloraxis='corr', antenna=antenna, showgui=showgui,
                       plotfile='{}/tsys/spw{}_tsys_vs_freq.page{}.png'.format(plotdir, spw, page))



def check_cal(vis=None, fdmspw=None, tdmspws=None, calibrator_fields=None, 
              refant=None, detail=2, ydatacolumn='corrected',
              bandpass_calibrator=None, phase_calibrator=None,
              science_field=None, flux_calibrator=None, plot_tsys=False, 
              plot_freq=False, plot_time=False, plot_bandpass=False,
              plot_solutions=False, plot_target=False, plot_uvdist=False,
              overwrite=True, showgui=False, dpi=600, plotdir='./plots'):
    """check the calibrated data after applycal
    the wrapped plotms for self calibration

    Parameters
    ----------
    vis : str
        measurements file
    fdmspw : str
        the spw of frequency domain mode
    tdmspws : str
        the spws of time domain mode, the spws used for tsys calibration 
        usually 128 channels.
        example: '1,3,4', '1~3'
    spw : str
        the spw used in the plots
        example: '1,3,4', '1~3'
    calibrator_fields : list
        a list contains all the fields of calibrators
        example: ['0', '2', '3'] or ['J1427-4206', 'Mars']
    science_field : str
        the fields of the science target
        example: 'Cen*' or '4~22'
    ydatacolumn : str
        the ydatacolumn of `plotms`
    detail : str
        what detail the plot generates
        0: gather all the antenna based information without set the `interactive`
        1: generates all the plots with `interactive`='antenna'
        2: generates all the plots with `interactive`='baseline', require `refant`
    refant : str
        the reference antenna, like 'CM03', 'DV48'
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
    
    # generates the antenna or baseline subgroups
    gridrows = int(np.ceil((len(ants)-1)/2))
    baselines = refant + '&*' # all the related baseline
    subgroup_num = 6
    gridrows = subgroup_num / 2 # default column number is 2
    if detail >= 1:
        ants_subgroups = group_antenna(ants, subgroup_num=subgroup_num)
    if detail >= 2:
        baselines_subgroups = group_antenna(ants, refant, subgroup_num=subgroup_num)

    if bandpass_calibrator:
        calibrator_fields = [bandpass_calibrator]

    # check the frequency based calibration, used be sinificant for Tsys calibration
    if plot_freq:
        print("Plot frequency related calibration for fields: {} ...".format(calibrator_fields))
        os.system('mkdir -p {}/freq/'.format(plotdir))
        os.system('mkdir -p {}/freq_corrected/'.format(plotdir))
        for yaxis in ['amp', 'phase']:
            for field in calibrator_fields:
                if detail == 1: # antenna based plots
                    for page, baseline in enumerate(ants_subgroups):
                        for spw_single in spw_expand(spw):
                            plotms(vis=vis, field=field, xaxis='frequency', yaxis=yaxis,
                                   spw=spw_single, avgtime='1e8', avgscan=True, coloraxis='corr',
                                   antenna=antenna, iteraxis='antenna', ydatacolumn=ydatacolumn,
                                   showgui=showgui, gridrows=gridrows, gridcols=2,
                                   dpi = dpi, overwrite=overwrite, verbose=False,
                                   plotfile='{}/freq_{}/field{}_amp_vs_freq.data.{}.png'.format(plotdir, ydatacolumn, field, page))

                if detail == 2: #baseline based plots
                    for page, baselines in enumerate(baselines_subgroups):
                        for spw_single in spw_expand(spw):
                            plotms(vis=vis, field=field, xaxis='frequency', yaxis=yaxis,
                                   spw=spw_single, avgtime='1e8', avgscan=True, coloraxis='corr',
                                   antenna=baselines, iteraxis='baseline', ydatacolumn=ydatacolumn,
                                   showgui=showgui, gridrows=gridrows, gridcols=2,
                                   dpi = dpi, overwrite=overwrite, verbose=False,
                                   plotfile='{}/freq_{}/field{}_amp_vs_freq.data.{}.png'.format(plotdir, ydatacolumn, field, page))

    # the phase should be significantly improved after bandpass calibration
    # especially for the phase calibrator
    # if phase_calibrator:
        # calibrator_fields = [phase_calibrator]
        # title = 'phase_calibrator: Amplitude vs Time'
    if plot_time:
        print("Plot time related calibration for fields: {} ...".format(calibrator_fields))
        os.system('mkdir -p {}/time/'.format(plotdir))
        os.system('mkdir -p {}/time_corrected/'.format(plotdir))
        for yaxis in ['amplitude', 'phase']:
            # plot the general consistency of each field
            if detail >= 0: 
                for field in calibrator_fields:
                    plotms(vis=vis, field=field, xaxis='time', yaxis=yaxis,
                           spw=fdmspw, avgchannel='1e8', coloraxis='corr',
                           ydatacolumn=ydatacolumn,
                           showgui=showgui, dpi = dpi, overwrite=overwrite,
                           plotfile='{}/time_{}/field{}_amp_vs_time.data.png'.format(plotdir, ydatacolumn, field))
            if detail >= 1: # antenna based plots
                for page, antenna in enumerate(ants_subgroups):
                    plotms(vis=vis, field=field, xaxis='time', yaxis=yaxis,
                           spw=fdmspw, avgchannel='1e8', coloraxis='corr',
                           antenna=antenna, iteraxis='antenna', ydatacolumn=ydatacolumn,
                           showgui=showgui, gridrows=gridrows, gridcols=2,
                           dpi = dpi, overwrite=overwrite,
                           plotfile='{}/time_{}/field{}_amp_vs_time.data.{}.png'.format(plotdir, ydatacolumn, field, page))
            if detail >= 2: # baseline based plots
                for field in calibrator_fields:
                    for page, baselines in enumerate(baselines_subgroups):
                        plotms(vis=vis, field=field, xaxis='time', yaxis=yaxis,
                               spw=fdmspw, avgchannel='1e8', coloraxis='corr',
                               antenna=baselines, iteraxis='baseline', ydatacolumn=ydatacolumn,
                               showgui=showgui, gridrows=gridrows, gridcols=2,
                               dpi = dpi, overwrite=overwrite,
                               plotfile='{}/time_{}/field{}_amp_vs_time.data.{}.png'.format(plotdir, ydatacolumn, field, page))

    if plot_tsys:
        os.system('mkdir -p {}/tsys/'.format(plotdir))
        # plot tsys vs time, to pick out bad antenna
        for page,antenna in enumerate(ants_subgroups):
            plotms(vis=vis+'.tsys', xaxis='time', yaxis='Tsys', 
                   coloraxis='spw', antenna=antenna,
                   gridcols=2, gridrows=gridrows, iteraxis='antenna',
                   showgui=showgui,
                   plotfile='{}/tsys/Tsys_vs_time.page{}.png'.format(plotdir, page))

            # plot tsys vs frequency
            if tdmspws is None:
                raise ValueError("No tdmspws founded!")
            for spw in spw_expand(tdmspws):
                plotms(vis=vis+'.tsys', xaxis='freq', yaxis='Tsys', spw=spw,
                       gridcols=2, gridrows=gridrows, iteraxis='antenna',
                       coloraxis='corr', antenna=antenna, showgui=showgui,
                       plotfile='{}/tsys/spw{}_tsys_vs_freq.page{}.png'.format(plotdir, spw, page))

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
        for page, antenna in enumerate(ants_subgroups):
            plotms(vis=vis+'.phase_inf.cal', xaxis='time', yaxis='phase',
                   coloraxis='corr', iteraxis='antenna', 
                   gridcols=2, gridrows=gridrows,
                   showgui=showgui, dpi=dpi, overwrite=overwrite, 
                   plotfile='{}/solutions/phase_inf_cal_page{}.png'.format(plotdir, page))

            # flux calibration table
            plotms(vis=vis+'.flux.cal', xaxis='time', yaxis='amp',
                   coloraxis='corr', iteraxis='antenna',
                   gridcols=2, gridrows=gridrows,
                   showgui=showgui, dpi=dpi, overwrite=overwrite,
                   plotfile='{}/solutions/flux_cal_page{}.png'.format(plotdir, page))
        
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


