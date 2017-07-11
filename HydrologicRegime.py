import arcpy


def main(streamNetwork,     # Path to the stream network file
        dem):               # Path to the DEM file
    arcpy.env.overwriteOutput = True
