# a collection of plots utils to inspect the data during calibratiion

# by Jianhang Chen
# cjhastro@gmail.com 
# last update: 21 Mar 2019


import os
import random
import numpy as np
from casa import tbtool, plotms, plotants

try:
    import analysisUtils as aU
    has_au = True
except:
    print('Warning: no analysisUtil found, some functions may not work')
    has_au = False


def spw_expand(spwstr, mapfun=None):
    """expand the spw string into a list

    Parameters
    ----------
    spwstr : str or list
        example: '1,3,4', '1~3', ['1','3','4']
    mapfun : function
        the function mapping to all the elements of the list before return

    Returns
    -------
    a list of single spws

    """
    if isinstance(spwstr, list):
        return spwstr
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
        spw_list = [spwstr]

    if callable(mapfun):
        spw_list = list(map(mapfun, spw_list))

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

def group_antenna(antenna_list=[], refant=None, subgroup_member=6):
    """group a large number of antenna into small subgroup

    It can be help to plot several baseline and antenna into one figure.

    Parameters
    ----------
    antenna_list : list
        the antennas to be included
    refant : str
        the reference antenna, if it is set, the returned subgroups are baseline groups
        if the refant is None, the returned subgroups are antenna groups
    subgroup_member : int
        the member number if the subgroup
    
    Returns
    -------
    A list of subgroups
    """
    # generate the baseline list
    if refant is not None:
        # generates the baseline groups based on the refant
        refant_idx = np.where(antenna_list == refant)
        # remove the refant from antenna_list
        antenna_list_new = np.delete(antenna_list, refant_idx)
        subgroups = []
        for i in range(0, len(antenna_list_new), subgroup_member):
            antbaseline = ''
            for j in range(0, subgroup_member):
                try:
                    antbaseline += '{}&{};'.format(refant, antenna_list_new[i+j])
                except:
                    pass
            subgroups.append(antbaseline[:-1]) #remove the last
    else:
        subgroups = []
        # generates the antenna groups
        for i in range(0, len(antenna_list), subgroup_member):
            antbaseline = ''
            for j in range(0, subgroup_member):
                try:
                    antbaseline += '{},'.format(antenna_list[i+j])
                except:
                    pass
            subgroups.append(antbaseline[:-1])
 
    return subgroups

def check_info(vis=None, showgui=False, plotdir='./plots', spw='',
               show_ants=True, show_mosaic=True, show_uvcoverage=True,
               show_time=True, show_channel=True, show_elevation=True):
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
    show_time : bool
        plot the all the amp vs time
    show_channel : bool
        plot the all the amp vs channel

    """
    os.system('mkdir -p {}/info'.format(plotdir))
    plotdir = plotdir + '/info'

    if show_ants:
        # Checking antenna position, choosing the reference antenna
        print('Plotting antenna positions...')
        plotants(vis=vis, figfile='{}/antpos.png'.format(plotdir))

    if show_mosaic and has_au:
        # For selecting phase center
        print("Plotting mosaic...")
        aU.plotmosaic(vis, figfile='{}/mosaic.png'.format(plotdir))

    if show_uvcoverage:
        print("Plotting u-v coverage...")
        plotms(vis=vis, xaxis='U', yaxis='V', coloraxis='field', 
               spw=spw, showgui=showgui, 
               plotfile='{}/uvcoverage.png'.format(plotdir),
               overwrite=True)
    if show_elevation:
        print("Plotting elevation with time...")
        # Checking the evevation, determine the need of elivation calibration
        plotms(vis=vis, xaxis='time', yaxis='elevation', spw=spw,
               avgchannel='1e6', coloraxis='field', 
               plotfile='{}/elevation.png'.format(plotdir), 
               showgui=showgui, overwrite=True)
    if show_time:
        print("Plotting amplitude vs time...")
        # checking the valid timerange of data
        plotms(vis=vis, xaxis='time', yaxis='amplitude', avgchannel='1e6', 
               spw=spw, coloraxis='field', showgui=showgui,
               plotfile='{}/amp_time.png'.format(plotdir),
               overwrite=True)
    if show_channel:
        print("Plotting amplitude vs channel")
        plotms(vis=vis, xaxis='channel', yaxis='amplitude', avgtime='1e6', 
               spw=spw, coloraxis='field',
               plotfile='{}/amp_channel.png'.format(plotdir), 
               showgui=showgui, overwrite=True)


def check_tsys(vis=None, tdmspws=None, ants_subgroups=None, gridcols=2, 
               gridrows=3, plotdir='./plots', showgui=False):
    """the stand alone plot function for tsys
    
    
    Parameters
    ----------
    vis : str
        visibility of the measurement file
    tdmspws : str
        time domain mode spws
    ants_subgroups : list
        the list contains the subgroups to be plot into one figure
    tdmspws : str
        time domain mode spws 
        for example: '2,3,4' or '2~3'
    gridrows : int
        the rows for subplots
    gridcols : int
        the columns for subplots
    plotdir : str
        the directory where to generate the plots
    showgui : bool
        set to "True" to open the gui window
    """
    if ants_subgroups is None:
        # Extract the antenna list from ms
        tb = tbtool()
        tb.open(vis+'/ANTENNA', nomodify=True)
        ants = tb.getcol('NAME')
        tb.close()
        
        ants_subgroups = group_antenna(ants, subgroup_member=gridrows*gridcols)

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
              ants=None, refant=None, detail=1, ydatacolumn='corrected',
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
        0: gather all the antenna based information without set the `interation`
        1: generates all the plots with `interation`='antenna'
        2: generates all the plots with `interation`='baseline', require `refant`
    ants : list
        all the antennas to be included
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
    if ants is None:
        tb = tbtool()
        tb.open(vis+'/ANTENNA', nomodify=True)
        ants = tb.getcol('NAME')
        tb.close()
    
    # generates the antenna or baseline subgroups
    gridcols = 2 # default
    subgroup_member = 6 # default
    gridrows = subgroup_member / gridcols # default column number is 2
    if detail >= 1:
        ants_subgroups = group_antenna(ants, subgroup_member=subgroup_member)
    if detail >= 2:
        if refant is None:
            refant = random.choice(ants)
            print('Warning: No refant specified, choose a random one!')
        baselines = refant + '&*' # all the related baseline
        baselines_subgroups = group_antenna(ants, refant, subgroup_member=subgroup_member)

    if bandpass_calibrator:
        calibrator_fields = [bandpass_calibrator]
    
    # plot the frequency related scatter
    if plot_freq:
        print("Plot frequency related calibration for fields: {} ...".format(calibrator_fields))
        os.system('mkdir -p {}/freq_{}/'.format(plotdir, ydatacolumn))
        for yaxis in ['amplitude', 'phase']:
            for field in calibrator_fields:
                if detail >= 0:
                    for spw_single in spw_expand(fdmspw):
                        plotms(vis=vis, field=field, xaxis='frequency', yaxis=yaxis,
                               spw=spw_single, avgtime='1e8', avgscan=True, coloraxis='corr',
                               ydatacolumn=ydatacolumn, showgui=showgui,
                               dpi = dpi, overwrite=overwrite, verbose=False,
                               plotfile='{}/freq_{}/field{}-spw{}-amp_vs_{}.all.png'.format(plotdir, ydatacolumn, field, spw_single, yaxis))

                if detail >= 1: # antenna based plots
                    for page, antenna in enumerate(ants_subgroups):
                        for spw_single in spw_expand(fdmspw):
                            plotms(vis=vis, field=field, xaxis='frequency', yaxis=yaxis,
                                   spw=spw_single, avgtime='1e8', avgscan=True, coloraxis='corr',
                                   antenna=antenna, iteraxis='antenna', ydatacolumn=ydatacolumn,
                                   showgui=showgui, gridrows=gridrows, gridcols=2,
                                   dpi = dpi, overwrite=overwrite, verbose=False,
                                   plotfile='{}/freq_{}/field{}-spw{}-amp_vs_{}.page{}.png'.format(plotdir, ydatacolumn, field, spw_single, yaxis, page))

                if detail >= 2: #baseline based plots
                    for page, baselines in enumerate(baselines_subgroups):
                        for spw_single in spw_expand(fdmspw):
                            plotms(vis=vis, field=field, xaxis='frequency', yaxis=yaxis,
                                   spw=spw_single, avgtime='1e8', avgscan=True, coloraxis='corr',
                                   antenna=baselines, iteraxis='baseline', ydatacolumn=ydatacolumn,
                                   showgui=showgui, gridrows=gridrows, gridcols=2,
                                   dpi = dpi, overwrite=overwrite, verbose=False,
                                   plotfile='{}/freq_{}/field{}-spw{}-amp_vs_{}.page{}.png'.format(plotdir, ydatacolumn, field, spw_single, yaxis, page))

    # the phase should be significantly improved after bandpass calibration
    # especially for the phase calibrator
    if plot_time:
        print("Plot time related calibration for fields: {} ...".format(calibrator_fields))
        os.system('mkdir -p {}/time_{}/'.format(plotdir, ydatacolumn))
        for yaxis in ['amplitude', 'phase']:
            # plot the general consistency of each field
            for field in calibrator_fields:
                if detail >= 0: 
                    for spw_single in spw_expand(fdmspw):
                        plotms(vis=vis, field=field, xaxis='time', yaxis=yaxis,
                               spw=spw_single, avgchannel='1e8', coloraxis='corr',
                               ydatacolumn=ydatacolumn,
                               showgui=showgui, dpi = dpi, overwrite=overwrite,
                               plotfile='{}/time_{}/field{}_{}_vs_time.png'.format(plotdir, ydatacolumn, field, yaxis))
                if detail >= 1: # antenna based plots
                    for page, antenna in enumerate(ants_subgroups):
                        for spw_single in spw_expand(fdmspw):
                            plotms(vis=vis, field=field, xaxis='time', yaxis=yaxis,
                                   spw=spw_single, avgchannel='1e8', coloraxis='corr',
                                   antenna=antenna, iteraxis='antenna', ydatacolumn=ydatacolumn,
                                   showgui=showgui, gridrows=gridrows, gridcols=2,
                                   dpi = dpi, overwrite=overwrite,
                                   plotfile='{}/time_{}/field{}_{}_vs_time.page{}.png'.format(plotdir, ydatacolumn, field, yaxis, page))
                if detail >= 2: # baseline based plots
                    for page, baselines in enumerate(baselines_subgroups):
                        for spw_single in spw_expand(fdmspw):
                            plotms(vis=vis, field=field, xaxis='time', yaxis=yaxis,
                                   spw=spw_single, avgchannel='1e8', coloraxis='corr',
                                   antenna=baselines, iteraxis='baseline', ydatacolumn=ydatacolumn,
                                   showgui=showgui, gridrows=gridrows, gridcols=2,
                                   dpi = dpi, overwrite=overwrite,
                                   plotfile='{}/time_{}/field{}_{}_vs_time.page{}.png'.format(plotdir, ydatacolumn, field, yaxis, page))

    if plot_tsys:
        # plot tsys vs time, to pick out bad antenna
        check_tsys(vis=vis, ants_subgroups=ants_subgroups, plotdir=plotdir, 
                   tdmspws=tdmspws, gridrows=gridrows, 
                   gridcols=gridcols, showgui=showgui)

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
               ydatacolumn=ydatacolumn, field=science_field,
               avgchannel='1e8', coloraxis='corr',
               plotfile = '{}/target/target_amp_vs_uvdist.png'.format(plotdir),
               showgui=showgui, dpi=dpi, overwrite=overwrite)
        for spw in spw_expand(fdmspw):
            plotms(vis=vis, xaxis='freq', yaxis='amp', spw=spw,
                   ydatacolumn=ydatacolumn, field=science_field,
                   avgtime='1e8', avgscan=True, coloraxis='corr',
                   plotfile='{}/target/target_amp_vs_freq.png'.format(plotdir),
                   showgui=showgui, dpi=dpi, overwrite=overwrite)


