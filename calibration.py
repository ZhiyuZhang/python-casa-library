# This script try to run all the seperate FluxCalibration.py scripts and 
# concatenate all the outputing measurement files

# Author: Jianhang Chen
# Email: cjhastro@gmail.com

# History:
#   2019.09.30: first release

import os
import glob

scriptnames = glob.glob('uid*.ms.scriptForCalibration.py')
scriptasdms = []
for i in range(len(scriptnames)):
    scriptasdms.append(scriptnames[i].replace('.ms.scriptForCalibration.py', ''))

if os.path.exists('../calibrated_self'): 
    os.chdir('../calibrated_self')
else:
    os.mkdir('../calibrated_self')
    os.chdir('../calibrated_self')


for asdmname in scriptasdms:
    mystep = 0
    execfile('../script_self/'+asdmname+'.ms.scriptForCalibration.py')

vis_list = [vis+'.ms.split.calibrated' for vis in scriptasdms]
concat(vis = vis_list , concatvis = 'calibrated_self.ms', timesort = True)
