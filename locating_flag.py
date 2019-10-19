# funtion to identify flagging data from the output in the logfile

# Author: Zhi-Yu Zhang
# Email: pmozhang@gmail.com 
# History:
#   21 Mar 2019, update by Zhiyu
#   30 Sep 2019, transfer into function from the original script, by Jianhang

import os
import glob
from   collections import Counter

def locating_flag(logfile):
    string       = open(logfile,'rU')
    all          = str(string.readlines())
    LastEndNum   = all.rfind('End')
    LastSection  = str(all[LastEndNum:])

    ant1 = ''
    ant2 = ''
    corr = ''

    ants =[]

    for line in LastSection.split('\\n'):
        if line.find('BL=')!=-1:
           a    = line.find('BL=')
           b    = line.find('Corr=')
           c    = line.find('Time=')
           d    = line.find('Spw=')
           e    = line.find('Scan=')
           ant1 = str(line[a+3 :a+7 ])
           ant2 = str(line[a+15:a+19])
           ants.append(ant1)
           ants.append(ant2)
           corr = str(line[b+5 :b+7 ])
           time = str(line[c+16:c+29])
           spw  = str(line[d+4 :d+6 ])
           scan = str(line[e+5 :e+7 ])
    #      print("----")
           print("flagdata(vis,mode='manual',antenna='"+ant1+"&"+ant2+"',correlation='"+corr+"', spw='"+spw+"',scan='"+scan+"',timerange='"+time+"')")

    #print(sorted(ants, key=Counter(ants).get, reverse=True))

    topten = Counter(ants).most_common(3)
    freq = Counter(ants)

    print("-----------------")
    print(topten)
    print("-----------------")
    print("Most frequent antennas and their frequency: ")
    print("                        ")

    try:
        most_ant1 = topten[0][0]
        print(topten[0][0], freq[topten[0][0]])
        most_ant2 = topten[1][0]
        print(topten[1][0], freq[topten[1][0]])
        most_ant3 = topten[2][0]
        print(topten[2][0], freq[topten[2][0]])
    except:
        pass
    print("                        ")
    print("-----------------")
    print("flagdata(vis, mode='manual',antenna='"+str(most_ant1)+"')")
    print("-----------------")





    # #------ find the most common element from the list --
    # # https://stackoverflow.com/questions/1518522/find-the-most-common-element-in-a-list
    # def most_common(lst):
    #     return max(set(lst), key=lst.count)
    # print(most_common(ants))
    # # --------------------------------------------------


    string.close()

if __name__ == '__main__':
    # directly run in ipython shell
    locating_flag(casalog.logfile())
