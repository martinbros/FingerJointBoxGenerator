#!/usr/bin/env python3

#import pretty_errors
from generateFingers import Edge, plotLinePoints, dxfFromDict
import matplotlib.pyplot as plt
import numpy as np
import ezdxf
import os
import shutil
import sys

materialThickness = 12.5
materialThicknessBase = 18.5


dogBoneDia = (1.0 / 8.0) * 25.4 + 0.5
dogBoneType = "I"
clearence = -0.15 / 2.0  # Clearence for inbetween fingers
clearenceMaterial = -0.35 / 2.0  # Clearence for holes and material thickness
#clearence = 0.0

powerCableHoleDia = 40.0

# Extra distance for hold downs
tnutDia = 18.8  # Diameter of the wings
tnutOffset = 13.0  # From edge of wing to edge of hole
tnutDrillDia = 8.0
holdDownBuffer = 10.0
holdDownExtra = materialThickness + tnutOffset + holdDownBuffer

# Dimensions for overall stand form
lugCompLength = 600.0 + (holdDownExtra * 2.0)
boxInnerFootprint = [lugCompLength, 175.0]
trapBase = lugCompLength
boxHeight = 200.0
drillRad = 1.0

# Dimensions for the bearing cage
marbleDia = 1.0 * 25.6
marbleBuffer = 2.0  # double this value is added to marbleDia to make race drill diameter
marbleNum = 10
raceRad = (lugCompLength / 2.0) - marbleDia * 2.0
print(raceRad * 2.0)
raceBuffer = 10.0  # This value is distance of material added to inside and outside of race drill hole

# Dimensions of the rotation stopping arm
innerRad = raceRad - marbleDia / 2.0 - marbleBuffer - raceBuffer - 10.0
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

smAngFingLen = materialThicknessBase / np.sin(angle)  # Smaller angle, finger length
lgAngFingLen = materialThickness * (np.tan(np.pi / 2.0 - angle) + 1 / np.cos(np.pi / 2.0 - angle))  # Larger angle, finger Length

smAngOff = materialThickness / np.tan(angle)  # Smaller angle, backoff from vertex
lgAngOff = materialThickness / np.cos(np.pi / 2.0 - angle)  # Larger angle, backoff from vertex THIS ONE SHOULD BE 0 when angle is 90deg

saveFolder = sys.argv[1]

if not os.path.exists(saveFolder):
	os.makedirs(saveFolder)
else:
	for filename in os.listdir(saveFolder):
		file_path = os.path.join(saveFolder, filename)
		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path):
				shutil.rmtree(file_path)
		except Exception as e:
			print('Failed to delete %s. Reason: %s' % (file_path, e))

##################
#
#  Generate Trapezoidal Wall
#
##################

wallOrigin = [boxInnerFootprint[1] / -2.0, 0.0]
tEdge = Edge(2, -materialThickness, clearence, boxInnerFootprint[1] - 2.0 * lgAngOff, lgAngOff)
tEdge.genFingerPointsBone(dogBoneDia, dogBoneType, False, drillNum = 1)
tEdge.rotateShiftElement("finger", wallOrigin)

rEdge = Edge(2, -materialThickness, clearence, hypotSpan, 0.0)
rEdge.genFingerPointsBone(dogBoneDia, dogBoneType, False, drillNum = 1)
rEdge.rotateShiftElement("finger", tEdge.cordsFinger[-1], -angleDeg)

bEdge = Edge(4, materialThicknessBase, -clearence, trapBase, 0.0)
bEdge.genFingerPointsBone(dogBoneDia, dogBoneType, True)
bEdge.rotateShiftElement("finger", rEdge.cordsFinger[-1], 180.0)

lEdge = Edge(rEdge.numFingers, -materialThickness, clearence, rEdge.span, rEdge.extra)
lEdge.genFingerPointsBone(dogBoneDia, dogBoneType, False, drillNum = 1)
lEdge.rotateShiftElement("finger", bEdge.cordsFinger[-1], angleDeg)

trapWall = np.concatenate([tEdge.cordsFinger[:-1], rEdge.cordsFinger[:-1], bEdge.cordsFinger[:-1], lEdge.cordsFinger])
trapWall[-1] = [wallOrigin[0], wallOrigin[1], 0.0]

layers = {}
layers["trap"] = trapWall

drillList = np.concatenate([tEdge.cordsDrill, rEdge.cordsDrill, lEdge.cordsDrill])
drillRadList = np.full([drillList.shape[0], 1], drillRad)
drillPoints = {}
drillPoints["drill"] = np.append(drillList, drillRadList, axis=1)

drillPoints["power"] = np.array([[0.0, boxHeight / -2.0, powerCableHoleDia / 2.0]])

dxfFromDict(layers, saveFolder + "\\trapezoid.dxf", drillPoints)
#plotLinePoints(layers["trap"], "line", color="k", marker="o")
#plotLinePoints(drillPoints["drill"], "circle", color="k")
#plotLinePoints(drillPoints["power"], "circle", color="r")

##################
#
#  Generate Top Surface
#
##################

wallOrigin = [0.0, 0.0]
shortEdge = Edge(tEdge.numFingers, -materialThickness, -clearence, tEdge.span, lgAngFingLen)
shortEdge.genFingerPointsBone(dogBoneDia, dogBoneType, True, drillNum=1)
shortEdge.rotateShiftElement("finger", wallOrigin)

longEdge = Edge(4, lgAngFingLen, clearence, boxInnerFootprint[0] - materialThickness * 2.0, 0.0)
longEdge.genFingerPointsBone(dogBoneDia, dogBoneType, False)
longEdge.rotateShiftElement("finger", shortEdge.cordsFinger[-1], 90.0)

shortEdgeTop = Edge(shortEdge.numFingers, shortEdge.fingerLength, shortEdge.clearence, shortEdge.span, shortEdge.extra)
shortEdgeTop.genFingerPointsBone(dogBoneDia, dogBoneType, True, drillNum=1)
shortEdgeTop.rotateShiftElement("finger", longEdge.cordsFinger[-1], 180.0)

longEdgeLeft = Edge(longEdge.numFingers, longEdge.fingerLength, longEdge.clearence, longEdge.span, longEdge.extra)
longEdgeLeft.genFingerPointsBone(dogBoneDia, dogBoneType, False)
longEdgeLeft.rotateShiftElement("finger", shortEdgeTop.cordsFinger[-1], 270.0)

platWall = np.concatenate([shortEdge.cordsFinger[:-1], longEdge.cordsFinger[:-1], shortEdgeTop.cordsFinger[:-1], longEdgeLeft.cordsFinger])
platWall[-1] = [wallOrigin[0], wallOrigin[1], 0.0]

layers = {}
layers["top"] = platWall

drillList = np.concatenate([shortEdge.cordsDrill, shortEdgeTop.cordsDrill])
drillRadList = np.full([drillList.shape[0], 1], drillRad)
drillPoints = {}
drillPoints["drill"] = np.append(drillList, drillRadList, axis=1)

# Holddown Drill Points
drillPoints["hold"] = np.array([[lgAngFingLen + tEdge.span / 2.0, holdDownBuffer / 2.0 + tnutDia / 2.0, tnutDrillDia / 2.0],
								[lgAngFingLen + tEdge.span / 2.0, lugCompLength - materialThickness * 2.0 - (holdDownBuffer / 2.0 + tnutDia / 2.0), tnutDrillDia / 2.0]])

dxfFromDict(layers, saveFolder + "\\top.dxf", drillPoints)
#plotLinePoints(platWall, "line", color="c", marker="o")
#plotLinePoints(drillPoints["drill"], "circle", color="k")
#plotLinePoints(drillPoints["hold"], "circle", color="r")

##################
#
#  Generate Angled Surface
#
##################

wallOrigin = [0.0, materialThickness]
angleEdge = Edge(rEdge.numFingers, -materialThickness, -clearence, hypotSpan, [-smAngOff, -lgAngOff])
angleEdge.genFingerPointsBone(dogBoneDia, dogBoneType, True, drillNum=1)
angleEdge.rotateShiftElement("finger", wallOrigin)

baseEdge = Edge(4, -lgAngFingLen, -clearence, longEdge.span, 0.0)
baseEdge.genFingerPointsBone(dogBoneDia, dogBoneType, True)
baseEdge.rotateShiftElement("finger", angleEdge.cordsFinger[-1], 90.0)

angleEdgeTop = Edge(rEdge.numFingers, -materialThickness, -clearence, angleEdge.span, [-lgAngOff, -smAngOff])
angleEdgeTop.genFingerPointsBone(dogBoneDia, dogBoneType, True, drillNum=1)
angleEdgeTop.rotateShiftElement("finger", baseEdge.cordsFinger[-1], 180.0)

topEdge = Edge(baseEdge.numFingers, -smAngFingLen, -clearence, baseEdge.span, 0.0)
topEdge.genFingerPointsBone(dogBoneDia, dogBoneType, True)
topEdge.rotateShiftElement("finger", angleEdgeTop.cordsFinger[-1], 270.0)

angledWall = np.concatenate([angleEdge.cordsFinger[:-1], baseEdge.cordsFinger[:-1], angleEdgeTop.cordsFinger[:-1], topEdge.cordsFinger])
angledWall[-1] = [wallOrigin[0], wallOrigin[1], 0.0]

layers = {}
layers["angled"] = angledWall

drillList = np.concatenate([angleEdge.cordsDrill, angleEdgeTop.cordsDrill])
drillRadList = np.full([drillList.shape[0], 1], drillRad)
drillPoints = {}
drillPoints["drill"] = np.append(drillList, drillRadList, axis=1)

dxfFromDict(layers, saveFolder + "\\angled.dxf", drillPoints)
#plotLinePoints(angledWall, "line", color="k", marker="o")
#plotLinePoints(drillPoints["drill"], "circle", color="k")

##################
#
#  Generate Mount Surface
#
##################

# trapezoid wall mate holes
bEdge.genHoleBone(materialThickness + clearenceMaterial * 2.0, clearence, dogBoneDia, "I", drillNum=1)
bEdge.rotateShiftElement("hole", [0.0, materialThickness / 2.0])
drillList = np.array(bEdge.cordsHolesDrill)

holeWidth = materialThickness * np.cos(np.pi / 2.0 - angle) + np.abs(topEdge.fingerLength) * np.cos(angle) + clearenceMaterial * 2.0
holeOffsetFromEdge = materialThickness / np.sin(angle) + clearence
holeCenterLine = trapBase - holeOffsetFromEdge + (holeWidth / 2.0)

# angled wall mate holes
baseEdge.genHoleBone(holeWidth, clearence, dogBoneDia, "X", drillNum=1)
baseEdge.rotateShiftElement("hole", [holeCenterLine, materialThickness], 90.0)

for hole in baseEdge.cordsHoles:
	bEdge.cordsHoles.append(hole)

mountHoles = bEdge.cordsHoles

bEdge.rotateShiftElement("hole", [bEdge.span, baseEdge.span + materialThickness * 2.0], 180.0)
drillList = np.concatenate([drillList, bEdge.cordsHolesDrill])

for hole in bEdge.cordsHoles:
	mountHoles.append(hole)

# base outline
baseSideLength = trapBase + 2.0 * (holeWidth - holeOffsetFromEdge)
baseOffsetX = holeWidth - holeOffsetFromEdge
outlineBuffer = materialThickness * 1.5

outline = np.array([[-baseOffsetX - outlineBuffer, -outlineBuffer, 0],
					[-baseOffsetX + baseSideLength + outlineBuffer, -outlineBuffer, 0],
					[-baseOffsetX + baseSideLength + outlineBuffer, boxInnerFootprint[0] + outlineBuffer, 0],
					[-baseOffsetX - outlineBuffer, boxInnerFootprint[0] + outlineBuffer, 0],
					[-baseOffsetX - outlineBuffer, -outlineBuffer, 0]])

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

layers = {}
layers["base"] = mountHoles

drillPoints = {}
drillPoints["race"] = np.array([[trapBase / 2.0, boxInnerFootprint[0] / 2.0, raceRad]])

drillRadList = np.full([drillList.shape[0], 1], drillRad)
drillPoints["drill"] = np.append(drillList, drillRadList, axis=1)

dxfFromDict(layers, saveFolder + "\\base.dxf", drillPoints)
plotLinePoints(mountHoles, "line", color="r")
plotLinePoints(drillPoints["drill"], "circle", color="k")
plotLinePoints(drillPoints["race"], "circle", color="y")

##################
#
#  Generate Foot
#
##################
layers = {}
layers["foot"] = outline

drillPoints = {}
drillPoints["foot"] = np.array([[trapBase / 2.0, boxInnerFootprint[0] / 2.0, powerCableHoleDia / 2.0]])
drillPoints["race"] = np.array([[trapBase / 2.0, boxInnerFootprint[0] / 2.0, raceRad]])

dxfFromDict(layers, saveFolder + "\\foot.dxf", drillPoints)
#plotLinePoints(outline, "line", color="b")

##################
#
#  Generate cage
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

drillPoints = {}
drillPoints["race"] = bearingHoles

dxfFromDict({}, saveFolder + "\\cage.dxf", drillPoints)
plotLinePoints(np.array(bearingHoles), "circle", color="c")

##################
#
#  Clearence Test
#
##################

testWidth = 50.0

finA = Edge(2, -materialThickness, clearence, 100.0, 0.0)
finA.genFingerPointsBone(dogBoneDia, dogBoneType, False)
finA.cordsFinger = np.concatenate([finA.cordsFinger, np.array([[100.0, -testWidth, 0], [0.0, -testWidth, 0], [0.0, 0.0, 0]])])

finB = Edge(finA.numFingers, -materialThickness, -clearence, finA.span, 0.0)
finB.genFingerPointsBone(dogBoneDia, dogBoneType, True)
finB.rotateShiftElement("finger", [0.0, clearence * 2.0])
finB.cordsFinger = np.concatenate([finB.cordsFinger, np.array([[100.0, clearence * 2.0 + testWidth, 0], [0.0, clearence * 2.0 + testWidth, 0], [0.0, clearence * 2.0, 0]])])

finB.genHoleBone(materialThickness + clearenceMaterial * 2.0, clearence, dogBoneDia, dogBoneType)
finB.rotateShiftElement("hole", [0.0, ((testWidth - materialThickness) / -2.0) + -materialThickness])

finB.cordsHoles.append(finA.cordsFinger)

layer = {}
layer["layerA"] = finB.cordsHoles
layer["layerB"] = finB.cordsFinger
dxfFromDict(layer, saveFolder + "\\clearenceTest.dxf")
plotLinePoints(layer["layerA"], "line", color="r")
plotLinePoints(layer["layerB"], "line", color="b")
plotLinePoints(finB.cordsHoles, "line", color="c")


##################
#
#  plot parameters
#
##################

plt.axis('scaled')
plt.tight_layout()
plt.show()
