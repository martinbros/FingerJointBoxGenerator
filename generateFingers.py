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

        try:
            if len(extra) == 2:
                self.extra = extra

        except TypeError:
            self.extra = [extra, extra]

        self.unit = span / (2.0 * numFingers + 1.0)

    def dogBoneCheck(self, dogBoneDia):  # Roughly implemented to check extra

        extraCheck = min(self.extra)

        while (not(2 * dogBoneDia < self.unit - 2.0 * self.clearence - 2.0 * self.boneCheck) or not(2 * dogBoneDia < self.unit - self.clearence + extraCheck)):
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
        drillSpace[0] = drillSpace[0] + self.extra[0]  # add extra onto the first point
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
        self.xList[0] = self.xList[0] + self.clearence + self.extra[0]  # For the first and last gaps, add on clearence and extra
        self.xList[-1] = self.xList[-1] + self.clearence + self.extra[1]
        self.xList = np.cumsum(self.xList)  # Generate all of the x-points from the widths
        self.xList = np.repeat(self.xList, 2.0)[:-1]  # Repeat x points for the fingers
        self.xList = np.insert(self.xList, 0, 0.0)  # Insert the starting point

        self.yList = np.tile([0.0, 0.0, self.fingerLength, self.fingerLength], self.numFingers + 1)[:-2]

        self.cordsFinger = np.dstack((self.xList, self.yList))[0]

    def genHXfingers(self, dogBoneDia, dogBoneType, invertBone):

        if dogBoneType == "H":
            boneX = dogBoneDia
            boneY = 0.0
            self.boneCheck = dogBoneDia / 2.0

        elif dogBoneType == "X":
            boneX = dogBoneDia * (1.0 / np.sqrt(2))
            boneY = dogBoneDia * (1.0 / np.sqrt(2)) * (self.fingerLength / np.abs(self.fingerLength))
            self.boneCheck = dogBoneDia * (1 / 2.0) - dogBoneDia * (1.0 / np.sqrt(2)) * (1 / 2.0)

        self.dogBoneCheck(dogBoneDia)
        fullBot = self.unit - 2.0 * self.clearence
        fullTop = self.unit + 2.0 * self.clearence

        if invertBone:  # Dogbone is on the bottom
            xBetBone = fullBot - 2 * boneX
            xTile = [boneX, xBetBone, boneX, fullTop]
            xRepeat = np.tile([1, 1, 2, 2], self.numFingers + 1)[:-1]
            xRepeat[-1] = 1
            xCutdown = -1
            xInsert = False

            yTile = [0.0 + boneY, 0.0, 0.0, 0.0 + boneY, self.fingerLength, self.fingerLength]
            yCutdown = -2

            bulgeTile = [1, 0, 1, 0, 0, 0]
            bList = np.tile(bulgeTile, self.numFingers + 1)[:-2]
            # delete points at the end

        else:  # Dogbone is on the top
            xBetBone = fullTop - 2 * boneX
            xTile = [boneX, xBetBone, boneX, fullBot]
            xRepeat = np.tile([2, 1, 1, 2], self.numFingers + 1)[:-3]
            xRepeat[-1] = 1
            xCutdown = -4
            xInsert = fullBot

            yTile = [0.0, 0.0, self.fingerLength - boneY, self.fingerLength, self.fingerLength, self.fingerLength - boneY]
            yCutdown = -4

            bulgeTile = [0, 0, -1, 0, -1, 0]
            bList = np.tile(bulgeTile, self.numFingers + 1)[:-4]

        xList = np.tile(xTile, self.numFingers + 1)[:xCutdown]
        if xInsert:
            xList = np.insert(xList, 0, xInsert)
        xList[0] = xList[0] + self.clearence + self.extra[0]  # For the first and last horizontal, add on clearence and extra
        xList[-1] = xList[-1] + self.clearence + self.extra[1]
        xList = np.cumsum(xList)  # Generate all of the x-points from the widths
        xList = np.repeat(xList, xRepeat)  # Repeat the x-points for the corresponding y-points
        xList = np.insert(xList, 0, 0.0)  # Insert the starting point

        yList = np.tile(yTile, self.numFingers + 1)[:yCutdown]

        yList[0] = 0.0  # first and last points always zero
        yList[-1] = 0.0
        bList[0] = 0  # First point never bulges
        if invertBone:
            xList=np.delete(xList, [1, -2])
            yList=np.delete(yList, [1, -2])
            bList=np.delete(bList, [1, -2])

        return xList, yList, bList * (self.fingerLength / np.abs(self.fingerLength))

    def genFingerPointsBone(self, dogBoneDia, dogBoneType, invertBone, drillNum=False):

        if dogBoneType == "H":
            xList, yList, bulgeList = self.genHXfingers(dogBoneDia, dogBoneType, invertBone)

        elif dogBoneType == "X":
            xList, yList, bulgeList = self.genHXfingers(dogBoneDia, dogBoneType, invertBone)

        elif dogBoneType == "I":
            self.boneCheck = dogBoneDia / 2.0
            self.dogBoneCheck(dogBoneDia)
            fullBot = self.unit - 2.0 * self.clearence
            fullTop = self.unit + 2.0 * self.clearence

            if invertBone:  # Dogbone is on the bottom
                middleY = dogBoneDia * (self.fingerLength / np.abs(self.fingerLength))
                bulgeTile = [0, 1, 0, 0, 0, 1]
            else:  # Dogbone is on the top
                middleY = self.fingerLength - dogBoneDia * (self.fingerLength / np.abs(self.fingerLength))
                bulgeTile = [0, 0, -1, 0, -1, 0]

            xTile = [fullBot, fullTop]
            xRepeat = np.full(self.numFingers * 2 + 1, 3)
            yTile = [0.0, 0.0, middleY, self.fingerLength, self.fingerLength, middleY]

            xList = np.tile(xTile, self.numFingers + 1)[:-1]
            xList[0] = xList[0] + self.clearence + self.extra[0]  # For the first and last horizontal, add on clearence and extra
            xList[-1] = xList[-1] + self.clearence + self.extra[1]
            xList = np.cumsum(xList)  # Generate all of the x-points from the widths
            xList = np.repeat(xList, xRepeat)[:-2]  # Repeat the x-points for the corresponding y-points
            xList = np.insert(xList, 0, 0.0)  # Insert the starting point

            yList = np.tile(yTile, self.numFingers + 1)[:-4]

            bulgeList = np.tile(bulgeTile, self.numFingers + 1)[:-4] * (self.fingerLength / np.abs(self.fingerLength))
            bulgeList[-1] = 0

        else:
            print("Must specify dogbone type")

        self.cordsFinger = np.dstack((xList, yList, bulgeList))[0]

        if drillNum:
            finWidths = np.tile([self.unit - 2.0 * self.clearence, self.unit + self.clearence * 2.0], self.numFingers + 1)[:-1]  # Create a tile of finger/gap widths
            finWidths[0] = finWidths[0] + self.clearence  # For the first and last gaps, add on clearence, do not inlude extra
            finWidths[-1] = finWidths[-1] + self.clearence

            drillXPoints = self.drillPoints(drillNum=drillNum, invertDrill=not invertBone, widths=finWidths)  # Generate the x points
            self.cordsDrill = np.dstack((drillXPoints, np.full((1, len(drillXPoints)), self.fingerLength / 2.0)))[0]

    def genHoleBone(self, materialThick, clearence, dogBoneDia, dogBoneType, openEnds=False,  invertHoles=False, drillNum=False):

        if dogBoneType == "H":
            self.dogBoneOffsetX = dogBoneDia
            self.dogBoneOffsetY = 0.0

        elif dogBoneType == "I":
            self.dogBoneOffsetX = 0.0
            self.dogBoneOffsetY = dogBoneDia

        elif dogBoneType == "X":
            self.dogBoneOffsetX = dogBoneDia * (1.0 / np.sqrt(2))
            self.dogBoneOffsetY = dogBoneDia * (1.0 / np.sqrt(2))

        else:
            self.dogBoneOffsetX = 0.0
            self.dogBoneOffsetY = 0.0

        self.dogBoneCheck(dogBoneDia)

        yMax = np.abs(materialThick) / 2.0 + clearence
        yVal = yMax - self.dogBoneOffsetY

        self.xHole = np.tile([self.unit - 2.0 * clearence, self.unit + clearence * 2.0], self.numFingers + 1)[:-1]  # Create a tile of finger/gap widths
        self.xHole[0] = self.xHole[0] + clearence + self.extra[0]  # For the first and last gaps, add on clearence and extra
        self.xHole[-1] = self.xHole[-1] + clearence + self.extra[1]
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
                                 [xCords[1] - self.dogBoneOffsetX, yMax, -1],
                                 [xCords[1], yVal, 0],
                                 [xCords[1], -yVal, -1],
                                 [xCords[1] - self.dogBoneOffsetX, -yMax, 0],
                                 [xCords[0], -yMax, 0],
                                 ])
            elif openEnds and idx == len(pairList) - 1:
                hole = np.array([
                                [xCords[1], -yMax, 0],
                                [xCords[0] + self.dogBoneOffsetX, -yMax, -1],
                                [xCords[0], -yVal, 0],
                                [xCords[0], yVal, -1],
                                [xCords[0] + self.dogBoneOffsetX, +yMax, 0],
                                [xCords[1], yMax, 0],
                                ])

            else:
                hole = np.array([[xCords[0], yVal, -1],
                                 [xCords[0] + self.dogBoneOffsetX, yMax, 0],
                                 [xCords[1] - self.dogBoneOffsetX, yMax, -1],
                                 [xCords[1], yVal, 0],
                                 [xCords[1], -yVal, -1],
                                 [xCords[1] - self.dogBoneOffsetX, -yMax, 0],
                                 [xCords[0] + self.dogBoneOffsetX, -yMax, -1],
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


def dxfFromDict(pointDict, fileName, drillDict={}):

    doc = ezdxf.new(dxfversion='R2010')  # Create a new DXF document
    msp = doc.modelspace()

    dxfLayer = {}

    # Plot Fingers
    for layer in pointDict:
        dxfLayer[layer] = doc.layers.new(name=layer)  # Create Layer

        if len(pointDict[layer][0]) == 3:
            msp.add_lwpolyline(pointDict[layer], format="xyb", dxfattribs={'layer': dxfLayer[layer].dxf.name})
        else:
            for hole in pointDict[layer]:
                msp.add_lwpolyline(hole, format="xyb", dxfattribs={'layer': dxfLayer[layer].dxf.name})

    # Plot Drill Points
    for layer in drillDict:
        for point in drillDict[layer]:
            print(point[:2])
            print(point[2])
            msp.add_circle(point[:2], point[2], dxfattribs={'layer': dxfLayer[layer].dxf.name})

    doc.saveas(fileName)
