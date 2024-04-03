#!/usr/bin/env python3

#import pretty_errors
from generateFingers import Edge, plotLinePoints
import matplotlib.pyplot as plt
import numpy as np
import ezdxf

boxInnerFootprint = [800.0, 600.0]
boxHeight = 50.0

materialThickness = 10.0
dogBoneDia = 4.3 + 0.2
dogBoneType = "I"
clearence = 0.2 / 2.0


south = Edge(numFingers=5, fingerLength=-materialThickness, clearence=-clearence, span=boxInnerFootprint[0], extra=0.0)
south.genFingerPointsBone(dogBoneDia, dogBoneType, True)

east = Edge(numFingers=6, fingerLength=-materialThickness, clearence=-clearence, span=boxInnerFootprint[1], extra=0.0)
east.genFingerPointsBone(dogBoneDia, dogBoneType, True)
east.rotateShiftElement("finger", south.cordsFinger[-1], 90.0)

north = Edge(south.numFingers, -materialThickness, -clearence, boxInnerFootprint[0], 0.0)
north.genFingerPointsBone(dogBoneDia, dogBoneType, True)
north.rotateShiftElement("finger", east.cordsFinger[-1], 180.0)

west = Edge(east.numFingers, -materialThickness, -clearence, boxInnerFootprint[1], 0.0)
west.genFingerPointsBone(dogBoneDia, dogBoneType, True)
west.rotateShiftElement("finger", north.cordsFinger[-1], 270.0)
print(west.cordsFinger[-1])

plotLinePoints(south.cordsFinger, "line", color="k", marker="o")
plotLinePoints(east.cordsFinger, "line", color="k", marker="o")
plotLinePoints(north.cordsFinger, "line", color="k", marker="o")
plotLinePoints(west.cordsFinger, "line", color="k", marker="o")

plt.axis('scaled')
plt.show()

doc = ezdxf.new(dxfversion='R2010')  # Create a new DXF document
msp = doc.modelspace()

layerHT = doc.layers.new(name="bot")  # Create Layer
msp.add_lwpolyline(np.concatenate([south.cordsFinger[:-1], east.cordsFinger[:-1], north.cordsFinger[:-1], west.cordsFinger]), format="xyb", dxfattribs={'layer': layerHT.dxf.name})
doc.saveas("testFile.dxf")