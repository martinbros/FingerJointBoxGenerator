#!/usr/bin/env python3

import pretty_errors
import numpy as np
from boxLib import *

class Edge:
    def __init__(self, origin, numFingers, fingerLength, clearence, span, extra, dogBoneDia):
        self.origin = origin
        self.numFingers = numFingers
        self.fingerLength = fingerLength
        self.clearence = clearence
        self.span = span
        self.extra = extra
        self.dogBoneDia = dogBoneDia
        
        self.unit = span / (2.0 * numFingers + 1.0)  # Need to check if unit is less than dogBoneDia
        #self.xList = np.empty((2 * numFingers + 1) * 2)
        #self.yList = np.empty((2 * numFingers + 1) * 2)
    
    def genFingerPoints(self):
        self.xList = np.tile([self.unit - 2.0 * self.clearence, self.unit + self.clearence * 2.0], self.numFingers + 1)[:-1] # Create a tile of finger/gap widths
        self.xList[0] = self.xList[0] + self.clearence + self.extra # For the first and last gaps, add on clearence and extra
        self.xList[-1] = self.xList[-1] + self.clearence + self.extra
        self.xList = np.cumsum(self.xList)  # Generate all of the x-points from the widths
        self.xList = np.repeat(self.xList, 2.0)[:-1]  # Repeat x points for the fingers
        self.xList = self.xList + self.origin[0]  # Shift the points according to the starting point
        self.xList = np.insert(self.xList, 0, self.origin[0])  # Insert the starting point
        
        self.yList = np.tile([self.origin[1], self.origin[1], self.origin[1] + self.fingerLength, self.origin[1] + self.fingerLength], self.numFingers + 1)[:-2]
        
    def genFingerPointsBone(self):
        self.dogBoneOffsetX = 1.0
        self.botHorz = self.unit - 2.0 * self.clearence - 2.0 * self.dogBoneOffsetX
        self.topHorz = self.unit + 2.0 * self.clearence - 2.0 * self.dogBoneOffsetX
                
        self.dogBoneOffsetY = 1.0
        self.botVert = self.origin[1] + self.dogBoneOffsetY
        self.topVert = self.origin[1] + self.fingerLength - self.dogBoneOffsetY
        self.fingerOut = self.origin[1] + self.fingerLength
        
        self.xList = np.tile([self.dogBoneOffsetX, self.botHorz, self.dogBoneOffsetX, self.dogBoneOffsetX, self.topHorz, self.dogBoneOffsetX], self.numFingers + 1)[:-3]
        self.xList[1] = self.xList[1] + self.clearence + self.extra # For the first and last horizontal, add on clearence and extra
        self.xList[-2] = self.xList[-2] + self.clearence + self.extra
        self.xList = np.cumsum(self.xList)  # Generate all of the x-points from the widths
                
        self.repeatList = np.tile([1, 1, 2], self.numFingers * 2 + 1)
        self.repeatList[-1] = 1
        self.xList = np.repeat(self.xList, self.repeatList)
        
        self.xList = self.xList + self.origin[0]  # Shift the points according to the starting point
        self.xList = np.insert(self.xList, 0, self.origin[0])  # Insert the starting point
        
        self.yList = np.tile([self.botVert, self.origin[1], self.origin[1], self.botVert, self.topVert, self.fingerOut, self.fingerOut, self.topVert], self.numFingers + 1)[:-4]
        self.yList[0] = self.origin[1]
        self.yList[-1] = self.origin[-1]
        
        
    
edgeA = Edge([0.0, 2.0], 3, 10.0, 0.5, 28.0, 0.0, 1.0)
edgeA.genFingerPointsBone()

edgeB = Edge([0.0, 0.0], edgeA.numFingers, 10.0, 0.0, edgeA.span, 0.0, 1.0)
edgeB.genFingerPoints()


plt.plot(edgeA.xList, edgeA.yList, color="k", marker="o")
plt.plot(edgeB.xList, edgeB.yList, color="g", marker="o")
plt.axis('scaled')
