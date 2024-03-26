#!/usr/bin/env python3

import pretty_errors
import numpy as np
from boxLib import *

class Edge:
    def __init__(self, origin, numFingers, fingerLength, clearence, span, extra):
        self.origin = origin
        self.numFingers = numFingers
        self.fingerLength = fingerLength
        self.clearence = clearence
        self.span = span
        self.extra = extra
    
        self.xList = np.empty((2 * numFingers + 1) * 2)
        self.yList = np.empty((2 * numFingers + 1) * 2)
        self.unit = span / (2.0 * numFingers + 1.0)
    
    def genFingerPoints(self):
        self.xList = np.tile([self.unit - 2.0 * self.clearence, self.unit + self.clearence * 2.0], self.numFingers + 1)[:-1] # Create a tile of finger/gap widths
        self.xList[0] = self.xList[0] + self.clearence + self.extra # For the first and last gaps, add on clearence and extra
        self.xList[-1] = self.xList[-1] + self.clearence + self.extra
        self.xList = np.cumsum(self.xList)  # Generate all of the x-points from the widths
        self.xList = np.repeat(self.xList, 2.0)[:-1]  # Repeat x points for the fingers
        self.xList = self.xList + self.origin[0]  # Shift the points according to the starting point
        self.xList = np.insert(self.xList, 0, self.origin[0])  # Insert the starting point
        
        self.yList = np.tile([self.origin[1], self.origin[1], self.origin[1] + self.fingerLength, self.origin[1] + self.fingerLength], self.numFingers + 1)[:-2]
        
    
edgeA = Edge([0.0, 0.2], 5, 1.0, 0.5, 14.0, 0.0)
edgeA.genFingerPoints()

edgeB = Edge([0.0, 0.0], edgeA.numFingers, 1.0, 0.0, edgeA.span, 0.0)
edgeB.genFingerPoints()


plt.plot(edgeA.xList, edgeA.yList, color="k")
plt.plot(edgeB.xList, edgeB.yList, color="g")
