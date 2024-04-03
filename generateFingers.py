#!/usr/bin/env python3

#import pretty_errors
import numpy as np
import ezdxf
import matplotlib.pyplot as plt

class Edge:
    def __init__(self, numFingers, fingerLength, clearence, span, extra):
        self.numFingers = numFingers
        self.fingerLength = fingerLength
        self.clearence = clearence
        self.span = span
        self.extra = extra

        self.unit = span / (2.0 * numFingers + 1.0)

    def dogBoneCheck(self, dogBoneDia):

        while (2.5 * dogBoneDia > self.unit - 2.0 * self.clearence - 2.0 * self.dogBoneOffsetX):
            self.numFingers -= 1
            self.unit = self.span / (2.0 * self.numFingers + 1.0)

    def genFingerPoints(self):
        self.xList = np.tile([self.unit - 2.0 * self.clearence, self.unit + self.clearence * 2.0], self.numFingers + 1)[:-1]  # Create a tile of finger/gap widths
        self.xList[0] = self.xList[0] + self.clearence + self.extra  # For the first and last gaps, add on clearence and extra
        self.xList[-1] = self.xList[-1] + self.clearence + self.extra
        self.xList = np.cumsum(self.xList)  # Generate all of the x-points from the widths
        self.xList = np.repeat(self.xList, 2.0)[:-1]  # Repeat x points for the fingers
        self.xList = np.insert(self.xList, 0, 0.0)  # Insert the starting point

        self.yList = np.tile([0.0, 0.0, self.fingerLength, self.fingerLength], self.numFingers + 1)[:-2]

        self.fingerPoints = np.dstack((self.xList, self.yList))[0]

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

        self.dogBoneCheck(dogBoneDia)
        self.topVert = self.fingerLength - self.dogBoneOffsetY

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
        self.xList[1] = self.xList[1] + self.clearence + self.extra  # For the first and last horizontal, add on clearence and extra
        self.xList[-2] = self.xList[-2] + self.clearence + self.extra
        self.xList = np.cumsum(self.xList)  # Generate all of the x-points from the widths

        self.repeatList = np.tile([1, 1, 2], self.numFingers * 2 + 1)
        self.repeatList[-1] = 1
        self.xList = np.repeat(self.xList, self.repeatList)

        self.xList = np.insert(self.xList, 0, 0.0)  # Insert the starting point

        self.yList = np.tile([self.dogBoneOffsetY, 0.0, 0.0, self.dogBoneOffsetY, self.topVert, self.fingerLength, self.fingerLength, self.topVert], self.numFingers + 1)[:-4]
        self.yList[0] = 0.0
        self.yList[-1] = 0.0

        self.fingerPoints = np.dstack((self.xList, self.yList, self.bulgeList))[0]

    def genHoleBone(self, materialThick, clearence, dogBoneDia, dogBoneType=None, invertHoles=False, openEnds=False):

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

        self.dogBoneCheck(dogBoneDia)

        yMax = materialThick / 2.0 + clearence
        yVal = yMax - self.dogBoneOffsetY

        self.xHole = np.tile([self.unit - 2.0 * clearence, self.unit + clearence * 2.0], self.numFingers + 1)[:-1]  # Create a tile of finger/gap widths
        self.xHole[0] = self.xHole[0] + clearence + self.extra  # For the first and last gaps, add on clearence and extra
        self.xHole[-1] = self.xHole[-1] + clearence + self.extra
        self.xHole = np.cumsum(self.xHole)  # Generate all of the x-point for the extent of the gaps
        self.xHole = np.insert(self.xHole, 0, 0.0)  # Insert the starting point

        pairList = list(zip(self.xHole, self.xHole[1:] + self.xHole[:1]))  # create pairs from the given x points, all iteratable pairs

        if invertHoles:
            pairList = pairList[::2]  # Every other pair, starting with frist
        else:
            pairList = pairList[1::2]  # Every other pair, starting with second

        self.holesPoints = []
        for idx, xCords in enumerate(pairList):

            if openEnds and idx == 0:
                hole = np.array([
                                 [xCords[0], yMax, 0],
                                 [xCords[1] - self.dogBoneOffsetX, yMax, 1],
                                 [xCords[1], yVal, 0],
                                 [xCords[1], -yVal, 1],
                                 [xCords[1] - self.dogBoneOffsetX, -yMax, 0],
                                 [xCords[0], -yMax, 0],
                                 ])
            elif openEnds and idx == len(pairList) - 1:
                hole = np.array([
                                [xCords[1], yMax, 0],
                                [xCords[0] + self.dogBoneOffsetX, yMax, 1],
                                [xCords[0], yVal, 0],
                                [xCords[0], -yVal, 1],
                                [xCords[0] + self.dogBoneOffsetX, -yMax, 0],
                                [xCords[1], -yMax, 0],
                                ])

            else:
                hole = np.array([[xCords[0], yVal, 1],
                                 [xCords[0] + self.dogBoneOffsetX, yMax, 0],
                                 [xCords[1] - self.dogBoneOffsetX, yMax, 1],
                                 [xCords[1], yVal, 0],
                                 [xCords[1], -yVal, 1],
                                 [xCords[1] - self.dogBoneOffsetX, -yMax, 0],
                                 [xCords[0] + self.dogBoneOffsetX, -yMax, 1],
                                 [xCords[0], -yVal, 0],
                                 [xCords[0], yVal, 0],
                                 ])

            x, y, b = hole.T
            plt.plot(x, y, color="c", marker="o")
            self.holesPoints.append(hole)

    def rotateAndShift(self, shiftOrigin=[0.0, 0.0], angle=0.0, ):

        if angle != 0.0:
            # convert angle to radians
            angle_rad = np.radians(angle)
            # create the rotation matrix
            rotation_matrix = np.array([[np.cos(angle_rad), -np.sin(angle_rad), 0],
                                        [np.sin(angle_rad), np.cos(angle_rad), 0],
                                        [0, 0, 1]])
            # concatenate the matrices to create the transformation matrix
            transformation_matrix = rotation_matrix
            # create a matrix of column vectors from the points
            points_matrix = np.hstack([np.dstack((self.xList, self.yList))[0], np.ones((len(self.xList), 1))]).T

            # apply the transformation to the points
            transformed_points = transformation_matrix @ points_matrix

            self.xList = transformed_points[0]
            self.yList = transformed_points[1]

        self.xList = self.xList + shiftOrigin[0]
        self.yList = self.yList + shiftOrigin[1]

        if hasattr(self, 'bulgeList'):
            self.fingerPoints = np.dstack((self.xList, self.yList, self.bulgeList))[0]
        else:
            self.fingerPoints = np.dstack((self.xList, self.yList))[0]


def plotHoles(holeArrays, color="k"):

    for hole in holeArrays:
        x, y, b = hole.T
        print(x)
        plt.plot(x, y, color=color, marker="o")


def holeLocations(width, numHoles):

    if numHoles == 0:
        return None

    elif numHoles == 1:
        return [width / 2.0, width / 2.0]

    else:
        bit = width / (numHoles)
        widths = []

        for x in range(numHoles + 1):
            if x == 0 or x == numHoles:
                widths.append(bit / 2.0)
            else:
                widths.append(bit)
        return widths


print(holeLocations(width=12.0, numHoles=4))

"""
edgeHT = Edge(3, -10.0, 0.5, 28.0, 0.0)
edgeHT.genFingerPointsBone(1.0, "H", True)
edgeHT.rotateAndShift([0.0, 1.0])

edgeHF = Edge(3, -10.0, 0.5, 28.0, 0.0)
edgeHF.genFingerPointsBone(1.0, "H", False)
edgeHF.rotateAndShift([0.0, 2.0])

edgeIT = Edge(3, -10.0, 0.5, 28.0, 0.0)
edgeIT.genFingerPointsBone(1.0, "I", True)
edgeIT.rotateAndShift([0.0, 3.0])

edgeIF = Edge(3, -10.0, 0.5, 28.0, 0.0)
edgeIF.genFingerPointsBone(1.0, "I", False)
edgeIF.rotateAndShift([0.0, 4.0])

edgeXT = Edge(3, -10.0, 0.5, 28.0, 0.0)
edgeXT.genFingerPointsBone(1.0, "X", True)
edgeXT.rotateAndShift([0.0, 5.0])

edgeXF = Edge(3, -10.0, 0.5, 28.0, 0.0)
edgeXF.genFingerPointsBone(1.0, "X", False)
edgeXF.rotateAndShift([0.0, 6.0])
"""

#edgeA = Edge(3, 10.0, -0.25, 28.0, 0.0)
#edgeA.genFingerPoints()

#edgeB = Edge(3, 10.0, 0.25, 28.0, 0.0)
#edgeB.genHoleBone(1.0, "X", 10.0, True, True)

#edgeXFF = Edge(3, -10.0, -0.25, 28.0, 0.0)
#edgeXFF.genFingerPointsBone(1.0, "X", False)

#edgeXFT = Edge(3, -10.0, +0.25, 28.0, 0.0)
#edgeXFT.genFingerPointsBone(1.0, "X", True)

#plt.plot(edgeA.xList, edgeA.yList, color="k", marker="o")
#plt.scatter(edgeB.xHole, edgeB.yList, color="b", marker="o")
#plt.plot(edgeXFF.xList, edgeXFF.yList, color="m", marker="o")
#plt.plot(edgeXFT.xList, edgeXFT.yList, color="r", marker="o")

#plt.plot(edgeHT.xList, edgeHT.yList, color="b", marker="o")
#plt.plot(edgeHF.xList, edgeHF.yList, color="g", marker="o")

#plt.plot(edgeIT.xList, edgeIT.yList, color="r", marker="o")
#plt.plot(edgeIF.xList, edgeIF.yList, color="c", marker="o")

#plt.plot(edgeXT.xList, edgeXT.yList, color="m", marker="o")
#plt.plot(edgeXF.xList, edgeXF.yList, color="violet", marker="o")


bone = Edge(100, 10.0, -0.25, 200.0, 0.0)
bone.genFingerPointsBone(8.0, "X", True)
plt.plot(bone.xList, bone.yList, color="k", marker="o")

bone.genHoleBone(materialThick=8.0, clearence=5.0, dogBoneDia=8.0, dogBoneType="X", invertHoles=False, openEnds=False)
#plotHoles(bone.holesPoints)

plt.axis('scaled')
"""
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
"""