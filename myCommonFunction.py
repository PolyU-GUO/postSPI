# postSPI: YADE post-processing for axial soil-pipe interaction (ASPI).
# Copyright (C) 2026 Chang GUO <chang.guo@connect.polyu.hk> -- GPL v2 or later.
# See COPYRIGHT and LICENSE in this directory.

import math

import numpy as np


def moving_average_2d_with_weight(matrix, weights, window_size=3):
    if weights.shape != matrix.shape:
        raise ValueError("Weights matrix must have the same shape as the input matrix")

    padded_matrix = np.pad(matrix, pad_width=window_size // 2, mode='edge')
    padded_weights = np.pad(weights, pad_width=window_size // 2, mode='edge')
    smoothed_matrix = np.zeros_like(matrix)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if np.isnan(matrix[i, j]):
                smoothed_matrix[i, j] = matrix[i, j]
            else:
                window = padded_matrix[i:i + window_size, j:j + window_size]
                weight_window = padded_weights[i:i + window_size, j:j + window_size]
                valid_mask = ~np.isnan(window)
                valid_values = window[valid_mask]
                valid_weights = weight_window[valid_mask]
                if valid_values.size > 0:
                    smoothed_matrix[i, j] = np.average(valid_values, weights=valid_weights)
                else:
                    smoothed_matrix[i, j] = matrix[i, j]

    return smoothed_matrix


def draw_half_circle_outline(ax, center, radius, linewidth, edgecolor='black', fill=True, alpha=1, linestyle='-'):
    theta = np.linspace(-np.pi / 2, np.pi / 2, 100)

    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)

    if fill:
        ax.fill_betweenx(y, center[0], x, color='white', zorder=10)
    ax.plot(x, y, color=edgecolor, linewidth=linewidth, zorder=11, alpha=alpha, linestyle=linestyle)


def InCircle_xy(point, Center, radius):
    return ((point[0] - Center[0]) ** 2 + (point[1] - Center[1]) ** 2) < radius ** 2


def calFractionInPipe(point, Center, radius, smallMesh, smallMeshSize, smallMeshSideNum):
    inNum = 0
    for i in smallMesh:
        inNum += InCircle_xy([i[0] + point[0] + smallMeshSize / 2, i[1] + point[1] + smallMeshSize / 2], Center, radius)
    return 1 - inNum * 1.0 / smallMeshSideNum / smallMeshSideNum


def periodicialize(data, boundaryDict_cell, xyz='xyz'):
    if len(data) == len(xyz):
        data = list(data)
    else:
        raise ValueError("Input to function periodicialize is wrong. Please check.")
    checklist = []
    for i in xyz:
        if i == 'x':
            checklist.append(0)
        elif i == 'y':
            checklist.append(1)
        elif i == 'z':
            checklist.append(2)
    output = []
    for d, l in zip(data, checklist):
        output.append(d % boundaryDict_cell[l])
    return output


class mesh_xz:
    def __init__(self, level, boundaryDict, positionList, smallMeshSideNum=500, smallorlarge=1) -> None:
        self.aabbx = [boundaryDict['aabbmin'][0], boundaryDict['aabbmax'][0]]
        self.aabbz = [boundaryDict['aabbmin'][2], boundaryDict['aabbmax'][2]]
        self.zone1aabbmin = boundaryDict['zonesAABB'][0][0]
        self.zone1aabbmax = boundaryDict['zonesAABB'][0][1]
        self.level = level
        self.meshSize = (boundaryDict['aabbmax'][0] - boundaryDict['aabbmin'][0]) / self.level
        self.abx = [self.zone1aabbmin[0], self.zone1aabbmax[0] - 0.005]
        self.abz = [positionList[boundaryDict['shearbox_id']][2] - 0.07, positionList[boundaryDict['shearbox_id']][2] + 0.07]
        if smallorlarge != 0:
            self.thisAabbX = self.abx
            self.thisAabbZ = self.abz
        elif smallorlarge == 0:
            self.thisAabbX = self.aabbx
            self.thisAabbZ = self.aabbz
        self.xMesh = np.arange(self.thisAabbX[0], self.thisAabbX[1], self.meshSize)
        self.zMesh = np.arange(self.thisAabbZ[0], self.thisAabbZ[1], self.meshSize)
        self.xMeshNum = len(self.xMesh)
        self.zMeshNum = len(self.zMesh)
        self.meshAabbMin = [self.zone1aabbmin[0], self.zone1aabbmin[1], self.thisAabbZ[0]]
        self.smallMeshSideNum = smallMeshSideNum
        self.smallMeshSize = self.meshSize / self.smallMeshSideNum
        self.smallMesh = []
        for i in range(self.smallMeshSideNum):
            for j in range(self.smallMeshSideNum):
                self.smallMesh.append([i * self.smallMeshSize, j * self.smallMeshSize])
        self.meshVolume = self.meshSize * self.meshSize * boundaryDict['aabbmax'][1]
        self.space = [[self.meshVolume for j in range(self.xMeshNum)] for i in range(self.zMeshNum)]
        self.zone3aabbmin = boundaryDict['zonesAABB'][2][0]
        self.zone3aabbmax = boundaryDict['zonesAABB'][2][1]
        self.zone3aabbmin_meshed = self.meshilize(self.zone3aabbmin)
        self.zone3aabbmax_meshed = self.meshilize(self.zone3aabbmax)
        self.zone2aabbmin = boundaryDict['zonesAABB'][1][0]
        self.zone2aabbmax = boundaryDict['zonesAABB'][1][1]

    def updateSpace(self, ppCenter_xz, ppR, calTouchedMesh=False):
        self.ppCenter_x = ppCenter_xz[0]
        self.ppCenter_z = ppCenter_xz[1]
        for i in range(self.zMeshNum):
            for j in range(self.xMeshNum):
                Num = int(InCircle_xy([self.xMesh[j], self.zMesh[i]], ppCenter_xz, ppR)) \
                    + int(InCircle_xy([self.xMesh[j] + self.meshSize, self.zMesh[i]], ppCenter_xz, ppR)) \
                    + int(InCircle_xy([self.xMesh[j], self.zMesh[i] + self.meshSize], ppCenter_xz, ppR)) \
                    + int(InCircle_xy([self.xMesh[j] + self.meshSize, self.zMesh[i] + self.meshSize], ppCenter_xz, ppR))
                if Num == 4:
                    self.space[i][j] = np.nan
                elif Num == 0:
                    self.space[i][j] = self.meshVolume
                else:
                    if calTouchedMesh:
                        self.space[i][j] = calFractionInPipe([self.xMesh[j], self.zMesh[i]], ppCenter_xz, ppR, self.smallMesh, self.smallMeshSize, self.smallMeshSideNum) * self.meshVolume
                    else:
                        self.space[i][j] = np.nan

    def meshList(self, initialValue):
        return [[initialValue for j in range(self.xMeshNum)] for i in range(self.zMeshNum)]

    def meshilize(self, data):
        if len(data) != 3:
            raise ValueError("Input to method mesh_xz.meshilize is wrong. Please check.")
        return [(data[i] - self.meshAabbMin[i]) / self.meshSize for i in range(3)]

    def meshilize_length(self, data):
        return data / self.meshSize
