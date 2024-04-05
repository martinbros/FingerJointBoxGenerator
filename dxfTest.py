#!/usr/bin/env python3

#import pretty_errors
from generateFingers import Edge, plotLinePoints
import matplotlib.pyplot as plt
import numpy as np
import ezdxf

baseIF = Edge(3, -2, 0.0, 28.0, 0.0)
baseIF.genFingerPointsBone(dogBoneDia=0.5, dogBoneType="I", invertBone=False, drillNum=False)
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


doc = ezdxf.new(dxfversion='R2010')  # Create a new DXF document
msp = doc.modelspace()

dxfLayer = {}

for layer in layers:
	dxfLayer[layer] = doc.layers.new(name=layer)  # Create Layer

	if len(layers[layer][0]) == 3:
		msp.add_lwpolyline(layers[layer], format="xyb", dxfattribs={'layer': dxfLayer[layer].dxf.name})
	else:
		for hole in layers[layer]:
			msp.add_lwpolyline(hole, format="xyb", dxfattribs={'layer': dxfLayer[layer].dxf.name})


doc.saveas("testGenerationNeg.dxf")