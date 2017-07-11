import arcpy
import os


def main(streamNetwork,     # Path to the stream network file
        dem,                # Path to the DEM file
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

    reachArray = makeReaches()

def makeReaches():
    i = 1
