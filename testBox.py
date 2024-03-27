#!/usr/bin/env python3

import pretty_errors
from generateFingers import Edge
import matplotlib.pyplot as plt

boxInnerFootprint = [100.0, 150.0]
boxHeight = 50.0

materialThickness = 10.0
dogBoneDia = 4.3 + 0.2
dogBoneType = "X"
clearence = 0.2 / 2.0


south = Edge(5, -materialThickness, clearence, boxInnerFootprint[0], 0.0)
south.genFingerPointsBone(dogBoneDia, dogBoneType, True)

east = Edge(7, -materialThickness, clearence, boxInnerFootprint[1], 0.0)
east.genFingerPointsBone(dogBoneDia, dogBoneType, True)
east.rotateAndShift([south.xList[-1], south.yList[-1]], 90.0)

north = Edge(south.numFingers, -materialThickness, clearence, boxInnerFootprint[0], 0.0)
north.genFingerPointsBone(dogBoneDia, dogBoneType, True)
north.rotateAndShift([east.xList[-1], east.yList[-1]], 180.0)

west = Edge(east.numFingers, -materialThickness, clearence, boxInnerFootprint[1], 0.0)
west.genFingerPointsBone(dogBoneDia, dogBoneType, True)
west.rotateAndShift([north.xList[-1], north.yList[-1]], 270.0)

wallWest = Edge(east.numFingers, materialThickness, clearence * 2.0, boxInnerFootprint[1], 0.0)
wallWest.genFingerPointsBone(dogBoneDia, dogBoneType, False)
wallWest.rotateAndShift([-1.0, 0.0], 90.0)


#plt.plot(.xList, .yList, color="violet", marker="o")
plt.plot(south.xList, south.yList, color="violet", marker="o")
plt.plot(east.xList, east.yList, color="g", marker="o")
plt.plot(north.xList, north.yList, color="b", marker="o")
plt.plot(west.xList, west.yList, color="c", marker="o")

plt.plot(wallWest.xList, wallWest.yList, color="r", marker="o")

plt.axis('scaled')

plt.show()