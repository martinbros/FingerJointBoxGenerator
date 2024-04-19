#!/usr/bin/env python3

#import pretty_errors
from generateFingers import Edge, plotLinePoints, dxfFromDict
import matplotlib.pyplot as plt
import numpy as np
import ezdxf

boxInnerFootprint = [600.0, 175.0]
trapBase = 600.0
boxHeight = 200.0

materialThickness = 10.0
materialThicknessBase = 19.0
dogBoneDia = 3.175 + 0.5
dogBoneType = "I"
clearence = 0.2 / 2.0
#clearence = 0.0

# Dimensions for the bearing race
marbleDia = 10.0
marbleBuffer = 4.0  # double this value is added to marbleDia to make race drill diameter
marbleNum = 16
raceRad = 250.0
raceBuffer = 10.0  # This value is distance of material added to inside and outside of race drill hole

# Dimensions of the rotation stopping arm
innerRad = raceRad - 30.0
armBase = 50.0
armEnd = 30.0
armLength = 50.0
armAngle = 45.0

if trapBase - boxInnerFootprint[1] != 0.0:
	angle = np.arctan(boxHeight / ((trapBase - boxInnerFootprint[1]) / 2.0))
else:
	angle = np.pi / 2.0

angleDeg = angle * (180.0 / np.pi)
hypotSpan = boxHeight / np.sin(angle)

smAngFingLen = materialThickness / np.sin(angle)  # Smaller angle, finger length
lgAngFingLen = materialThickness * (np.tan(np.pi / 2.0 - angle) + 1 / np.cos(np.pi / 2.0 - angle))  # Larger angle, finger Length

smAngOff = materialThickness / np.tan(angle)  # Smaller angle, backoff from vertex
lgAngOff = materialThickness / np.cos(np.pi / 2.0 - angle)  # Larger angle, backoff from vertex THIS ONE SHOULD BE 0 when angle is 90deg

layers = {}

##################
#
#  Generate Trapezoidal Wall
#
##################

wallOrigin = [boxInnerFootprint[1] / -2.0, 0.0]
tEdge = Edge(2, -materialThickness, clearence, boxInnerFootprint[1] - 2.0 * lgAngOff, lgAngOff)
tEdge.genFingerPointsBone(dogBoneDia, dogBoneType, False)
tEdge.rotateShiftElement("finger", wallOrigin)

rEdge = Edge(2, -materialThickness, clearence, hypotSpan, 0.0)
rEdge.genFingerPointsBone(dogBoneDia, dogBoneType, False)
rEdge.rotateShiftElement("finger", tEdge.cordsFinger[-1], -angleDeg)

bEdge = Edge(4, materialThickness, -clearence, trapBase, 0.0)
bEdge.genFingerPointsBone(dogBoneDia, dogBoneType, True)
bEdge.rotateShiftElement("finger", rEdge.cordsFinger[-1], 180.0)

lEdge = Edge(rEdge.numFingers, -materialThickness, clearence, rEdge.span, rEdge.extra)
lEdge.genFingerPointsBone(dogBoneDia, dogBoneType, False)
lEdge.rotateShiftElement("finger", bEdge.cordsFinger[-1], angleDeg)

trapWall = np.concatenate([tEdge.cordsFinger[:-1], rEdge.cordsFinger[:-1], bEdge.cordsFinger[:-1], lEdge.cordsFinger])
trapWall[-1] = [wallOrigin[0], wallOrigin[1], 0.0]

layers["trap"] = trapWall
#plotLinePoints(trapWall, "line", color="k", marker="o")

##################
#
#  Generate Top Surface
#
##################

wallOrigin = [0.0, 0.0]
shortEdge = Edge(tEdge.numFingers, -materialThickness, -clearence, tEdge.span, lgAngFingLen)
shortEdge.genFingerPointsBone(dogBoneDia, dogBoneType, True)
shortEdge.rotateShiftElement("finger", wallOrigin)

longEdge = Edge(4, lgAngFingLen, clearence, boxInnerFootprint[0] - materialThickness * 2.0, 0.0)
longEdge.genFingerPointsBone(dogBoneDia, dogBoneType, False)
longEdge.rotateShiftElement("finger", shortEdge.cordsFinger[-1], 90.0)

shortEdgeTop = Edge(shortEdge.numFingers, shortEdge.fingerLength, shortEdge.clearence, shortEdge.span, shortEdge.extra)
shortEdgeTop.genFingerPointsBone(dogBoneDia, dogBoneType, True)
shortEdgeTop.rotateShiftElement("finger", longEdge.cordsFinger[-1], 180.0)

longEdgeLeft = Edge(longEdge.numFingers, longEdge.fingerLength, longEdge.clearence, longEdge.span, longEdge.extra)
longEdgeLeft.genFingerPointsBone(dogBoneDia, dogBoneType, False)
longEdgeLeft.rotateShiftElement("finger", shortEdgeTop.cordsFinger[-1], 270.0)

platWall = np.concatenate([shortEdge.cordsFinger[:-1], longEdge.cordsFinger[:-1], shortEdgeTop.cordsFinger[:-1], longEdgeLeft.cordsFinger])
platWall[-1] = [wallOrigin[0], wallOrigin[1], 0.0]

layers["top"] = platWall
#plotLinePoints(platWall, "line", color="c", marker="o")

##################
#
#  Generate Angled Surface
#
##################

wallOrigin = [0.0, materialThickness]
angleEdge = Edge(rEdge.numFingers, -materialThickness, -clearence, hypotSpan, [-smAngOff, -lgAngOff])
angleEdge.genFingerPointsBone(dogBoneDia, dogBoneType, True)
angleEdge.rotateShiftElement("finger", wallOrigin)

baseEdge = Edge(4, -lgAngFingLen, -clearence, longEdge.span, 0.0)
baseEdge.genFingerPointsBone(dogBoneDia, dogBoneType, True)
baseEdge.rotateShiftElement("finger", angleEdge.cordsFinger[-1], 90.0)

angleEdgeTop = Edge(rEdge.numFingers, -materialThickness, -clearence, angleEdge.span, [-lgAngOff, -smAngOff])
angleEdgeTop.genFingerPointsBone(dogBoneDia, dogBoneType, True)
angleEdgeTop.rotateShiftElement("finger", baseEdge.cordsFinger[-1], 180.0)

topEdge = Edge(baseEdge.numFingers, -smAngFingLen, -clearence, baseEdge.span, 0.0)
topEdge.genFingerPointsBone(dogBoneDia, dogBoneType, True)
topEdge.rotateShiftElement("finger", angleEdgeTop.cordsFinger[-1], 270.0)

angledWall = np.concatenate([angleEdge.cordsFinger[:-1], baseEdge.cordsFinger[:-1], angleEdgeTop.cordsFinger[:-1], topEdge.cordsFinger])
angledWall[-1] = [wallOrigin[0], wallOrigin[1], 0.0]

layers["angled"] = angledWall 
#plotLinePoints(angledWall, "line", color="k", marker="o")

##################
#
#  Generate Mount Surface
#
##################

# trapezoid wall mate holes
bEdge.genHoleBone(materialThickness + clearence * 2.0, clearence, dogBoneDia, "H")
bEdge.rotateShiftElement("hole", [0.0, materialThickness / 2.0])

holeWidth = materialThickness * np.cos(np.pi / 2.0 - angle) + np.abs(topEdge.fingerLength) * np.cos(angle) + clearence * 2.0
holeOffsetFromEdge = materialThickness / np.sin(angle) + clearence
holeCenterLine = trapBase - holeOffsetFromEdge + (holeWidth / 2.0)

# angled wall mate holes
baseEdge.genHoleBone(holeWidth, clearence, dogBoneDia, "H")
baseEdge.rotateShiftElement("hole", [holeCenterLine, materialThickness], 90.0)

for hole in baseEdge.cordsHoles:
	bEdge.cordsHoles.append(hole)

mountHoles = bEdge.cordsHoles

bEdge.rotateShiftElement("hole", [bEdge.span, baseEdge.span + materialThickness * 2.0], 180.0)

for hole in bEdge.cordsHoles:
	mountHoles.append(hole)

# base outline
outline = np.array([[-materialThickness * 2.0, -materialThickness * 2.0, 0],
			[trapBase + materialThickness * 2.0, -materialThickness * 2.0, 0],
			[trapBase + materialThickness * 2.0, boxInnerFootprint[0] + materialThickness * 2.0, 0],
			[-materialThickness * 2.0, boxInnerFootprint[0] + materialThickness * 2.0, 0],
			[-materialThickness * 2.0, -materialThickness * 2.0, 0]])

mountHoles.append(outline)

# Inner Arm outline
yCord = np.sqrt(np.square(innerRad) - (np.square(armBase / 2.0)))
bulgeVal = (armBase / 2.0) / (innerRad - yCord)

circleArmPoints = np.array([[-armBase / 2.0, -yCord, -bulgeVal],
					[armBase / 2.0, -yCord, 0],
					[armEnd / 2.0, -yCord + armLength, 0],
					[-armEnd / 2.0, -yCord + armLength, 0],
					[-armBase / 2.0, -yCord, 0]])

shift = Edge(numFingers=1, fingerLength=1, clearence=1, span=1, extra=0)
circleArmPoints = shift.rotateAndShift(circleArmPoints, shiftOrigin=[trapBase / 2.0, boxInnerFootprint[0] / 2.0], angle=armAngle)

mountHoles.append(circleArmPoints)

layers["base"] = mountHoles
#plotLinePoints(mountHoles, "line", color="r")

##################
#
#  Generate Foot
#
##################

layers["foot"] = outline

drillPoints = {}
drillPoints["foot"] = np.array([[trapBase / 2.0, boxInnerFootprint[0] / 2.0, raceRad], [trapBase / 2.0, boxInnerFootprint[0] / 2.0, 30.0]])
drillPoints["base"] = np.array([[trapBase / 2.0, boxInnerFootprint[0] / 2.0, raceRad]])

#plotLinePoints(outline, "line", color="b")

##################
#
#  Generate race
#
##################

bearingHoles = []
bearingAngle = (2 * np.pi) / marbleNum

for num in range(marbleNum):
	xPoint = raceRad * np.cos(bearingAngle * num)
	yPoint = raceRad * np.sin(bearingAngle * num)
	bearingHoles.append([xPoint, yPoint, marbleDia / 2.0 + marbleBuffer])

bearingHoles.append([0, 0, raceRad + (marbleDia / 2.0 + marbleBuffer + raceBuffer)])
bearingHoles.append([0, 0, raceRad - (marbleDia / 2.0 + marbleBuffer + raceBuffer)])
bearingHoles = shift.rotateAndShift(np.array(bearingHoles), shiftOrigin=[trapBase / 2.0, boxInnerFootprint[0] / 2.0])
drillPoints["race"] = bearingHoles

plotLinePoints(np.array(bearingHoles), "circle", color="k")


##################
#
#  Generate DXF
#
##################

dxfFromDict(layers, "trapezoidBoxBaseClear.dxf", drillPoints)
plt.axis('scaled')
plt.tight_layout()
plt.show()
