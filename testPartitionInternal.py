#!/usr/bin/env python3

#import pretty_errors
from generateFingers import Edge, plotLinePoints, dxfFromDict
import matplotlib.pyplot as plt
import numpy as np
import ezdxf

boxInnerFootprint = [800.0, 600.0]
boxHeight = 50.0

materialThickness = 10.0
dogBoneDia = 3.175 + 0.5
dogBoneType = "I"
clearence = 0.2 / 2.0

layers = {}

##################
#
#  Divider
#
##################

wallOrigin = [boxInnerFootprint[1] / 2.0, 0.0]
wallOrigin = [materialThickness + clearence, 100.0]
wallOrigin = [clearence * 2.0, boxInnerFootprint[1] / 2.0]
divBot = Edge(4, -materialThickness, -clearence, boxInnerFootprint[0] - clearence * 4.0, 0.0)
divBot.genFingerPointsBone(dogBoneDia, dogBoneType, True)
divBot.rotateShiftElement("finger", wallOrigin)

divR = Edge(1, -materialThickness, -clearence, boxHeight, 0.0)
divR.genFingerPointsBone(dogBoneDia, dogBoneType, True)
divR.rotateShiftElement("finger", divBot.cordsFinger[-1], 90.0)

stopPoint = [[divBot.cordsFinger[0][0], divR.cordsFinger[-1][1], 0]]

divL = Edge(divR.numFingers, divR.fingerLength, divR.clearence, divR.span, 0.0)
divL.genFingerPointsBone(dogBoneDia, dogBoneType, True)
divL.rotateShiftElement("finger", stopPoint[0], 270.0)

divWall = np.concatenate([divBot.cordsFinger[:-1], divR.cordsFinger, divL.cordsFinger])
plotLinePoints(divWall, "line", color="c", marker="o")
layers["divider"] = divWall

##################
#
#  Generate Footprint
#
##################
footOrigin = [-materialThickness, -materialThickness]
fS = Edge(4, materialThickness, clearence, boxInnerFootprint[0], materialThickness)
fS.genFingerPointsBone(dogBoneDia, dogBoneType, False)
fS.rotateShiftElement("finger", footOrigin)

fE = Edge(5, materialThickness, clearence, boxInnerFootprint[1], materialThickness)
fE.genFingerPointsBone(dogBoneDia, dogBoneType, False)
fE.rotateShiftElement("finger", fS.cordsFinger[-1], 90.0)

fN = Edge(fS.numFingers, materialThickness, clearence, boxInnerFootprint[0], materialThickness)
fN.genFingerPointsBone(dogBoneDia, dogBoneType, False)
fN.rotateShiftElement("finger", fE.cordsFinger[-1], 180.0)

fW = Edge(fE.numFingers, materialThickness, clearence, boxInnerFootprint[1], materialThickness)
fW.genFingerPointsBone(dogBoneDia, dogBoneType, False)
fW.rotateShiftElement("finger", fN.cordsFinger[-1], 270.0)

foot = np.concatenate([fS.cordsFinger[:-1], fE.cordsFinger[:-1], fN.cordsFinger[:-1], fW.cordsFinger])
foot[-1] = [footOrigin[0], footOrigin[1], 0.0]

divBot.genHoleBone(materialThickness, clearence, dogBoneDia, dogBoneType)
divBot.rotateShiftElement("hole", [clearence * 2, boxInnerFootprint[1] / 2.0])

foot = [foot]
for hole in divBot.cordsHoles:
	foot.append(hole)

plotLinePoints(foot, "line")
layers["foot"] = foot

##################
#
#  South Wall
#
##################

wallOrigin = [0.0, 0.0]

sWall = Edge(fS.numFingers, -materialThickness, -clearence, boxInnerFootprint[0], 0.0)
sWall.genFingerPointsBone(dogBoneDia, dogBoneType, True)
sWall.rotateShiftElement("finger", wallOrigin)

sWallR = Edge(1, -materialThickness, -clearence, boxHeight, 0.0)
sWallR.genFingerPointsBone(dogBoneDia, dogBoneType, True)
sWallR.rotateShiftElement("finger", sWall.cordsFinger[-1], 90.0)

stopPoint = [[sWall.cordsFinger[0][0], sWallR.cordsFinger[-1][1], 0]]

sWallL = Edge(sWallR.numFingers, sWallR.fingerLength, sWallR.clearence, sWallR.span, 0.0)
sWallL.genFingerPointsBone(dogBoneDia, dogBoneType, True)
sWallL.rotateShiftElement("finger", stopPoint[0], 270.0)

southWall = np.concatenate([sWall.cordsFinger[:-1], sWallR.cordsFinger, sWallL.cordsFinger])
plotLinePoints(southWall, "line", color="c", marker="o")
layers["south"] = southWall

##################
#
#  West Wall
#
##################

wallOrigin = [0.0, -materialThickness]

wWall = Edge(fW.numFingers, materialThickness, -clearence, boxInnerFootprint[1], materialThickness)
wWall.genFingerPointsBone(dogBoneDia, dogBoneType, True)
wWall.rotateShiftElement("finger", wallOrigin, 90.0)

wWallR = Edge(1, -materialThickness, clearence, boxHeight, 0.0)
wWallR.genFingerPointsBone(dogBoneDia, dogBoneType, False)
wWallR.rotateShiftElement("finger", wWall.cordsFinger[-1])

stopPoint = [[wWallR.cordsFinger[-1][0], wWall.cordsFinger[0][1], 0]]

wWallL = Edge(wWallR.numFingers, wWallR.fingerLength, wWallR.clearence, wWallR.span, 0.0)
wWallL.genFingerPointsBone(dogBoneDia, dogBoneType, False)
wWallL.rotateShiftElement("finger", stopPoint[0], 180.0)

westWall = np.concatenate([wWall.cordsFinger[:-1], wWallR.cordsFinger, wWallL.cordsFinger])
westWall[-1] = [wallOrigin[0], wallOrigin[1], 0.0]

divR.genHoleBone(materialThickness, clearence, dogBoneDia, dogBoneType)
divR.rotateShiftElement("hole", [clearence, boxInnerFootprint[1] / 2.0])

westWall = [westWall]
for hole in divR.cordsHoles:
	westWall.append(hole)

plotLinePoints(westWall, "line", color="g", marker="o")
layers["west"] = westWall

plt.axis('scaled')
plt.tight_layout()
plt.show()

dxfFromDict(layers, "testDivBox.dxf")
