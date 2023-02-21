import pretty_errors
import sys
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


spacing = fingerLength*.5

baseLengthSpan = internalLength - cutClearence * 2.0
baseWidthSpan = internalWidth - cutClearence * 2.0
heightSpan = internalHeight - fingerLength

filePrefix = "fingerBox"
fileName = "_%sx%sx%s(%sx%sx%s)C%s_M%s_B%s" % (internalWidth, internalLength, internalHeight, numWidthFingers, numLengthFingers, numHeightFingers, cutClearence, materialThickness, dogBoneDia)
print(fileName)

# Generate Bottom
ptLst1, boundryBot, units = gen_bottom(orgin=[0,0], numFingList=[numWidthFingers,numLengthFingers], fingerLength=fingerLength, clearence=cutClearence, spanList=[baseWidthSpan,baseLengthSpan], dogBoneDiameter=dogBoneDia, boneBulge=boneBulge)
print(units)
create_dxf([ptLst1], ["bottom"], filePrefix + "A", fileName)
graphPoints(ptLst1)

# Generate Right
startPoint = [boundryBot[1][0] + spacing , boundryBot[1][1] + cutClearence + fingerLength]
ptLst3, boundry, units = gen_Side(orgin=startPoint, rotation=270, numFingList=[numLengthFingers,-numHeightFingers], fingerLength=fingerLength, clearence=cutClearence, spanList=[baseLengthSpan,heightSpan], extraList=[cutClearence + fingerLength, fingerLength], dogBoneDiameter=dogBoneDia, boneBulge=boneBulge)
print(units)
create_dxf([ptLst3], ["SideB"], filePrefix + "C", fileName)
graphPoints(ptLst3, color="r")

# Generate Top
startPoint = [boundryBot[0][0] - cutClearence, boundryBot[1][1] + spacing]
ptLst2, boundry, units = gen_Side(orgin=startPoint, rotation=0, numFingList=[numWidthFingers,numHeightFingers], fingerLength=fingerLength, clearence=cutClearence, spanList=[baseWidthSpan,heightSpan], extraList=[cutClearence, fingerLength], dogBoneDiameter=dogBoneDia, boneBulge=boneBulge)
print(units)
create_dxf([ptLst2], ["SideA"], filePrefix + "B", fileName)
graphPoints(ptLst2, color="c")

#Create dxf file of all shapes
create_dxf([ptLst1, ptLst2, ptLst3], ["bot","S_T", "S_R"], filePrefix, fileName)

# Generate Top Right (used to verify side heights match)
startPoint = [boundry[1][0] + spacing , boundry[0][1]]
ptLst3, boundry, units = gen_Side(orgin=startPoint, rotation=0, numFingList=[numLengthFingers,-numHeightFingers], fingerLength=fingerLength, clearence=cutClearence, spanList=[baseLengthSpan,heightSpan], extraList=[cutClearence + fingerLength, fingerLength], dogBoneDiameter=dogBoneDia, boneBulge=boneBulge)
graphPoints(ptLst3, color="b")

plt.axis('scaled')
plt.show()