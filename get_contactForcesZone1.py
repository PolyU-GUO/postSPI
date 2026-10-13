# postSPI: YADE post-processing for axial soil-pipe interaction (ASPI).
# Copyright (C) 2026 Chang GUO <chang.guo@connect.polyu.hk> -- GPL v2 or later.
# See COPYRIGHT and LICENSE in this directory.

'''
get_ file is used for get raw data from Yade
please run get_boundaryInfo.py and cal_particlesID.py before this code
yade -j4 get_contactForcesZone1.py
'''
from setting import *
from myCommonSavers import *

boundaryDict=reader(boundaryDictPath)
particlesID=reader(particlesIDPath)
particlesIDinZone1=[id for id in particlesID if id in boundaryDict['zone1IDs']]
boundaryList=[boundaryDict['wall_id_X0'],boundaryDict['wall_id_X1'],boundaryDict['wall_id_Z0'],boundaryDict['wall_id_Z1']]


### define and create path for saving
thisSavePath=contactForceZone1Path
dataName='contactForce'
checkPath(thisSavePath)
print(f'_ {dataName} data will be saved in {thisSavePath}.')
dataName2='maxNormalForces'
maxNormalForces=[]

n=0
gap=83
cover=1
for path in PPath:
    pathHead=path[path.find('Loadingn')+len('Loadingn'):path.find('Y')].zfill(3)
    if (n%gap==0 or n==1): # set path gap
        contactList=[]
        savePath=thisSavePath+pathHead+dataName+'.data'
        if cover or (not os.path.exists(savePath)):
            print(f'___Yade file: {path} is being loaded.')
            O.load(abspath+'/'+path)
            maxNormalForce=0.0
            for i in O.interactions:
                if (not (i.id1 in boundaryList)) and (not (i.id2 in boundaryList)) and ((i.id1 in particlesIDinZone1) or (i.id2 in particlesIDinZone1)):
                    pos1=list(O.bodies[i.id1].state.pos)
                    pos2=list(O.bodies[i.id2].state.pos)
                    if i.id1 in boundaryDict['shearbox_members']: pos1=list(i.geom.contactPoint)
                    elif i.id2 in boundaryDict['shearbox_members']: pos2=list(i.geom.contactPoint)
                    normalForce=i.phys.normalForce.norm()
                    contactList.append([pos1,pos2,normalForce])
                    maxNormalForce=max(maxNormalForce,normalForce)
            maxNormalForces.append(maxNormalForce)
            print(maxNormalForce)
            saver(contactList,savePath)
            print(f'______ {dataName} is saved to {savePath}.')
            saver(maxNormalForces,thisSavePath+dataName2+'.data')
            print(f'______ {dataName2} is saved to {thisSavePath+dataName2}.data')
    n+=1
