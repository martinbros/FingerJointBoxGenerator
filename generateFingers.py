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
        
        self.unit = span / (2.0 * numFingers + 1.0)  # Need to check if unit is less than dogBoneDia
    
    def genFingerPoints(self):
        self.xList = np.tile([self.unit - 2.0 * self.clearence, self.unit + self.clearence * 2.0], self.numFingers + 1)[:-1] # Create a tile of finger/gap widths
        self.xList[0] = self.xList[0] + self.clearence + self.extra # For the first and last gaps, add on clearence and extra
        self.xList[-1] = self.xList[-1] + self.clearence + self.extra
        self.xList = np.cumsum(self.xList)  # Generate all of the x-points from the widths
        self.xList = np.repeat(self.xList, 2.0)[:-1]  # Repeat x points for the fingers
        self.xList = self.xList + self.origin[0]  # Shift the points according to the starting point
        self.xList = np.insert(self.xList, 0, self.origin[0])  # Insert the starting point
        
        self.yList = np.tile([self.origin[1], self.origin[1], self.origin[1] + self.fingerLength, self.origin[1] + self.fingerLength], self.numFingers + 1)[:-2]
        
    def genFingerPointsBone(self, dogBoneDia=0.0, dogBoneType=None, invertBone=False):
        
        if dogBoneType == "H":
            self.dogBoneOffsetX = dogBoneDia
            self.dogBoneOffsetY = 0.0
        
        elif dogBoneType == "I":
            self.dogBoneOffsetX = 0.0
            self.dogBoneOffsetY = dogBoneDia * (self.fingerLength / np.abs(self.fingerLength))
        
        elif dogBoneType == "X":
            self.dogBoneOffsetX = dogBoneDia * (1.0 / np.sqrt(2))
            self.dogBoneOffsetY = dogBoneDia * (1.0 / np.sqrt(2)) * (self.fingerLength / np.abs(self.fingerLength))
        
        else:
            self.dogBoneOffsetX = 0.0
            self.dogBoneOffsetY = 0.0
                       
        self.botVert = self.origin[1] + self.dogBoneOffsetY
        self.topVert = self.origin[1] + self.fingerLength - self.dogBoneOffsetY
        self.fingerOut = self.origin[1] + self.fingerLength
        
        if invertBone:  # dogbone is on the bottom
            self.bulgeList = np.tile([1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0], (self.numFingers + 1))[:-4] * (self.fingerLength / np.abs(self.fingerLength))
            self.bulgeList[0] = 0.0
            self.bulgeList[-2] = 0.0
            
            self.botHorz = self.unit - 2.0 * self.clearence - 2.0 * self.dogBoneOffsetX
            self.topHorz = self.unit + 2.0 * self.clearence
            
            elementWidths = [self.dogBoneOffsetX, self.botHorz, self.dogBoneOffsetX, 0.0, self.topHorz, 0.0]
        
        else:  # Dogbone is on the top
            self.bulgeList = np.tile([0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0], (self.numFingers + 1))[:-4] * -1 * (self.fingerLength / np.abs(self.fingerLength))
            
            self.botHorz = self.unit - 2.0 * self.clearence
            self.topHorz = self.unit + 2.0 * self.clearence - 2.0 * self.dogBoneOffsetX
            
            elementWidths = [0.0, self.botHorz, 0.0, self.dogBoneOffsetX, self.topHorz, self.dogBoneOffsetX]
                
             
        self.xList = np.tile(elementWidths, self.numFingers + 1)[:-3]
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
        
        self.fingerPoints = np.dstack((self.xList, self.yList, self.bulgeList))[0]
        
        
    
edgeHT = Edge([0.0, 1.0], 3, -10.0, 0.5, 28.0, 0.0)
edgeHT.genFingerPointsBone(1.0, "H", True)

edgeHF = Edge([0.0, 2.0], 3, -10.0, 0.5, 28.0, 0.0)
edgeHF.genFingerPointsBone(1.0, "H", False)

edgeIT = Edge([0.0, 3.0], 3, -10.0, 0.5, 28.0, 0.0)
edgeIT.genFingerPointsBone(1.0, "I", True)

edgeIF = Edge([0.0, 4.0], 3, -10.0, 0.5, 28.0, 0.0)
edgeIF.genFingerPointsBone(1.0, "I", False)

edgeXT = Edge([0.0, 5.0], 3, -10.0, 0.5, 28.0, 0.0)
edgeXT.genFingerPointsBone(1.0, "X", True)

edgeXF = Edge([0.0, 6.0], 3, -10.0, 0.5, 28.0, 0.0)
edgeXF.genFingerPointsBone(1.0, "X", False)

edgeA = Edge([0.0, 0.0], 3, 10.0, -0.25, 28.0, 0.0)
edgeA.genFingerPoints()

edgeB = Edge([0.0, 1.0], 3, 10.0, 0.25, 28.0, 0.0)
edgeB.genFingerPoints()


plt.plot(edgeA.xList, edgeA.yList, color="k", marker="o")
plt.plot(edgeB.xList, edgeB.yList, color="c", marker="o")

#plt.plot(edgeHT.xList, edgeHT.yList, color="b", marker="o")
#plt.plot(edgeHF.xList, edgeHF.yList, color="g", marker="o")

#plt.plot(edgeIT.xList, edgeIT.yList, color="r", marker="o")
#plt.plot(edgeIF.xList, edgeIF.yList, color="c", marker="o")

#plt.plot(edgeXT.xList, edgeXT.yList, color="m", marker="o")
#plt.plot(edgeXF.xList, edgeXF.yList, color="violet", marker="o")

plt.axis('scaled')

doc = ezdxf.new(dxfversion='R2010')  # Create a new DXF document
msp = doc.modelspace()

layerHT = doc.layers.new(name="HT")  # Create Layer
msp.add_lwpolyline(edgeHT.fingerPoints, format="xyb", dxfattribs={'layer': layerHT.dxf.name})

layerHF = doc.layers.new(name="HF")  # Create Layer
msp.add_lwpolyline(edgeHF.fingerPoints, format="xyb", dxfattribs={'layer': layerHF.dxf.name})

layerIT = doc.layers.new(name="IT")  # Create Layer
msp.add_lwpolyline(edgeIT.fingerPoints, format="xyb", dxfattribs={'layer': layerIT.dxf.name})

layerIF = doc.layers.new(name="IF")  # Create Layer
msp.add_lwpolyline(edgeIF.fingerPoints, format="xyb", dxfattribs={'layer': layerIF.dxf.name})

layerXT = doc.layers.new(name="XT")  # Create Layer
msp.add_lwpolyline(edgeXT.fingerPoints, format="xyb", dxfattribs={'layer': layerXT.dxf.name})

layerXF = doc.layers.new(name="XF")  # Create Layer
msp.add_lwpolyline(edgeXF.fingerPoints, format="xyb", dxfattribs={'layer': layerXF.dxf.name})

doc.saveas("testFile.dxf")
