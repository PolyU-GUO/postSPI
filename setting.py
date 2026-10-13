# postSPI: YADE post-processing for axial soil-pipe interaction (ASPI).
# Copyright (C) 2026 Chang GUO <chang.guo@connect.polyu.hk> -- GPL v2 or later.
# See COPYRIGHT and LICENSE in this directory.

from myCommonFunction import *
import os
targetSimulation=os.environ.get('TARGET_SIMULATION','R34A025')

OutDiameter=0.102
ppR=OutDiameter/2.0
targetWidthX=0.6
targetHeightZ1=0.71 # top
targetHeightZ0=0.3 # pipe's center position
thickness=0.01 # bottom boundary thickness
boundaryGap=thickness*1.5
WidthX=targetWidthX+2*thickness+boundaryGap*2
WidthX0=WidthX/2
HeightZ0=targetHeightZ0+boundaryGap+thickness*1 # pipe center's height
HeightZ1=targetHeightZ1+boundaryGap+thickness*1.5 # height of sample

##################################################
# Nominal pressure at the pipe centre [kPa]. The simulation label encodes it
# (R34 / S34 / M34 -> 34 kPa); set it explicitly for your own case.
simulationPressure=34
Knaught=1-math.sin(math.radians(39.6))
K0Pressure=Knaught*simulationPressure
mainPaths=dict()
with open('paths.txt') as f:
    lines=f.readlines()
    for line in lines:
        mainPaths[line[0:line.find(':')]]=line[line.find(':')+1:].strip()

abspath=mainPaths[targetSimulation]
postPath=abspath+'/post'
boundaryDictPath=postPath+'/boundaryDict.data'
particlesIDPath=postPath+'/particlesID.data'
pressureMatrixPath=postPath+'/pressureMatrix/rawData/'
pressureMatrix_net_Path=postPath+'/pressureMatrix_net/rawData/'
pressureMatrixZone5Path=postPath+'/pressureMatrixZone5/rawData/'
pressureMatrixZone5_net_Path=postPath+'/pressureMatrixZone5_net/rawData/'
pressureMatrixZone5_cap_Path=postPath+'/pressureMatrixZone5_cap/rawData/'
pressureMatrix_zone1_vertical_path=postPath+'/pressureMatrix/zone1/vertical/'
pressureMatrix_zone1_lateral_path=postPath+'/pressureMatrix/zone1/lateral/'
pressureMatrix_zone5_vertical_path=postPath+'/pressureMatrix/zone5/vertical/'
pressureMatrix_zone5_vertical_net_path=postPath+'/pressureMatrix_net/zone5/vertical/'
pressureMatrix_zone5_vertical_cap_path=postPath+'/pressureMatrix_cap/zone5/vertical/'
pressureMatrix_earth_path=postPath+'/pressureMatrix/earth/'
pressureMatrix_zone3_principal_path=postPath+'/pressureMatrix/zone3/principal/'
pressureMatrix_zone5_lateral_path=postPath+'/pressureMatrix/zone5/lateral/'
pressureMatrix_zone5_lateral_net_path=postPath+'/pressureMatrix_net/zone5/lateral/'
pressureMatrix_zone5_lateral_cap_path=postPath+'/pressureMatrix_cap/zone5/lateral/'
positionListPath=postPath+'/positionList.data'
internaledPositionListPath=postPath+'/internaledPositionList.data'
voidRatio_zone1_path=postPath+'/Void/Zone1/'
centerAndRadiusPathZone1=postPath+'/centerAndRadius/rawData/zone1/'
anglePosListPath=postPath+'/anglePosList.data'
contactForcePath=postPath+'/contactForce/rawData/'
watercontentPath=postPath+'/waterContent/rawData/'
contactForceZone1Path=postPath+'/contactForce/rawData/Zone1/'
contactForceZone1_cap_Path=postPath+'/contactForce_cap/rawData/Zone1/'
contactForceDataPath=postPath+'/contactForce/data/'
contactForceFigurePath=postPath+'/contactForce/Fig/'
contactForceZone1FigurePath=postPath+'/contactForce/Fig/Zone1/'
contactForceZone1Figure_cap_Path=postPath+'/contactForce_cap/Fig/Zone1/'
contactForceZone1yzFigurePath=postPath+'/contactForce/Fig/Zone1yz/'
displacement_Y_zone5Path=postPath+'/displacement/displacementY/Zone5/'
displacementListPath = postPath+'/displacement/'
displacementXZPath=postPath+'/displacement/displacementXZ/'
displacementPath=postPath+'/displacement/rawData/'
sizeListPath=postPath+'/sizeList.data'
rotation_Y_zone5Path=postPath+'/rotation/rotationY/Zone5/'
rotationPath=postPath+'/rotation/rawData/'
pipePostionPath=postPath+'/pipePostion/'
pipePostionPathRaw=pipePostionPath+'rawData/'
ppPosDictPath=postPath+'/pipePostion/sumppPos.data'
forceOnPipePath=postPath+'/forceOnPipe/rawData/'
print('**********************************************')
print('Post-analysis of '+targetSimulation+' in '+abspath)

checkPath(postPath+'/paths')
internalPath=list()
externalPath=list()
PPath=list()
for dirpath, dirnames, filenames in os.walk(abspath, topdown=True):
    # 清空 dirnames 列表，这样 os.walk 就不会进入子文件夹
    dirnames.clear()
    for filename in filenames:
        if '/' in filename:
            continue
        if 'timeSaver' in filename:
            continue
        if ".yade.bz2" in filename:
            if 'externaled' in filename:
                externalPath.append(filename)
            elif 'internaled' in filename:
                internalPath.append(filename)
            elif 'P' in filename:
                PPath.append(filename)
tempList=list()
for i in PPath:
    s=i.split('N')[1].split('Y')[0]
    if 'Loadingn' in s:
        tempList.append([int(s.split('Loadingn')[0]),'L',int(s.split('Loadingn')[1]),i])
    else:
        tempList.append([int(s.split('Unloadingn')[0]),'U',int(s.split('Unloadingn')[1]),i])
PPathList=sorted(tempList,key=lambda x:(x[0],x[1],x[2]))
PPathNum,PPath=zip(*[[i[2],i[3]] for i in PPathList])

def get_ppDisplacement(cycNum, LorU, pathHead):
    matches = []
    for i in PPath:
        if 'N'+str(int(cycNum))+LorU in i and 'n'+str(int(pathHead))+'Y' in i:
            matches.append(i.split('Y')[-1].split('.yade.bz2')[0])
    if len(matches) == 0:
        raise ValueError(f"No match found for cycNum={cycNum}, LorU={LorU}, pathHead={pathHead}")
    elif len(matches) > 1:
        raise ValueError(f"Multiple matches found ({len(matches)}): {matches}")
    return matches[0]


forceOnPipeEndName='forceOnPipe.data'
ppPosEndName='ppPos.data'