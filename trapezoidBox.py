#!/usr/bin/env python3

#import pretty_errors
from generateFingers import Edge, plotLinePoints, dxfFromDict
import matplotlib.pyplot as plt
import numpy as np
import ezdxf

boxInnerFootprint = [600.0, 175.0]
trapBase = 175.0
boxHeight = 200.0

materialThickness = 10.0
dogBoneDia = 3.175 + 0.5
dogBoneType = "I"
clearence = 0.2 / 2.0
clearence = 0.0

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

print("%s : %s : %s : %s" % (smAngFingLen, lgAngFingLen, smAngOff, lgAngOff))

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
plotLinePoints(angledWall, "line", color="k", marker="o")

##################
#
#  Generate Mount Surface
#
##################
holeOrigin = [0.0, materialThickness / 2.0]

#trapezoid wall mate surface
bEdge.genHoleBone(materialThickness + clearence * 2.0, clearence, dogBoneDia, dogBoneType)
bEdge.rotateShiftElement("hole", holeOrigin)

#angled wall mate surface
baseEdge.genHoleBone(materialThickness + clearence * 2.0, clearence, dogBoneDia, dogBoneType)
baseEdge.rotateShiftElement("hole", [trapBase - materialThickness / 2.0,  holeOrigin[1] + materialThickness / 2.0], 90.0)

for hole in baseEdge.cordsHoles:
	bEdge.cordsHoles.append(hole)

mountHoles = bEdge.cordsHoles

bEdge.rotateShiftElement("hole", [bEdge.span, baseEdge.span + materialThickness * 2.0], 180.0)

for hole in bEdge.cordsHoles:
	mountHoles.append(hole)

outline = np.array([[-materialThickness * 2.0, -materialThickness * 2.0, 0],
			[trapBase + materialThickness * 2.0, -materialThickness * 2.0, 0],
			[trapBase + materialThickness * 2.0, boxInnerFootprint[0] + materialThickness * 2.0, 0],
			[-materialThickness * 2.0, boxInnerFootprint[0] + materialThickness * 2.0, 0],
			[-materialThickness * 2.0, -materialThickness * 2.0, 0]])

mountHoles.append(outline)

layers["base"] = mountHoles

plotLinePoints(mountHoles, "line", color="r")

dxfFromDict(layers, "trapezoidRecBox.dxf")
plt.axis('scaled')
plt.tight_layout()
plt.show()