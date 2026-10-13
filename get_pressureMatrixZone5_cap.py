# postSPI: YADE post-processing for axial soil-pipe interaction (ASPI).
# Copyright (C) 2026 Chang GUO <chang.guo@connect.polyu.hk> -- GPL v2 or later.
# See COPYRIGHT and LICENSE in this directory.

'''
get_ file is used for get raw data from Yade
please run yade -j4 get_boundaryInfo.py and python3 cal_particlesID.py before this code
yade -j4 get_pressureMatrixZone5_cap.py
'''
from setting import *
from myCommonSavers import *
import numpy as np
boundaryDict=reader(boundaryDictPath)

thisSavePath=pressureMatrixZone5_cap_Path
checkPath(thisSavePath)
dataName='pressureMatrixZone5_cap'
print(f'_ {dataName} data will be saved in {thisSavePath}.')
particlesID=reader(particlesIDPath)

n=0
gap=83
cover=False
for path in PPath:
    pathHead=path[path.find('Loadingn')+len('Loadingn'):path.find('Y')].zfill(3)
    if (n%gap==0): # set path gap
        savePath=thisSavePath+pathHead+dataName+'.data'
        if cover or (not os.path.exists(savePath)):
            print(f'___Yade file: {path} is being loaded.')
            O.load(abspath+'/'+path)

            pressureMatrixZone5_net_List=[]
            for i in O.interactions:
                if i.isReal and i.isActive:
                    if (i.id1 in particlesID) or (i.id2 in particlesID):
                        pressureMatrixZone5_net=(i.phys.fCap).outer(O.bodies[i.id1].state.pos-O.bodies[i.id2].state.pos)
                        pressureMatrixZone5_net_List.append([list(i.geom.contactPoint),[list(i) for i in list(pressureMatrixZone5_net)]])
            saver(pressureMatrixZone5_net_List,savePath)
            print(f'______ {dataName} List is saved to {savePath}.')
    n+=1



