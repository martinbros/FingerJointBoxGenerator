#!/usr/bin/env python3

#import pretty_errors
from generateFingers import Edge, plotLinePoints
import matplotlib.pyplot as plt
import numpy as np
import ezdxf

boxInnerFootprint = [800.0, 600.0]
boxHeight = 1.5 * 25.4

materialThickness = 10.0
dogBoneDia = 3.175 + 0.5
dogBoneType = "I"
clearence = 0.2 / 2.0

##################
#
#  Generate footprint
#
##################
south = Edge(numFingers=3, fingerLength=-materialThickness, clearence=-clearence, span=boxInnerFootprint[0], extra=0.0)
south.genFingerPointsBone(dogBoneDia, dogBoneType, True)

east = Edge(numFingers=4, fingerLength=-materialThickness, clearence=-clearence, span=boxInnerFootprint[1], extra=0.0)
east.genFingerPointsBone(dogBoneDia, dogBoneType, True)
east.rotateShiftElement("finger", south.cordsFinger[-1], 90.0)

north = Edge(south.numFingers, -materialThickness, -clearence, boxInnerFootprint[0], 0.0)
north.genFingerPointsBone(dogBoneDia, dogBoneType, True)
north.rotateShiftElement("finger", east.cordsFinger[-1], 180.0)

west = Edge(east.numFingers, -materialThickness, -clearence, boxInnerFootprint[1], 0.0)
west.genFingerPointsBone(dogBoneDia, dogBoneType, True)
west.rotateShiftElement("finger", north.cordsFinger[-1], 270.0)

footPrint = np.concatenate([south.cordsFinger[:-1], east.cordsFinger[:-1], north.cordsFinger[:-1], west.cordsFinger])
plotLinePoints(footPrint, "line", color="k", marker="o")

##################
#
#  Generate SouthWall
#
##################
wallOrigin = [-(materialThickness + clearence), -materialThickness / 2.0]
#wallOrigin = [0.0, 0.0]
wallSouth = Edge(south.numFingers, -materialThickness, clearence, boxInnerFootprint[0], materialThickness + clearence)
wallSouth.genFingerPointsBone(dogBoneDia, dogBoneType, False)
wallSouth.rotateShiftElement("finger", wallOrigin)

wallSouthUp = Edge(1, -materialThickness, clearence, boxHeight + materialThickness, 0.0)
wallSouthUp.genFingerPointsBone(dogBoneDia, dogBoneType, False)
wallSouthUp.rotateShiftElement("finger", wallSouth.cordsFinger[-1], -90.0)

stopPoint = [[wallSouth.cordsFinger[0][0], wallSouthUp.cordsFinger[-1][1], 0]]

wallSouthDown = Edge(wallSouthUp.numFingers, -materialThickness, clearence, wallSouthUp.span, 0.0)
wallSouthDown.genFingerPointsBone(dogBoneDia, dogBoneType, False)
wallSouthDown.rotateShiftElement("finger", stopPoint[0], -270.0)

southWall = np.concatenate([wallSouth.cordsFinger[:-1], wallSouthUp.cordsFinger, wallSouthDown.cordsFinger])
plotLinePoints(southWall, "line", color="c", marker="o")

##################
#
#  Generate WestWall
#
##################
wallOrigin = [-materialThickness / 2.0, -clearence]
#wallOrigin = [0.0, 0.0]
wallWest = Edge(west.numFingers, materialThickness, clearence, boxInnerFootprint[1], clearence)
wallWest.genFingerPointsBone(dogBoneDia, dogBoneType, False)
wallWest.rotateShiftElement("finger", wallOrigin, 90.0)

wallWestUp = Edge(wallSouthUp.numFingers, -materialThickness, -clearence, boxHeight + materialThickness, 0.0)
wallWestUp.genFingerPointsBone(dogBoneDia, dogBoneType, True)
wallWestUp.rotateShiftElement("finger", wallWest.cordsFinger[-1], 180.0)

stopPoint = [[wallWestUp.cordsFinger[-1][0], wallWest.cordsFinger[0][1], 0]]

wallWestDown = Edge(wallWestUp.numFingers, -materialThickness, -clearence, wallWestUp.span, 0.0)
wallWestDown.genFingerPointsBone(dogBoneDia, dogBoneType, True)
wallWestDown.rotateShiftElement("finger", stopPoint[0], 0.0)

westWall = np.concatenate([wallWest.cordsFinger[:-1], wallWestUp.cordsFinger, wallWestDown.cordsFinger])

plotLinePoints(westWall, "line", color="r", marker="o")
plotLinePoints(wallWestDown.rotateAndShift(westWall, angle=90.0), "line", color="y", marker="o")

plt.axis('scaled')
plt.show()

doc = ezdxf.new(dxfversion='R2010')  # Create a new DXF document
#doc = ezdxf.new(dxfversion='AC1024')
msp = doc.modelspace()

bot = doc.layers.new(name="bot")  # Create Layer
msp.add_lwpolyline(footPrint, format="xyb", dxfattribs={'layer': bot.dxf.name})

south = doc.layers.new(name="south")  # Create Layer
msp.add_lwpolyline(southWall, format="xyb", dxfattribs={'layer': south.dxf.name})

west = doc.layers.new(name="west")  # Create Layer
msp.add_lwpolyline(westWall, format="xyb", dxfattribs={'layer': west.dxf.name})

doc.saveas("testBox.dxf")