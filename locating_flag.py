# Aim: A function for identifying tagged data (by plotms) to flag, read from the output in the logfile.
# Usage: under CASA;  version (>5.6)
# Within CASA:  plotms, select a region, click 'locate'. 
# Then the selected base information will shown in the log file and the message window. 
# Then the script will read the most frequent baselines and their statistics, 
# and output flagdata command for your choice.

# Example:
# execfile('locating_flag.py')

# Author: Zhi-Yu Zhang
# Email: pmozhang@gmail.com 
# History:
#   21 Mar 2019, update by Zhiyu
#   30 Sep 2019, transfer into function from the original script, by Jianhang
#   06 Feb 2020, update searching using Regular Expression  



import os
import glob
from   collections import Counter

def locating_flag(logfile):
    string       = open(logfile,'rU')
    AllLines     = str(string.readlines())
    LastEndNum   = AllLines.rfind('Plotting')
    LastEndNum   = max(AllLines.rfind(i) for i in ["Plotting", "END", "UVdist", "Time in"])# AllLines.rfind('Plotting')


    LastSection  = str(AllLines[LastEndNum:])
    ant1         = ''
    ant2         = ''
    corr         = ''
    ants         = []

    for line in LastSection.split('\\n'):
        if line.find('BL=')!=-1:
#          print("Both antennas are found")
          
           if line.find('@')!=-1:
              search = "@"
           else:
              search = "&"
           ant1  = re.compile("BL"    + b'(.*?)' + search    , re.S).findall(line)[0][1:].rstrip()
           ant2  = re.compile("&"     + b'(.*?)' + search    , re.S).findall(line)[0][1:].rstrip()
           scan  = re.compile("Scan"  + b'(.*?)' + "Field", re.S).findall(line)[0][1:].rstrip()
           field = re.compile("Field" + b'(.*?)' + "\["   , re.S).findall(line)[0][1:].rstrip()
           time  = re.compile("Time"  + b'(.*?)' + "BL"   , re.S).findall(line)[0][1:].rstrip()
           spw   = re.compile("Spw"   + b'(.*?)' + "Chan" , re.S).findall(line)[0][1:].rstrip()
           chan  = re.compile("Chan"  + b'(.*?)' + "Freq" , re.S).findall(line)[0][1:].rstrip()
           corr  = re.compile("Corr"  + b'(.*?)' + "X="   , re.S).findall(line)[0][1:].rstrip()
           ants.append(ant1)
           ants.append(ant2)
           print("flagdata(vis,mode='manual',antenna='"+ant1+"&"+ant2+"',correlation='"+corr+"', spw='"+spw+"',scan='"+scan+"',timerange='"+time+"')")
        elif line.find('ANT1=')!=-1:
           ant1  = re.compile("ANT1"  + b'(.*?)' + "&"    , re.S).findall(line)[0][1:].rstrip()
           scan  = re.compile("Scan"  + b'(.*?)' + "Field", re.S).findall(line)[0][1:].rstrip()
           field = re.compile("Field" + b'(.*?)' + "\["   , re.S).findall(line)[0][1:].rstrip()
           time  = re.compile("Time"  + b'(.*?)' + "ANT1" , re.S).findall(line)[0][1:].rstrip()
           spw   = re.compile("Spw"   + b'(.*?)' + "Chan" , re.S).findall(line)[0][1:].rstrip()
           chan  = re.compile("Chan"  + b'(.*?)' + "Freq" , re.S).findall(line)[0][1:].rstrip()
           corr  = re.compile("Corr"  +b'(.*?)'  + "X="   , re.S).findall(line)[0][1:].rstrip()
           ants.append(ant1)
           print("flagdata(vis,mode='manual',antenna='"+ant1+"&"+ant2+"',correlation='"+corr+"', spw='"+spw+"',scan='"+scan+"',timerange='"+time+"')")


    topten = Counter(ants).most_common(10)
    freq   = Counter(ants)


#   print("-----------------")
#   print(topten)
    print("-----------------")
    print("Most frequent antennas (NOT baselines) and their frequencies: ")
    print("                        ")
    

    most_baselines= [] 
    for idx in range(0,10):
        if len(topten) > idx:
            most_baselines.append(topten[idx][0])
            print(topten[idx][0], freq[topten[idx][0]])


    print("                        ")
    print("-----------------")
    print("Please complete your script, by adding info of correlations, spw, time, etc.")
    print("-----------------")
    for idx in range(0, len(most_baselines)):
        print("flagdata(vis, mode='manual',antenna='"+str(most_baselines[idx])+"',flagbackup=False)")
    print("-----------------")


    string.close()

if __name__ == '__main__':
    # directly run in ipython shell
    locating_flag(casalog.logfile())




    # #------ find the most common element from the list --
    # # https://stackoverflow.com/questions/1518522/find-the-most-common-element-in-a-list
    # def most_common(lst):
    #     return max(set(lst), key=lst.count)
    # print(most_common(ants))
    # # --------------------------------------------------



