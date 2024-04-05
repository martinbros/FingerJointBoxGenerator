#!/usr/bin/env python3

#import pretty_errors
from generateFingers import Edge, plotLinePoints
import matplotlib.pyplot as plt
import numpy as np
import ezdxf

boxInnerFootprint = [800.0, 600.0]
boxHeight = 50.0

materialThickness = 10.0
dogBoneDia = 3.175 + 0.5
dogBoneType = "I"
clearence = 0.2 / 2.0

##################
#
#  Divider
#
##################

#wallOrigin = [-(materialThickness + clearence), -materialThickness / 2.0]
wallOrigin = [0.0, 0.0]
divBot = Edge(4, -materialThickness, -clearence, boxInnerFootprint[0], materialThickness)
divBot.genFingerPointsBone(dogBoneDia, dogBoneType, False)
divBot.rotateShiftElement("finger", wallOrigin)

divR = Edge(1, materialThickness + clearence, clearence, boxHeight, 0.0)
divR.genFingerPointsBone(dogBoneDia, dogBoneType, False)
divR.rotateShiftElement("finger", divBot.cordsFinger[-1], 90.0)

stopPoint = [[divBot.cordsFinger[0][0], divR.cordsFinger[-1][1], 0]]

divL = Edge(divR.numFingers, materialThickness + clearence, clearence, divR.span, 0.0)
divL.genFingerPointsBone(dogBoneDia, dogBoneType, False)
divL.rotateShiftElement("finger", stopPoint[0], 270.0)

divWall = np.concatenate([divBot.cordsFinger[:-1], divR.cordsFinger, divL.cordsFinger])
#plotLinePoints(divWall, "line", color="c", marker="o")

##################
#
#  Generate WestWall
#
##################

wallOrigin = [0.0, 0.0]
div1 = Edge(1, materialThickness, clearence, boxHeight, 0.0)
div1.genFingerPointsBone(dogBoneDia, dogBoneType, invertBone=True)
div1.genHoleBone(materialThickness, clearence, dogBoneDia, dogBoneType, openEnds=True, invertHoles=True)
div1.rotateShiftElement("hole", [boxInnerFootprint[1] / 2.0, 0], angle=90.0)

westASpan = div1.cordsHoles[0][0][0]
westA = Edge(3, -materialThickness, -clearence, westASpan, 0.0)
westA.genFingerPointsBone(dogBoneDia, dogBoneType, invertBone=True)

westBSpan = boxInnerFootprint[1] - div1.cordsHoles[0][-1][0]
westB = Edge(3, -materialThickness, -clearence, westBSpan, 0.0)
westB.genFingerPointsBone(dogBoneDia, dogBoneType, invertBone=True)
westB.rotateShiftElement("finger", div1.cordsHoles[0][-1])

wR = Edge(1, -materialThickness, -clearence, boxHeight, 0.0)
wR.genFingerPointsBone(dogBoneDia, dogBoneType, invertBone=True)
wR.rotateShiftElement("finger", westB.cordsFinger[-1], 90.0)

wL = Edge(1, -materialThickness, -clearence, boxHeight, 0.0)
wL.genFingerPointsBone(dogBoneDia, dogBoneType, invertBone=True)
wL.rotateShiftElement("finger", [0.0, boxHeight], 270.0)


westWall = np.concatenate([westA.cordsFinger[:-1], div1.cordsHoles[0][:-1], westB.cordsFinger[:-1], wR.cordsFinger, div1.cordsHoles[-1], wL.cordsFinger])
westWall[-1] = [wallOrigin[0], wallOrigin[1], 0.0]
plotLinePoints(westWall, "line", color="c", marker="o")

plt.axis('scaled')
plt.show()


layers = {}
layers["divider"] = divWall
layers["west"] = westWall


doc = ezdxf.new(dxfversion='R2010')  # Create a new DXF document
msp = doc.modelspace()

dxfLayer = {}

for layer in layers:
	dxfLayer[layer] = doc.layers.new(name=layer)  # Create Layer
	msp.add_lwpolyline(layers[layer], format="xyb", dxfattribs={'layer': dxfLayer[layer].dxf.name})

doc.saveas("testDivBox.dxf")
