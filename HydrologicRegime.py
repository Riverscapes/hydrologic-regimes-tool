import arcpy
import os

from ClassificationReach import ClassificationReach


def main(streamNetwork,     # Path to the stream network file
        dem,                # Path to the DEM file
        marchPrecip,        # Path to file with precipitation in March
        janTemp,            # Path to file with temperature in January
        snowDepth,          # Path to file with depth of snow
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

    reachArray = makeReaches(clippedStreamNetwork, dem, marchPrecip, janTemp, snowDepth, minWinterTemp, tempData, testing)

    writeOutput(reachArray, outputDataPath, arcpy.Describe(clippedStreamNetwork).spatialReference, outputName)


def makeReaches(streamNetwork, dem, marchPrecip, janTemp, snowDepth, minWinterTemp, tempData, testing):
    reaches = []
    numReaches = int(arcpy.GetCount_management(streamNetwork).getOutput(0))
    numReachesString = str(numReaches)
    arcpy.AddMessage("Reaches to calculate: " + numReachesString)
    arcpy.AddMessage("Creating Reach Array...")

    polylineCursor = arcpy.da.SearchCursor(streamNetwork, ['SHAPE@'])
    if testing:
        for i in range(10):
            arcpy.AddMessage("Creating Reach " + str(i+1) + " out of 10")
            row = polylineCursor.next()
            classification = findClassification(row[0].firstPoint, dem, marchPrecip, janTemp, snowDepth, minWinterTemp, tempData)

            reach = ClassificationReach(row[0], classification)
            reaches.append(reach)
    else:
        i = 0 # just used for displaying how far through the program it is
        for row in polylineCursor:
            i += 1
            if i%5 == 0:
                arcpy.AddMessage("Creating Reach " + str(i) + " out of " + numReachesString
                             + " (" + str((float(i)/float(numReaches))*100) + "% complete)")
            classification = findClassification(row[0].firstPoint, dem, marchPrecip, janTemp, snowDepth, minWinterTemp, tempData)
            reach = ClassificationReach(row[0], classification)
            reaches.append(reach)

    del row
    del polylineCursor

    arcpy.AddMessage("Reach Array Created")

    return reaches


def findClassification(point, dem, marchPrecip, janTemp, snowDepth, minWinterTemp, tempData):
    arcpy.env.workspace = tempData
    sr = arcpy.Describe(dem).spatialReference
    pointFile = arcpy.CreateFeatureclass_management(tempData, "point.shp", "POINT", "", "DISABLED", "DISABLED", sr)
    cursor = arcpy.da.InsertCursor(pointFile, ["SHAPE@"])
    cursor.insertRow([point])
    del cursor
    #arcpy.AddMessage("March Precip: " + str(findRasterValueAtPoint(pointFile, marchPrecip, tempData)))
    #arcpy.AddMessage("Elevation: " + str(findRasterValueAtPoint(pointFile, dem, tempData)))
    #arcpy.AddMessage("Min Winter Temp: " + str(findRasterValueAtPoint(pointFile, minWinterTemp, tempData)))
    #arcpy.AddMessage("Jan Temp: " + str(findRasterValueAtPoint(pointFile, janTemp, tempData)))
    #arcpy.AddMessage("________________________________________________________________________")

    marchPrecipNum = findRasterValueAtPoint(pointFile, marchPrecip, tempData)

    if marchPrecipNum >= 261.7:
        if findRasterValueAtPoint(pointFile, dem, tempData) < 618: # Finds elevation, branches
            return "Rainfall"
        else:
            return "Rain-Snow"
    else:
        if marchPrecipNum < 185.6:
            if findRasterValueAtPoint(pointFile, janTemp, tempData) >= -5: # Finds temp in January, branches based on that
                """
                if findSnowDepth(pointFile, snowDepth, tempData) < 1741: # We still can't find good data for snow depth
                    return "Groundwater"
                else:
                    return "Snow-Rain"
                """
                return "Groundwater or Snow-Rain"

            else:
                if findRasterValueAtPoint(pointFile, minWinterTemp, tempData) < -7.7: # Finds winter temperature, branches based on that
                    return "Ultra-Snowmelt"
                else:
                    return "Snowmelt"
        else:
            return "Snow&Rain"


def findRasterValueAtPoint(point, raster, tempData):
    valuePoint = tempData + "\\rasterPoint.shp"
    sr = arcpy.Describe(raster).SpatialReference

    arcpy.sa.ExtractValuesToPoints(point, raster, valuePoint)
    searchCursor = arcpy.da.SearchCursor(valuePoint, "RASTERVALU")
    row = searchCursor.next()
    value = row[0]

    del searchCursor
    del row
    return value


def findPolygonValueAtPoint(point, polygon, fieldName, tempData):
    valuePoint = tempData + "\polygonPoint.shp"
    arcpy.Intersect_analysis([point, polygon], valuePoint)
    searchCursor = arcpy.da.SearchCursor(valuePoint, fieldName)
    row = searchCursor.next()
    value  = row[0]
    del row, searchCursor
    return value


def findSnowDepth(point, snowDepth, tempData):
    #TODO: Write findSnowDepth()
    return 1

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
