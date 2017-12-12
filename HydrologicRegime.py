import arcpy
import os

from ClassificationReach import ClassificationReach


def main(streamNetwork,     # Path to the stream network file
        dem,                # Path to the DEM file
        marchPrecip,        # Path to file with precipitation in March
        janTemp,            # Path to file with temperature in January
        aprilTemp,          # Path to file with mean temperature in April
        minWinterTemp,      # Path to file with minimum winter temperature
        clippingRegion,     # Path to polygon to clip stream network to
        outputFolder,       # Path to where we want to put our output
        outputName,         # Name to call output files
        testing):           # Allows the user to run a limited run
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")  # We'll be using a bunch of spatial analysis tools

    if testing:
        arcpy.AddMessage("TESTING")

    """Creates the temporary data folder, where we'll put all our intermediate results"""
    if not os.path.exists(outputFolder+"\\temporaryData"):
        os.makedirs(outputFolder+"\\temporaryData")
    tempData = outputFolder + "\\temporaryData"

    """Creates our output folder, where we'll put our final results"""
    if not os.path.exists(outputFolder+"\HydrologicRegime"):
        os.makedirs(outputFolder+"\HydrologicRegime")
    outputDataPath = outputFolder+"\HydrologicRegime"

    """Clips our stream network to a clipping region, if necessary"""
    if clippingRegion is not None:
        clippedStreamNetwork = tempData + "\clippedStreamNetwork.shp"
        arcpy.AddMessage("Clipping stream network...")
        arcpy.Clip_analysis(streamNetwork, clippingRegion, clippedStreamNetwork)
    else:
        clippedStreamNetwork = streamNetwork

    reachArray = makeReaches(clippedStreamNetwork, dem, marchPrecip, janTemp, aprilTemp, minWinterTemp, tempData, testing)

    writeOutput(reachArray, outputDataPath, arcpy.Describe(clippedStreamNetwork).spatialReference, outputName)


def makeReaches(streamNetwork, dem, marchPrecip, janTemp, aprilTemp, minWinterTemp, tempData, testing):
    reaches = []
    numReaches = int(arcpy.GetCount_management(streamNetwork).getOutput(0))
    numReachesString = str(numReaches)
    arcpy.AddMessage("Reaches to calculate: " + numReachesString)
    arcpy.AddMessage("Creating Reach Array...")

    sr = arcpy.Describe(streamNetwork).spatialReference

    fileOne = open(tempData + "\marchPrecip.txt", 'w')
    fileTwo = open(tempData + "\marchPrecipGreater.txt", 'w')

    polylineCursor = arcpy.da.SearchCursor(streamNetwork, ['SHAPE@'])
    if testing:
        for i in range(10):
            arcpy.AddMessage("Creating Reach " + str(i+1) + " out of 10")
            row = polylineCursor.next()
            classification = findClassification(row[0].firstPoint, dem, marchPrecip, janTemp, aprilTemp, minWinterTemp, tempData, sr, fileOne, fileTwo, testing)

            reach = ClassificationReach(row[0], classification)
            reaches.append(reach)
    else:
        i = 0 # just used for displaying how far through the program it is
        for row in polylineCursor:
            i += 1
            if i%100 == 0:
                arcpy.AddMessage("Creating Reach " + str(i) + " out of " + numReachesString
                             + " (" + str((float(i)/float(numReaches))*100) + "% complete)")
            classification = findClassification(row[0].firstPoint, dem, marchPrecip, janTemp, aprilTemp, minWinterTemp, tempData, sr, fileOne, fileTwo, testing)
            reach = ClassificationReach(row[0], classification)
            reaches.append(reach)

    fileOne.close()
    fileTwo.close()

    del row
    del polylineCursor

    arcpy.AddMessage("Reach Array Created")

    return reaches


def findClassification(point, dem, marchPrecip, janTemp, aprilTemp, minWinterTemp, tempData, sr, txtFile, txtFileTwo, testing):
    arcpy.env.workspace = tempData
    pointFile = arcpy.CreateFeatureclass_management(tempData, "point.shp", "POINT", "", "DISABLED", "DISABLED", sr)
    cursor = arcpy.da.InsertCursor(pointFile, ["SHAPE@"])
    cursor.insertRow([point])
    del cursor

    if testing:
        arcpy.AddMessage("March Precip: " + str(findRasterValueAtPoint(pointFile, marchPrecip, tempData)))
        arcpy.AddMessage("Elevation: " + str(findRasterValueAtPoint(pointFile, dem, tempData)))
        arcpy.AddMessage("Min Winter Temp: " + str(findRasterValueAtPoint(pointFile, minWinterTemp, tempData)))
        arcpy.AddMessage("Jan Temp: " + str(findRasterValueAtPoint(pointFile, janTemp, tempData)))
        arcpy.AddMessage("________________________________________________________________________")

    marchPrecipNum = findRasterValueAtPoint(pointFile, marchPrecip, tempData)

    txtFile.write(str(marchPrecipNum) + "\n")
    if marchPrecipNum >= 261.7:
        txtFileTwo.write(str(marchPrecipNum) + "\n")

    if marchPrecipNum >= 261.7:
        if findRasterValueAtPoint(pointFile, dem, tempData) < 618: # Finds elevation, branches
            return "Rainfall"
        else:
            return "Rain-Snow"
    else:
        if marchPrecipNum < 185.6:
            if findRasterValueAtPoint(pointFile, janTemp, tempData) >= -5: # Finds temp in January, branches based on that
                if findRasterValueAtPoint(pointFile, aprilTemp, tempData) < 6.26: # Finds temp in April, branch based on that
                    return "Groundwater"
                else:
                    return "Snow-Rain"
            else:
                if findRasterValueAtPoint(pointFile, minWinterTemp, tempData) < -7.7: # Finds winter temperature, branches based on that
                    return "Ultra-Snowmelt"
                else:
                    return "Snowmelt"
        else:
            return "Snow and Rain"


def findRasterValueAtPoint(point, raster, tempData):
    valuePoint = tempData + "\\rasterPoint.shp"

    arcpy.sa.ExtractValuesToPoints(point, raster, valuePoint)
    searchCursor = arcpy.da.SearchCursor(valuePoint, "RASTERVALU")
    row = searchCursor.next()
    value = row[0]

    del searchCursor
    del row
    return value


#def findRasterPointWithBuffer(point, raster, bufferSize, tempData):


def findPolygonValueAtPoint(point, polygon, fieldName, tempData):
    valuePoint = tempData + "\polygonPoint.shp"
    arcpy.Intersect_analysis([point, polygon], valuePoint)
    searchCursor = arcpy.da.SearchCursor(valuePoint, fieldName)
    row = searchCursor.next()
    value  = row[0]
    del row, searchCursor
    return value



def writeOutput(reachArray, outputDataPath, spatialReference, outputName):
    arcpy.env.workspace = outputDataPath

    outputShape = arcpy.CreateFeatureclass_management(outputDataPath, outputName+ ".shp", "POLYLINE", "", "DISABLED", "DISABLED", spatialReference)
    arcpy.AddField_management(outputShape, "Regime", "TEXT")

    insertCursor = arcpy.da.InsertCursor(outputShape, ["SHAPE@", "Regime"])
    for reach in reachArray:
        insertCursor.insertRow([reach.polyline, reach.classification])
    del insertCursor

    tempLayer = outputDataPath + "\\" +  outputName+ "_lyr"
    outputLayer = outputDataPath + "\\" +  outputName+ ".lyr"
    arcpy.MakeFeatureLayer_management(outputShape, tempLayer)
    arcpy.SaveToLayerFile_management(tempLayer, outputLayer)
