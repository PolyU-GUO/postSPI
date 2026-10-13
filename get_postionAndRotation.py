# postSPI: YADE post-processing for axial soil-pipe interaction (ASPI).
# Copyright (C) 2026 Chang GUO <chang.guo@connect.polyu.hk> -- GPL v2 or later.
# See COPYRIGHT and LICENSE in this directory.

'''
get_ file is used for get raw data from Yade
please run get_boundaryInfor.py before this code
yade -j4 get_postionAndRotation.py
'''
from setting import *
from myCommonSavers import *
import numpy as np
boundaryDict=reader(boundaryDictPath)
checkPath(displacementPath)
print(f'_displacement data will be saved in {displacementPath}.')

checkPath(rotationPath)
print(f'_rotation data will be saved in {rotationPath}.')

n=0
gap=200
cover=False
for path in PPath:
    pathHead=path[path.find('Loadingn')+len('Loadingn'):path.find('Y')].zfill(3)
    if (n%gap==0): # set path gap
        
        print(f'___Yade file: {path} is being loaded.')
        O.load(abspath+'/'+path)

        savePath=displacementPath+pathHead+'dis.data'
        if cover or (not os.path.exists(savePath)):
            disList=[list(b.state.displ()) for b in O.bodies]
            saver(disList,savePath)
            print(f'______disList is saved to {savePath}.')

        savePath=rotationPath+pathHead+'rot.data'
        if cover or (not os.path.exists(savePath)):
            rotList=[list(b.state.rot()) for b in O.bodies]
            saver(rotList,savePath)
            print(f'______rotList is saved to {savePath}.')
    n+=1


