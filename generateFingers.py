#!/usr/bin/env python3

import pretty_errors
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

    def holeDistances(self, width, numHoles):

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

    def drillPoints(self, drillNum, invertDrill, widths):

        drillSpace = [self.holeDistances(width, drillNum) for width in widths]
        drillSpace = [x for xs in drillSpace for x in xs]  # Flatten list
        drillSpace[0] = drillSpace[0] + self.extra  # add extra onto the first point
        drillSpace = np.cumsum(drillSpace)
        drillSpace = np.delete(drillSpace, slice(drillNum, None, drillNum + 1))

        if invertDrill:
            mask = np.tile(np.concatenate(
                                        (np.full((1, drillNum), True)[0],
                                        np.full((1, drillNum), False)[0])
                                        ), self.numFingers + 1)[:-drillNum]
        else:
            mask = np.tile(np.concatenate(
                                        (np.full((1, drillNum), False)[0],
                                        np.full((1, drillNum), True)[0])
                                        ), self.numFingers + 1)[:-drillNum]

        return drillSpace[mask]

    def rotateAndShift(self, points, shiftOrigin=[0.0, 0.0], angle=0.0):

        try:
            x, y, b = points.T
        except ValueError:
            x, y = points.T

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
            points_matrix = np.hstack([np.dstack((x, y))[0], np.ones((len(x), 1))]).T

            # apply the transformation to the points
            transformed_points = transformation_matrix @ points_matrix

            x = transformed_points[0]
            y = transformed_points[1]

        x = x + shiftOrigin[0]
        y = y + shiftOrigin[1]

        if "b" in locals():
            return np.dstack((x, y, b))[0]
        else:
            return np.dstack((x, y))[0]

    def rotateShiftElement(self, element, shiftOrigin=[0.0, 0.0], angle=0.0):
        if element == "finger":
            if hasattr(self, "cordsFinger"):
                self.cordsFinger = self.rotateAndShift(self.cordsFinger, shiftOrigin, angle)

            if hasattr(self, "cordsDrill"):
                self.cordsDrill = self.rotateAndShift(self.cordsDrill, shiftOrigin, angle)

        elif element == "hole":
            if hasattr(self, "cordsHoles"):
                holePoints = []
                for hole in self.cordsHoles:
                    holePoints.append(self.rotateAndShift(hole, shiftOrigin, angle))
                self.cordsHoles = holePoints

            if hasattr(self, "cordsHolesDrill"):
                self.cordsHolesDrill = self.rotateAndShift(self.cordsHolesDrill, shiftOrigin, angle)

        else:
            print("Need to give element to rotate")

    def genFingerPoints(self):
        self.xList = np.tile([self.unit - 2.0 * self.clearence, self.unit + self.clearence * 2.0], self.numFingers + 1)[:-1]  # Create a tile of finger/gap widths
        self.xList[0] = self.xList[0] + self.clearence + self.extra  # For the first and last gaps, add on clearence and extra
        self.xList[-1] = self.xList[-1] + self.clearence + self.extra
        self.xList = np.cumsum(self.xList)  # Generate all of the x-points from the widths
        self.xList = np.repeat(self.xList, 2.0)[:-1]  # Repeat x points for the fingers
        self.xList = np.insert(self.xList, 0, 0.0)  # Insert the starting point

        self.yList = np.tile([0.0, 0.0, self.fingerLength, self.fingerLength], self.numFingers + 1)[:-2]

        self.fingerPoints = np.dstack((self.xList, self.yList))[0]

    def genFingerPointsBone(self, dogBoneDia=0.0, dogBoneType=None, invertBone=False, drillNum=False):

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

        self.cordsFinger = np.dstack((self.xList, self.yList, self.bulgeList))[0]

        if drillNum:
            finWidths = np.tile([self.unit - 2.0 * self.clearence, self.unit + self.clearence * 2.0], self.numFingers + 1)[:-1]  # Create a tile of finger/gap widths
            finWidths[0] = finWidths[0] + self.clearence  # For the first and last gaps, add on clearence, do not inlude extra
            finWidths[-1] = finWidths[-1] + self.clearence

            drillXPoints = self.drillPoints(drillNum=drillNum, invertDrill=not invertBone, widths=finWidths)  # Generate the x points
            self.cordsDrill = np.dstack((drillXPoints, np.full((1, len(drillXPoints)), self.fingerLength / 2.0)))[0]

    def genHoleBone(self, materialThick, clearence, dogBoneDia, dogBoneType=None, invertHoles=False, openEnds=False, drillNum=False):

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
            pairList = pairList[::2]  # Every other pair, starting with first
        else:
            pairList = pairList[1::2]  # Every other pair, starting with second

        self.cordsHoles = []
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

            self.cordsHoles.append(hole)

        if drillNum:
            finWidths = np.tile([self.unit - 2.0 * clearence, self.unit + clearence * 2.0], self.numFingers + 1)[:-1]  # Create a tile of finger/gap widths
            finWidths[0] = finWidths[0] + clearence  # For the first and last gaps, add on clearence, do not inlude extra
            finWidths[-1] = finWidths[-1] + clearence

            drillXPoints = self.drillPoints(drillNum=drillNum, invertDrill=not invertHoles, widths=finWidths)  # Generate the x points
            self.cordsHolesDrill = np.dstack((drillXPoints, np.full((1, len(drillXPoints)), 0.0 / 2.0)))[0]


def plotLinePoints(points, plotType, color="k", marker="o"):

    if len(points[0]) <= 3:  # Check if first element is a point
        try:
            x, y, b = points.T
        except ValueError:
            x, y = points.T

        if plotType == "line":
            plt.plot(x, y, color=color, marker=marker)
        elif plotType == "scatter":
            plt.scatter(x, y, color=color, marker=marker)

    else:  # iterate thorough array of array of points
        for hole in points:
            x, y, b = hole.T

            if plotType == "line":
                plt.plot(x, y, color=color, marker=marker)
            elif plotType == "scatter":
                plt.scatter(x, y, color=color, marker=marker)

"""
bone = Edge(numFingers=100, fingerLength=20.0, clearence=-0.25, span=200, extra=0.0)
bone.genFingerPointsBone(8.0, "X", True, drillNum=1)
bone.rotateShiftElement(element="finger", shiftOrigin=[0.0, 0.0], angle=45.0)
plotLinePoints(bone.cordsFinger, "line")
plotLinePoints(bone.cordsDrill, "scatter", "r")

bone.genHoleBone(materialThick=8.0, clearence=5.0, dogBoneDia=3.0, dogBoneType="X", invertHoles=False, openEnds=False, drillNum=8)
bone.rotateShiftElement(element="hole", shiftOrigin=[0.0, 0.0], angle=45.0)
plotLinePoints(bone.cordsHoles, "line", "c")
plotLinePoints(bone.cordsHolesDrill, "scatter", "g")

plt.axis('scaled')
plt.show()
"""


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