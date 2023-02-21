#!/usr/bin/env python3

from argparse import ArgumentParser, RawTextHelpFormatter
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


spacing = fingerLength * 0.5

baseLengthSpan = internalLength - cutClearence * 2.0
baseWidthSpan = internalWidth - cutClearence * 2.0
heightSpan = internalHeight - fingerLength

if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "folder", metavar="folder", type=str, nargs="+", help="folder in which the DXF will be saved to")
    parser.add_argument("-p", "--prefix", dest="prefix", type=str, required=False,
                        help="DXF File Name Prefix", default="fingerBox")

    args = parser.parse_args()
    data_folder = args.folder
    file_prefix = "".join(data_folder) + "\\" + args.prefix

fileName = "_%sx%sx%s(%sx%sx%s)C%s_M%s_B%s.dxf" % (internalWidth, internalLength, internalHeight, numWidthFingers, numLengthFingers, numHeightFingers, cutClearence, materialThickness, dogBoneDia)
print(file_prefix + fileName)

# Generate Bottom
ptLst1, boundryBot, units1 = gen_bottom(orgin=[0, 0], numFingList=[numWidthFingers, numLengthFingers], fingerLength=fingerLength, clearence=cutClearence, spanList=[baseWidthSpan, baseLengthSpan], dogBoneDiameter=dogBoneDia, boneBulge=boneBulge)
create_dxf([ptLst1], ["bottom"], file_prefix + "A", fileName)
graphPoints(ptLst1)

# Generate Right
startPoint = [boundryBot[1][0] + spacing, boundryBot[1][1] + cutClearence + fingerLength]
ptLst3, boundry, units2 = gen_Side(orgin=startPoint, rotation=270, numFingList=[numLengthFingers, -numHeightFingers], fingerLength=fingerLength, clearence=cutClearence, spanList=[baseLengthSpan, heightSpan], extraList=[cutClearence + fingerLength, fingerLength], dogBoneDiameter=dogBoneDia, boneBulge=boneBulge)
create_dxf([ptLst3], ["SideB"], file_prefix + "C", fileName)
graphPoints(ptLst3, color="r")

# Generate Top
startPoint = [boundryBot[0][0] - cutClearence, boundryBot[1][1] + spacing]
ptLst2, boundry, units3 = gen_Side(orgin=startPoint, rotation=0, numFingList=[numWidthFingers, numHeightFingers], fingerLength=fingerLength, clearence=cutClearence, spanList=[baseWidthSpan, heightSpan], extraList=[cutClearence, fingerLength], dogBoneDiameter=dogBoneDia, boneBulge=boneBulge)
create_dxf([ptLst2], ["SideA"], file_prefix + "B", fileName)
graphPoints(ptLst2, color="c")

# Create dxf file of all shapes
create_dxf([ptLst1, ptLst2, ptLst3], ["bot", "S_T", "S_R"], file_prefix, fileName)

# Generate Top Right (used to verify side heights match)
startPoint = [boundry[1][0] + spacing, boundry[0][1]]
ptLst3, boundry, units = gen_Side(orgin=startPoint, rotation=0, numFingList=[numLengthFingers, -numHeightFingers], fingerLength=fingerLength, clearence=cutClearence, spanList=[baseLengthSpan, heightSpan], extraList=[cutClearence + fingerLength, fingerLength], dogBoneDiameter=dogBoneDia, boneBulge=boneBulge)
graphPoints(ptLst3, color="b")


print("Width: %s\nLength: %s\nHeight: %s" % (np.around(units1, 2)[0], np.around(units1, 2)[1], np.around(units2, 2)[1]))
plt.axis('scaled')
plt.show()
