#!/usr/bin/env python3

import pretty_errors
from boxLib import *

internalWidth = 42.0 * 4 + 1
internalLength = 42.0 * 3 + 1
internalHeight = 47.0
materialThickness = 3.18

numWidthFingers = 8
numLengthFingers = 6
numHeightFingers = 2

dogBoneDia = 0.0
boneBulge = 0.75
fingerOutstick = 0.0
fingerLength = materialThickness + fingerOutstick
cutClearence = 0.2
# Send cut send recommends 0.01in (0.005in per side) of clearence


spacing = fingerLength * 0.5

baseLengthSpan = internalLength - cutClearence * 2.0
baseWidthSpan = internalWidth - cutClearence * 2.0
heightSpan = internalHeight - fingerLength


#file_prefix = "".join(data_folder) + "\\" + args.prefix

fileName = "_%sx%sx%s(%sx%sx%s)C%s_M%s_D%s_B%s.dxf" % (internalWidth, internalLength, internalHeight, numWidthFingers, numLengthFingers, numHeightFingers, cutClearence, materialThickness, dogBoneDia, boneBulge)
#print(file_prefix + fileName)

# Generate Bottom
ptLst1, boundryBot, units1 = gen_bottom(orgin=[0, 0], numFingList=[numWidthFingers, numLengthFingers], fingerLength=fingerLength, clearence=cutClearence, spanList=[baseWidthSpan, baseLengthSpan], dogBoneDiameter=dogBoneDia, boneBulge=boneBulge)
#create_dxf([ptLst1], ["bottom"], file_prefix + "A", fileName)
graphPoints(ptLst1)


