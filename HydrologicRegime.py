import arcpy
import os

import Reach


def main(streamNetwork,     # Path to the stream network file
        dem,                # Path to the DEM file
        marchPrecip,        # Path to file with precipitation in March
        janTemp,            # Path to file with temperature in January
        snowDepth,          # Path to file with depth of snow
        minWinterTemp,      # Path to file with minimum winter temperature
        clippingRegion,     # Path to polygon to clip stream network to
        outputFolder,       # Path to where we want to put our output
        testing):           # Allows the user to run a limited run
    arcpy.env.overwriteOutput = True

    if testing:
        arcpy.AddMessage("TESTING")

    """Creates the temporary data folder, where we'll put all our intermediate results"""
    if not os.path.exists(outputFolder+"\\temporaryData"):
        os.makedirs(outputFolder+"\\temporaryData")
    tempData = outputFolder + "\\temporaryData"

    """Creates our output folder, where we'll put our final results"""
    if not os.path.exists(outputFolder+"\outputData"):
        os.makedirs(outputFolder+"\outputData")
    outputDataPath = outputFolder+"\outputData"

    """Clips our stream network to a clipping region, if necessary"""
    if clippingRegion is not None:
        clippedStreamNetwork = tempData + "\clippedStreamNetwork.shp"
        arcpy.AddMessage("Clipping stream network...")
        arcpy.Clip_analysis(streamNetwork, clippingRegion, clippedStreamNetwork)
    else:
        clippedStreamNetwork = streamNetwork

    reachArray = makeReaches(clippedStreamNetwork, dem, marchPrecip, janTemp, snowDepth, minWinterTemp, tempData, testing)


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

            reach = Reach(row[0], classification)
            reaches.append(reach)
    else:
        i = 0 # just used for displaying how far through the program it is
        for row in polylineCursor:
            i += 1
            arcpy.AddMessage("Creating Reach " + str(i) + " out of " + numReachesString
                             + " (" + str((float(i)/float(numReaches))*100) + "% complete)")

    del row
    del polylineCursor

    arcpy.AddMessage("Reach Array Created")

    return reaches


def findClassification(point, dem, marchPrecip, janTemp, snowDepth, minWinterTemp, tempData):
    marchPrecipNum = findMarchPrecip(point, marchPrecip)
    if marchPrecipNum >= 261.7:
        if findElevation(point, dem) < 618:
            return "Rainfall"
        else:
            return "Rain-Snow"
    else:
        if marchPrecipNum < 185.6:
            if findJanTemp(point, janTemp) >= -5:
                if findSnowDepth(point, snowDepth) < 1741:
                    return "Groundwater"
                else:
                    return "Snow-Rain"
            else:
                if findMinWinterTemp(point, minWinterTemp) < -7.7:
                    return "Ultra-Snowmelt"
                else:
                    return "Snowmelt"
        else:
            return "Snow&Rain"


def findMarchPrecip(point, marchPrecip):
    #TODO: Write findMarchPrecip()
    return 1


def findElevation(point, dem):
    #TODO: Write findElevation()
    return 1


def findJanTemp(point, janTemp):
    #TODO: Write findJanTemp()
    return 1


def findSnowDepth(point, snowDepth):
    #TODO: Write findSnowDepth()
    return 1


def findMinWinterTemp(point, minWinterTemp):
    #TODO: Write findMinWinterTemp()
    return 1


    return 1