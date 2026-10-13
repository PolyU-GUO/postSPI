# postSPI: YADE post-processing for axial soil-pipe interaction (ASPI).
# Copyright (C) 2026 Chang GUO <chang.guo@connect.polyu.hk> -- GPL v2 or later.
# See COPYRIGHT and LICENSE in this directory.


##########################################  
import numpy as np
from myCommonSavers import *
from setting import *
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
boundaryDict=reader(boundaryDictPath)
positionList=reader(positionListPath)

zone1Path=postPath+'/displacement/displacementY/Zone1/'
checkPath(zone1Path)
print(f'Figures of zone 1 are saved in '+zone1Path)
zone5Path=postPath+'/displacement/displacementY/Zone5/'
checkPath(zone5Path)
print(f'Figures of zone 5 are saved in '+zone5Path)

f = os.listdir(displacementPath)
f= [i for i in f if 'dis.data' in i]
f.sort()

aabbx=[boundaryDict['aabbmin'][0],boundaryDict['aabbmax'][0]]
aabbz=[boundaryDict['aabbmin'][2],boundaryDict['aabbmax'][2]]
zone1aabbmin=boundaryDict['zonesAABB'][0][0]
zone1aabbmax=boundaryDict['zonesAABB'][0][1]
abx=[zone1aabbmin[0],zone1aabbmax[0]]
abz=[zone1aabbmin[2],zone1aabbmax[2]]
sizeList=reader(sizeListPath)

gap=200
n=0
for p in f:
    if (n%gap==0):
        disList=reader(displacementPath+p)
        displacement=int(p.replace('dis.data',''))
        ppDisplacement=displacement/10000.0
        print(f'Now analyse the condition of axial displacement is {displacement}')
        x0 = []
        z0 = []
        dy = []
        size = []
        paID = boundaryDict['parIDs']
        for id in paID:
            if(disList[id][0]**2+disList[id][1]**2+disList[id][2]**2)**0.5<ppDisplacement*1.2:
                x0.append(positionList[id][0])
                z0.append(positionList[id][2])
                dy.append(disList[id][1])
                size.append((sizeList[id])**3/200.0)

        config = {
            "font.family":'Arial',
            "font.size": 16,
        }
        rcParams.update(config)

        fig1, ax1 = plt.subplots(figsize=(6.4,10))
        rdy=[i*1000 for i in dy]
        cmap=plt.get_cmap('bone_r')
        newcolors=cmap(np.linspace(0, 1, 256))
        newcmap = ListedColormap(newcolors[77:236]) 
        bounds = np.linspace(0, 20, 21)
        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=160)
        a=ax1.scatter(x0, z0, c=rdy, norm=norm,cmap=newcmap,s=size,alpha=1,edgecolors='none')
        cbar=fig1.colorbar(a, ax=ax1,ticks=[0, 2, 4, 6, 8,10,12,14,16,18,20],extend='both')
        cbar.ax.set_yticklabels(['0', '2', '4', '6', '8','10','12','14','16','18','20'])
        ax1.set(xlim=abx, ylim=abz)
        ax1.set_title('${u}$ = '+ '%.1f'%(float(ppDisplacement)*1000)+" mm")

        plt.xticks([])
        plt.yticks([])
        ax1.set_aspect('equal')
        plt.tight_layout()
        plt.savefig(str(int(float(ppDisplacement)*10000)).zfill(3)+'.png', dpi=300)
        print("save figure: "+str(int(float(ppDisplacement)*10000)).zfill(3)+'.png')

        plt.rcParams['figure.figsize']=(5.68,10)

        ax1.set(xlim=aabbx, ylim=aabbz)
        ax1.set_aspect('equal')
        plt.tight_layout()
        plt.savefig(str(int(float(ppDisplacement)*10000)).zfill(3)+'2.png', dpi=300)
        print("save figure: "+str(int(float(ppDisplacement)*10000)).zfill(3)+'2.png')
    n+=1
