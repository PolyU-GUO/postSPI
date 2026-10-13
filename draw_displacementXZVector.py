# postSPI: YADE post-processing for axial soil-pipe interaction (ASPI).
# Copyright (C) 2026 Chang GUO <chang.guo@connect.polyu.hk> -- GPL v2 or later.
# See COPYRIGHT and LICENSE in this directory.

"""
Please run python3 cal_particlesID.py and yade -j4 get_posAndRot.py before running
python3 draw_displacementXZVector.py 
"""
##########################################  
from myCommonSavers import *
from setting import *
import matplotlib.pyplot as plt
from matplotlib import rcParams

### Read necessary base data
boundaryDict=reader(boundaryDictPath)
if targetSimulation=='R34':
    positionList1=reader(displacementPath+'001position.data')
else:
    positionList1=reader(positionListPath)

particlesID=reader(particlesIDPath)
particlesIDinZone1=[id for id in particlesID if id in boundaryDict['zone1IDs']]
ppPosDict=reader(ppPosDictPath)
sizeList=reader(sizeListPath)

### define and create path for saving
thisSavePath=displacementXZPath
thisSavePathsvg=thisSavePath+'svg/'
checkPath(thisSavePath)
checkPath(thisSavePathsvg)

### define and get path for reading analysed data
thisReadName=displacementPath
dataName='dis'
f = os.listdir(thisReadName)
f= [i for i in f if dataName+'.data' in i]
f.sort()

thisMesh=mesh_xz(200,boundaryDict,positionList1)

config = {
    "font.family":'Arial',
    "font.size": 16,
}

gap=100
n=0

x0 = []
z0 = []

for id in particlesIDinZone1:
    if positionList1[id][1]<0.003:
        x0.append(positionList1[id][0])
        z0.append(positionList1[id][2])
if targetSimulation=='R34':
    ppPos0z=ppPosDict['001'][2]
else:
    ppPos0z=ppPosDict['000'][2]
import matplotlib.colors as mcolors
norm = mcolors.Normalize(vmin=0, vmax=0.001)
for p in f:
    if (n%gap==0 and n !=0):
        pathHead=p.replace(dataName+'.data','')
        displacement=int(pathHead)
        ppDisplacement=displacement/10000.0
        ppPosz=ppPosDict[pathHead][2]
        disList=reader(displacementPath+p)
        print(f'Now analyse the condition of axial displacement is {displacement}')

        dx = []
        dz = []
        length = []
        for id in particlesIDinZone1:
            if positionList1[id][1]<0.003:
                dxx=disList[id][0]
                dzz=disList[id][2]
                dx.append(dxx)
                dz.append(dzz)
                length.append((dxx**2+dzz**2)**0.5)

        rcParams.update(config)

        fig1, ax1 = plt.subplots(figsize=(6.4,10))
        print(np.mean(length))
        a=ax1.quiver(x0, z0, # x, y position
            dx, dz, # dx,dy displacement 
            length,
            cmap='viridis',
            norm=norm,
            angles='xy', # determine angle based on 'xy': x, y to x+dx,y+dy; 'uv': 0,0 to dx,dy
            scale_units='xy',
            scale=0.2, # scale of vector length, 0.1 means 10 times, 10 means 1/10, 1is the real conditon
            width=.003, # size of vectors
            )
        
        cbar = plt.colorbar(a,extend='max')
        ticks = cbar.get_ticks()
        newticks = [tick *1000 for tick in ticks]

        cbar.set_ticks(ticks)
        cbar.set_ticklabels(['%.1f'%(nt) for nt in newticks])
        ppPos=ppPosDict[pathHead]
        draw_half_circle_outline(ax1, [ppPos[0],ppPos[2]], ppR, 2,edgecolor='black',fill=0, alpha=0.8)
        draw_half_circle_outline(ax1, [ppPos[0],ppPos[2]], ppR+0.0036, 3,edgecolor='black',fill=0, linestyle=':', alpha=0.8)

        plt.xticks([])
        plt.yticks([])

        ax1.set(xlim=thisMesh.abx, ylim=thisMesh.abz)
        ax1.set_aspect('equal')
        plt.tight_layout()

        figName=thisSavePath+pathHead
        plt.savefig(figName+'.png', dpi=300)
        print("save figure: "+figName+'.png')
        plt.savefig(thisSavePathsvg+pathHead+'.svg')
        plt.close()
    n+=1
