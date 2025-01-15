#!/usr/bin/env python3

#import pretty_errors
from generateFingers import Edge, plotLinePoints, dxfFromDict
import matplotlib.pyplot as plt
import numpy as np
import ezdxf

baseIF = Edge(3, 2, 0.5, 28.0, [3.0, -1.0])
baseIF.genFingerPointsBone(dogBoneDia=0.5, dogBoneType="I", invertBone=False, drillNum=1)
baseIF.genHoleBone(baseIF.fingerLength, baseIF.clearence, dogBoneDia=0.5, dogBoneType="I", openEnds=True)

baseIT = Edge(baseIF.numFingers, baseIF.fingerLength, baseIF.clearence, baseIF.span, baseIF.extra)
baseIT.genFingerPointsBone(dogBoneDia=0.5, dogBoneType="I", invertBone=True, drillNum=False)
baseIT.genHoleBone(baseIF.fingerLength, baseIF.clearence, dogBoneDia=0.5, dogBoneType="I", openEnds=True, invertHoles=True)

baseHF = Edge(baseIF.numFingers, baseIF.fingerLength, baseIF.clearence, baseIF.span, baseIF.extra)
baseHF.genFingerPointsBone(dogBoneDia=0.5, dogBoneType="H", invertBone=False, drillNum=False)
baseHF.genHoleBone(baseIF.fingerLength, baseIF.clearence, dogBoneDia=0.5, dogBoneType="H", openEnds=True)

baseHT = Edge(baseIF.numFingers, baseIF.fingerLength, baseIF.clearence, baseIF.span, baseIF.extra)
baseHT.genFingerPointsBone(dogBoneDia=0.5, dogBoneType="H", invertBone=True, drillNum=False)
baseHT.genHoleBone(baseIF.fingerLength, baseIF.clearence, dogBoneDia=0.5, dogBoneType="H", openEnds=True, invertHoles=True)

baseXF = Edge(baseIF.numFingers, baseIF.fingerLength, baseIF.clearence, baseIF.span, baseIF.extra)
baseXF.genFingerPointsBone(dogBoneDia=0.5, dogBoneType="X", invertBone=False, drillNum=False)
baseXF.genHoleBone(baseIF.fingerLength, baseIF.clearence, dogBoneDia=0.5, dogBoneType="X", openEnds=True)

baseXT = Edge(baseIF.numFingers, baseIF.fingerLength, baseIF.clearence, baseIF.span, baseIF.extra)
baseXT.genFingerPointsBone(dogBoneDia=0.5, dogBoneType="X", invertBone=True, drillNum=False)
baseXT.genHoleBone(baseIF.fingerLength, baseIF.clearence, dogBoneDia=0.5, dogBoneType="X", openEnds=True, invertHoles=True)

layers = {}
layers["fIF"] = baseIF.cordsFinger
layers["fIT"] = baseIT.cordsFinger
layers["fHF"] = baseHF.cordsFinger
layers["fHT"] = baseHT.cordsFinger
layers["fXF"] = baseXF.cordsFinger
layers["fXT"] = baseXT.cordsFinger
layers["hIF"] = baseIF.cordsHoles
layers["hIT"] = baseIT.cordsHoles
layers["hHF"] = baseHF.cordsHoles
layers["hHT"] = baseHT.cordsHoles
layers["hXF"] = baseXF.cordsHoles
layers["hXT"] = baseXT.cordsHoles

drillLayer = {}
drillLayer["drill"] = baseIF.cordsDrill  # Pull coordinates for drill location
drillRadList = np.full([drillLayer["drill"].shape[0], 1], 0.5)  # Create a list equal to the length of the drill coordinate list
drillLayer["drill"] = np.append(drillLayer["drill"], drillRadList, axis=1)  # Append the drill radius to the coordinate list


dxfFromDict(layers, "testGeneration.dxf", drillLayer)
