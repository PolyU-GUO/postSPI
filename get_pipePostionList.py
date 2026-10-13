# postSPI: YADE post-processing for axial soil-pipe interaction (ASPI).
# Copyright (C) 2026 Chang GUO <chang.guo@connect.polyu.hk> -- GPL v2 or later.
# See COPYRIGHT and LICENSE in this directory.

'''
get_ file is used for get raw data from Yade
please run get_boundaryInfor.py before this code
yade -j4 get_pipePostionList.py
'''
from setting import *
from myCommonSavers import *
import numpy as np
boundaryDict=reader(boundaryDictPath)

checkPath(pipePostionPathRaw)
print(f'_pipe position data will be saved in {pipePostionPathRaw}.')
endName=ppPosEndName


targetWidthX=0.6
thickness=0.01 # bottom boundary thickness
boundaryGap=thickness*1.5
WidthX=targetWidthX+2*thickness+boundaryGap*2
WidthX0=WidthX/2
ppPosList0=WidthX0-targetWidthX / 2.0
n=0
gap=1
cover=False
for path in PPath:
    pathHead=path[path.find('Loadingn')+len('Loadingn'):path.find('Y')].zfill(3)
    if (n%gap==0): # set path gap
        savePath=pipePostionPathRaw+pathHead+endName
        if cover or (not os.path.exists(savePath)):
            print(f'___Yade file: {path} is being loaded.')
            O.load(abspath+'/'+path)
            ppPosList=list(O.bodies[boundaryDict['shearbox_id']].state.pos)
            ppPosList[0]=ppPosList0
            saver(ppPosList,savePath)
            print(f'______ppPosList is saved to {savePath}.')
    n+=1


f = os.listdir(pipePostionPathRaw)
f= [i for i in f if endName in i]
ppPosDict=dict()
for subPath in f:
    ppPosDict[subPath.replace(endName,'')]=reader(pipePostionPathRaw+subPath)

saver(ppPosDict,ppPosDictPath)
print(f'______ppPosDict is saved to {ppPosDictPath}.')