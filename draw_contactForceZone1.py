# postSPI: YADE post-processing for axial soil-pipe interaction (ASPI).
# Copyright (C) 2026 Chang GUO <chang.guo@connect.polyu.hk> -- GPL v2 or later.
# See COPYRIGHT and LICENSE in this directory.

"""
Please run yade -j4 get_contactForcesZone1.py before running
python3 draw_contactForceZone1.py
"""
##########################################  
import numpy as np
from myCommonSavers import *
from myCommonFunction import *
from setting import *
import matplotlib.pyplot as plt
from matplotlib import rcParams

### Read necessary base data
boundaryDict=reader(boundaryDictPath)
positionList=reader(positionListPath)
ppPosDict=reader(ppPosDictPath)

### define and create path for saving
thisSavePath=contactForceZone1FigurePath
thisSavePathsvg=thisSavePath+'svg/'
checkPath(thisSavePath)
checkPath(thisSavePathsvg)

### define and get path for reading analysed data
thisReadName=contactForceZone1Path
dataName='contactForce'
fileName = os.listdir(thisReadName)
f = [i for i in fileName if dataName+'.data' in i]
f.sort()
dataName2='maxNormalForces'
maxNormalForces=reader(thisReadName+dataName2+'.data')
# Fixed colour-bar upper bound for the force chains [N].
maxNormalForceInHistory=5.4
setMinNormalForce=0.2
### initialize a mesh
thisMesh=mesh_xz(200,boundaryDict,positionList)

### common plt setting
config = {
    "font.family":'Arial',
    "font.size": 16,
    }
colorNum=10
from matplotlib.colors import LinearSegmentedColormap
minGrey=0.8
colors = [(minGrey, minGrey, minGrey), (0, 0, 0)]  # Gray to black
cmap = LinearSegmentedColormap.from_list("custom_gray_black", colors, N=256)
gap=10
n=0
for p in f:
    if (n%gap==0 or n ==83):
        pathHead=p.replace(dataName+'.data','')
        ppPos=ppPosDict[pathHead]
        displacement=int(p.replace(dataName+'.data',''))
        ppDisplacement=displacement/10000.0
        print(f'Now analyse the condition of axial displacement is {displacement}')

        rcParams.update(config)
        fig1, ax1 = plt.subplots(figsize=(6.5,10))
        
        contactList=reader(thisReadName+p)
        # Sort data by force in descending order to plot darker lines first
        contactList.sort(key=lambda x: x[2],reverse=1)
        num=int(len(contactList)*0.4)

        contactList=contactList[:num]
        contactList.sort(key=lambda x: x[2],reverse=0)
        normalForces=[i[2] for i in contactList]
        for pos1,pos2,normalForce in contactList:
            if normalForce>setMinNormalForce:
                color_value = int((normalForce / maxNormalForceInHistory) * (colorNum-1)) / (colorNum-1)
                ax1.plot(
                    [pos1[0],pos2[0]],[pos1[2],pos2[2]],
                    linewidth=normalForce/maxNormalForceInHistory*8, 
                    color=cmap(color_value),
                    zorder=5)
        
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=setMinNormalForce, vmax=maxNormalForceInHistory))
        sm.set_array([])
        cbar = plt.colorbar(sm,extend='both')
        # Set color bar ticks to ten discrete intervals
        ticks=np.linspace(setMinNormalForce, maxNormalForceInHistory, num=colorNum+1)
        cbar.set_ticks(ticks)
        cbar.set_ticklabels([f'{round(tick,2):.2f}' for tick in ticks])
        cbar.cmap.set_under('white')
        draw_half_circle_outline(ax1, [ppPos[0],ppPos[2]], ppR, 2,edgecolor='black',fill=1)

        plt.xticks([])
        plt.yticks([])

        ax1.set(xlim=thisMesh.abx, ylim=thisMesh.abz)

        for spine in ax1.spines.values():
            spine.set_zorder(15)
        ax1.set_aspect('equal')
        plt.tight_layout()

        figName=thisSavePath+pathHead
        fig1.savefig(figName+'.png', dpi=300)
        print("save figure: "+figName+'.png')
        fig1.savefig(thisSavePathsvg+str(int(float(ppDisplacement)*10000)).zfill(3)+'.svg')
        plt.close()

    n+=1
