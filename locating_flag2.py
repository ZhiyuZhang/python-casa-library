# funtion to identify flagging data from the output in the logfile

# Author: Zhi-Yu Zhang, Jianhang Chen
# Email: pmozhang@gmail.com 
# History:
#   21 Mar 2019, update by Zhiyu
#   30 Sep 2019, transfer into function from the original script, by Jianhang
#    3 Dec 2019, match the logs by regex, Jianhang


import re
from collections import OrderedDict, Counter

version = '0.0.3'

def match_info(info_line, debug=False):
    """match the info of plotms selection
    """
    match_list = OrderedDict()
    match_list['scan']    = 'Scan=(?P<scan>\d+)\s'
    match_list['field']   = 'Field=(?P<field>[\w\s]+)\s\[(?P<field_id>\d+)\]\s'
    match_list['time']    = 'Time=(?P<time>[\w/:.]+)\s'
    match_list['baseline']= 'BL=(?P<ant1>\w+)@\w+\s&\s(?P<ant2>\w+)@\w+\s\[[\d&]+\]\s'
    match_list['spw']     = 'Spw=(?P<spw>\d+)\s'
    match_list['chan']    = 'Chan=(?P<chan>(\d+)|(<\d+~\d+>))\s'
    match_list['freq']    = '(Avg\s)*Freq=(?P<freq>[\d.]+)\s'
    match_list['corr']    = 'Corr=(?P<corr>\w+)\s'

    if debug:
        for item in match_list:
            p_match = re.compile(match_list[item])
            print("{:<10}: {}".format(item, p_match.search(info_line)))

    p_string = 'PlotMS::locate\+\s'
    for value in match_list.values():
        p_string = p_string + value
    p_info = re.compile(r"{}".format(p_string))
    info_matched = p_info.search(info_line)
    return info_matched.groupdict()

def pretty_output(counter):
    """make Couter output more readable

    """
    output = ''
    for item in counter:
        output += "{}[{}] ".format(item[0], item[1])
    return output


def locating_flag(logfile, n=5):
    """Searching flag information in logfile

    Parameters
    ----------
    logfile : str
        the filename of the log
    n : int
        the number of most common outputs

    """
    p_select = re.compile('Found (?P<n_select>\d+) points \((?P<n_unflagged>\d+) unflagged\)')
    p_overselect = re.compile('Only first (?P<n_over>\d+) points reported above')
    with open(logfile) as logfile:
        all_lines = logfile.readlines()
    for ind in range(len(all_lines) - 1, 0, -1):
        p_matched = p_select.search(all_lines[ind])
        if p_matched:
            p_overmatched = p_overselect.search(all_lines[(ind - 1)])
            if p_overmatched:
                n_select_start = ind - int(p_overmatched.groupdict()['n_over'])
            else:
                n_select_start = ind - int(p_matched.groupdict()['n_select'])
            n_select_end = ind
            break

    match_stat = {'ants':[], 'baselines':[], 'spws':[], 'corrs':[], 'chans':[]}
    ants_all = []
    baselines_all = []

    for line in all_lines[n_select_start:n_select_end]:
        info_matched = match_info(line)
        if info_matched:
            ant1 = info_matched['ant1']
            ant2 = info_matched['ant2']
            map(match_stat['ants'].append, [ant1, ant2])
            map(lambda x:match_stat['baselines'].append(x[0]+'&'+x[1]), [[ant1, ant2]])
            match_stat['corrs'].append(info_matched['corr'])
            match_stat['spws'].append(info_matched['spw'])
            match_stat['chans'].append(info_matched['chan'])

    for item in match_stat:
        print("Statistics for {}:\n{}\n".format(item, pretty_output(Counter(match_stat[item]).most_common(n))))

    # generate flagdata command
    flag_baseline = ''
    for baseline in Counter(match_stat['baselines']).most_common(n):
        flag_baseline += "{};".format(baseline[0])
    flag_corr = Counter(match_stat['corrs']).most_common(1)[0]

    print("flagdata(vis='', antenna='{}', corr='{}')".format(flag_baseline[:-1], flag_corr[0]))

if __name__ == '__main__':
    locating_flag(casalog.logfile())
