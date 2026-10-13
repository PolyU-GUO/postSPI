# postSPI: YADE post-processing for axial soil-pipe interaction (ASPI).
# Copyright (C) 2026 Chang GUO <chang.guo@connect.polyu.hk> -- GPL v2 or later.
# See COPYRIGHT and LICENSE in this directory.

"""
Please run yade -j4 get_pressureMatrixZone5.py before running
python3 draw_pressureMatrixZone5.py
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
thisSavePath=pressureMatrix_zone5_vertical_path
thisSavePathsvg=thisSavePath+'svg/'
checkPath(thisSavePath)
checkPath(thisSavePathsvg)

thisSavePath2=pressureMatrix_zone5_lateral_path
thisSavePath2svg=thisSavePath2+'svg/'
checkPath(thisSavePath2)
checkPath(thisSavePath2svg)
print(f'Figures of are saved in '+thisSavePath)

### define and get path for reading analysed data
thisReadName=pressureMatrixZone5Path
dataName='pressureMatrixZone5'
f = os.listdir(thisReadName)
f= [i for i in f if dataName+'.data' in i]
f.sort()

### initialize a mesh
thisMesh=mesh_xz(100,boundaryDict,positionList,smallorlarge=0)

### common plt setting
config = {
    "font.family":'Arial',
    "font.size": 16,
    }

gap=1
n=0
for p in f:
    if (n%gap==0 and n<=200)or n==83:
        pathHead=p.replace(dataName+'.data','')
        ppPos=ppPosDict[pathHead]
        displacement=int(pathHead)
        ppDisplacement=displacement/10000.0
        print(f'Now analyse the condition of axial displacement is {displacement}')

        thisMesh.updateSpace([ppPos[0],ppPos[2]],ppR,calTouchedMesh=1)
        pressures=thisMesh.meshList(0.0)
        pressures2=thisMesh.meshList(0.0)

        pressureMatrixList=reader(thisReadName+p)
        for contactPoint,pressureMatrix in pressureMatrixList:
            c=thisMesh.meshilize(periodicialize(contactPoint,boundaryDict_cell=boundaryDict['cell'],xyz='xyz'))
            if (0<=c[0]<thisMesh.xMeshNum) and (0<=c[2]<thisMesh.zMeshNum):
                i=int(c[2])
                j=int(c[0])
                pressures[i][j]+=pressureMatrix[2][2]
                pressures2[i][j]+=pressureMatrix[0][0]
        pressures=[[np.nan if thisMesh.space[i][j]==np.nan or thisMesh.space[i][j]==0.0 else -pressures[i][j]/thisMesh.space[i][j]/1000 for j in range(thisMesh.xMeshNum)]for i in range(thisMesh.zMeshNum)]
        window_size=8
        pressures=moving_average_2d_with_weight(np.array(pressures),np.array(thisMesh.space), window_size=window_size)

        pressures2=[[np.nan if thisMesh.space[i][j]==np.nan or thisMesh.space[i][j]==0.0 else -pressures2[i][j]/thisMesh.space[i][j]/1000 for j in range(thisMesh.xMeshNum)]for i in range(thisMesh.zMeshNum)]
        pressures2=moving_average_2d_with_weight(np.array(pressures2),np.array(thisMesh.space), window_size=window_size)

        rcParams.update(config)
        fig1, ax1 = plt.subplots(figsize=(7,10))
        print(np.nanmean(pressures))
        a=ax1.imshow(pressures,  interpolation='bilinear',cmap='viridis')
        ppR_meshed=thisMesh.meshilize_length(ppR)
        ppC_meshed=thisMesh.meshilize(ppPos)
        draw_half_circle_outline(ax1, [ppC_meshed[0]-0.5,ppC_meshed[2]-0.5], ppR_meshed, 8,edgecolor='black',fill=1)

        cbar=fig1.colorbar(a, ax=ax1,extend='max')
        cbar.mappable.set_clim(0,math.ceil((simulationPressure*3)/10.0)*10)

        plt.xticks([])
        plt.yticks([])

        ax1.set(xlim=[thisMesh.zone3aabbmin_meshed[0],thisMesh.zone3aabbmax_meshed[0]], ylim=[thisMesh.zone3aabbmin_meshed[2],thisMesh.zone3aabbmax_meshed[2]])
        ax1.set_aspect('equal')
        plt.tight_layout()

        figName=thisSavePath+pathHead
        fig1.savefig(figName+'.png', dpi=300)
        print("save figure: "+figName+'.png')
        fig1.savefig(thisSavePathsvg+pathHead+'.svg')
        plt.close()

        rcParams.update(config)
        fig1, ax1 = plt.subplots(figsize=(7,10))
        print(np.nanmean(pressures2))
        a=ax1.imshow(pressures2,  interpolation='bilinear',cmap='viridis')
        draw_half_circle_outline(ax1, [ppC_meshed[0]-0.5,ppC_meshed[2]-0.5], ppR_meshed, 8,edgecolor='black',fill=1)
        cbar=fig1.colorbar(a, ax=ax1,extend='max')
        cbar.mappable.set_clim(0,math.ceil((simulationPressure*3)/10.0)*10)


        plt.xticks([])
        plt.yticks([])

        ax1.set(xlim=[thisMesh.zone3aabbmin_meshed[0],thisMesh.zone3aabbmax_meshed[0]], ylim=[thisMesh.zone3aabbmin_meshed[2],thisMesh.zone3aabbmax_meshed[2]])
        ax1.set_aspect('equal')
        plt.tight_layout()

        figName=thisSavePath2+pathHead
        plt.savefig(figName+'.png', dpi=300)
        print("save figure: "+figName+'.png')
        plt.savefig(thisSavePath2svg+pathHead+'.svg')
        plt.close()
    n+=1
