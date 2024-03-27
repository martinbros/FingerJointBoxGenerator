import numpy as np
import ezdxf
import matplotlib.pyplot as plt

# https://www.euclideanspace.com/maths/geometry/affine/aroundPoint/matrix2d/
# https://ezdxf.readthedocs.io/en/stable/tutorials/lwpolyline.html


def graphPoints(pointsList, color="k"):

    for idx in range(len(pointsList) - 1):
        plt.plot([pointsList[idx][0], pointsList[idx + 1][0]], [pointsList[idx][1], pointsList[idx + 1][1]], color=color)


def dogBoneCheck(boneDia, numFingers, clearence, span):
    polarity = numFingers / np.absolute(numFingers)
    numFingers = np.absolute(numFingers)

    unit = (span - (2.0 * numFingers * clearence)) / (2.0 * numFingers + 1.0)

    while (2.5 * boneDia > unit + 2 * clearence):
        numFingers -= 1
        unit = (span - (2.0 * numFingers * clearence)) / (2.0 * numFingers + 1.0)

    return numFingers * polarity


def genPoints(origin, typeSide, numFingers, fingerLength, clearence, dogDia, bulge, span, extra):

    numFingers = int(np.absolute(numFingers))

    xList = np.empty((2 * numFingers + 1) * 2)
    yList = np.empty((2 * numFingers + 1) * 2)
    bulgeList = np.empty((2 * numFingers + 1) * 2)

    unit = (span - (2.0 * numFingers * clearence)) / (2.0 * numFingers + 1.0)
    hole = unit + 2 * clearence
    dogDiff = hole - 2 * dogDia

    #  Generate width of fingers/slots
    if typeSide == "thick":

        bulge = (np.absolute(fingerLength) / fingerLength) * bulge * -1

        yList = np.tile([origin[1] + fingerLength, origin[1] + fingerLength, origin[1] + fingerLength, origin[1] + fingerLength, origin[1], origin[1]], numFingers + 1)[4:]

        bulgeList = np.tile([0.0, 0.0, bulge, 0.0, bulge, 0.0], numFingers + 1)[:-4]

        xList = np.tile([unit, dogDia, dogDiff, dogDia], numFingers + 1)[:-3]
        xList[0] = xList[0] + extra
        xList[-1] = xList[-1] + extra

        xList = np.cumsum(xList)  # Generate all of the x-points from the widths
        repeatList = np.tile([2, 1, 1, 2], numFingers + 1)[:-3]
        repeatList[-1] = 1
        xList = np.repeat(xList, repeatList)

    elif typeSide == "thin":

        bulge = (np.absolute(fingerLength) / fingerLength) * bulge

        yList = np.tile([origin[1], origin[1], origin[1], origin[1], origin[1] + fingerLength, origin[1] + fingerLength, ], numFingers + 1)[1:-3]

        bulgeList = np.tile([bulge, 0.0, bulge, 0.0, 0.0, 0.0], numFingers + 1)[1:-3]
        bulgeList[-1] = 0

        xList = np.tile([dogDia, dogDiff, dogDia, unit], numFingers + 1)[2:-3]
        xList = np.concatenate([[extra + clearence + unit - dogDia], xList, [extra + clearence + unit - dogDia]])  # Insert extra and the difference between the clearence + unit - dogbone

        xList = np.cumsum(xList)  # Generate all of the x-points from the widths
        repeatList = np.tile([1, 1, 2, 2], numFingers + 1)[1:-2]
        xList = np.repeat(xList, repeatList)

    else:
        print("enter edge type")

    xList = xList + origin[0]  # Shift the points according to the starting point
    xList = np.insert(xList, 0, origin[0])  # Insert the starting point

    return(np.dstack((xList, yList, bulgeList))[0], unit)


def rotate_points(points, angle, origin=(0, 0)):
    # convert angle to radians
    angle_rad = np.radians(angle)
    # create the translation matrix to move the origin to the specified point
    translation_matrix = np.array([[1, 0, origin[0]],
                                   [0, 1, origin[1]],
                                   [0, 0, 1]])
    # create the rotation matrix
    rotation_matrix = np.array([[np.cos(angle_rad), -np.sin(angle_rad), 0],
                                [np.sin(angle_rad), np.cos(angle_rad), 0],
                                [0, 0, 1]])
    # create the inverse of the translation matrix to move the origin back
    inverse_translation_matrix = np.array([[1, 0, -origin[0]],
                                           [0, 1, -origin[1]],
                                           [0, 0, 1]])
    # concatenate the matrices to create the transformation matrix
    transformation_matrix = translation_matrix @ rotation_matrix @ inverse_translation_matrix
    # create a matrix of column vectors from the points
    #print(points[:, :2])
    points_matrix = np.hstack([points[:, :2], np.ones((len(points), 1))]).T
    print(points_matrix)
    # apply the transformation to the points
    transformed_points = transformation_matrix @ points_matrix

    # Apply Bulge List back in
    transformed_points[-1] = points[:, -1]
    # return the transformed points as a 2D numpy array
    return transformed_points.T


def gen_bottom(orgin, numFingList, fingerLength, clearence, spanList, dogBoneDiameter, boneBulge):
    numFingList[0] = dogBoneCheck(dogBoneDiameter, numFingList[0], clearence, spanList[0])
    numFingList[1] = dogBoneCheck(dogBoneDiameter, numFingList[1], clearence, spanList[1])

    allPoints, yUnit = genPoints(orgin, typeSide="thin", numFingers=numFingList[1], fingerLength=fingerLength, clearence=clearence, span=spanList[1], extra=0.0, dogDia=dogBoneDiameter, bulge=boneBulge)
    allPoints = rotate_points(allPoints, 90, orgin)

    points, xUnit = genPoints(allPoints[-1], typeSide="thin", numFingers=numFingList[0], fingerLength=fingerLength, clearence=clearence, span=spanList[0], extra=0.0, dogDia=dogBoneDiameter, bulge=boneBulge)
    rightPoint = points[-1]
    allPoints = np.concatenate([allPoints, points])

    points, unit = genPoints(points[-1], typeSide="thin", numFingers=numFingList[1], fingerLength=fingerLength, clearence=clearence, span=spanList[1], extra=0.0, dogDia=dogBoneDiameter, bulge=boneBulge)
    points = rotate_points(points, 270, points[0])
    allPoints = np.concatenate([allPoints, points])

    points, unit = genPoints(points[-1], typeSide="thin", numFingers=numFingList[0], fingerLength=fingerLength, clearence=clearence, span=spanList[0], extra=0.0, dogDia=dogBoneDiameter, bulge=boneBulge)
    points = rotate_points(points, 180, points[0])
    allPoints = np.concatenate([allPoints, points])

    return(allPoints, [orgin, rightPoint], [xUnit, yUnit])


def gen_Side(orgin, rotation, numFingList, fingerLength, clearence, spanList, extraList, dogBoneDiameter, boneBulge):
    numFingList[0] = dogBoneCheck(dogBoneDiameter, numFingList[0], clearence, spanList[0])
    numFingList[1] = dogBoneCheck(dogBoneDiameter, numFingList[1], clearence, spanList[1])

    polarity = numFingList[1] / np.absolute(numFingList[1])

    allPoints, xUnit = genPoints(orgin, typeSide="thick", numFingers=numFingList[0], fingerLength=fingerLength, clearence=clearence, span=spanList[0], extra=extraList[0], dogDia=dogBoneDiameter, bulge=boneBulge)

    if polarity > 0:
        points, yUnit = genPoints(allPoints[-1], typeSide="thin", numFingers=numFingList[1], fingerLength=-fingerLength, clearence=clearence, span=spanList[1], extra=extraList[1], dogDia=dogBoneDiameter, bulge=boneBulge)
    else:
        points, yUnit = genPoints(allPoints[-1], typeSide="thick", numFingers=numFingList[1], fingerLength=fingerLength, clearence=clearence, span=spanList[1], extra=extraList[1], dogDia=dogBoneDiameter, bulge=boneBulge)

    points = rotate_points(points, 90, allPoints[-1])
    allPoints = np.concatenate([allPoints, points])

    rightPoint = points[-1]

    finalStart = [orgin[0], allPoints[-1][1]]

    if polarity > 0:
        points, unit = genPoints(finalStart, typeSide="thin", numFingers=numFingList[1], fingerLength=-fingerLength, clearence=clearence, span=spanList[1], extra=fingerLength, dogDia=dogBoneDiameter, bulge=boneBulge)
    else:
        points, unit = genPoints(finalStart, typeSide="thick", numFingers=numFingList[1], fingerLength=fingerLength, clearence=clearence, span=spanList[1], extra=fingerLength, dogDia=dogBoneDiameter, bulge=boneBulge)

    points = rotate_points(points, 270, finalStart)
    allPoints = np.concatenate([allPoints, points])

    if rotation == 0:
        return(allPoints, [orgin, rightPoint], [xUnit, yUnit])
    else:
        return(rotate_points(allPoints, rotation, orgin), [orgin, rotate_points(np.array([rightPoint]), rotation, orgin)[0]], [xUnit, yUnit])


def create_dxf(allPoints, layerNames, filePrefix, fileName):
    doc = ezdxf.new(dxfversion='R2010')  # Create a new DXF document

    for idx in range(len(layerNames)):

        layer = doc.layers.new(name=layerNames[idx])  # Create Layer
        msp = doc.modelspace()
        msp.add_lwpolyline(allPoints[idx], format="xyb", dxfattribs={'layer': layer.dxf.name})

    doc.saveas(filePrefix + fileName)
