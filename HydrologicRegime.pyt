import arcpy
import HydrologicRegime


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "HydrologicRegime"
        self.alias = "Hydrologic Regime Model"

        # List of tool classes associated with this toolbox
        self.tools = [HydrologicRegimeTool]


class HydrologicRegimeTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Hydrologic Regime Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName = "Stream Network",
            name = "streamNetwork",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Input",
            multiValue = False)

        param1 = arcpy.Parameter(
            displayName = "DEM",
            name = "DEM",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Input",
            multiValue = False)

        param2 = arcpy.Parameter(
            displayName = "March Precipitation",
            name = "marchPrecip",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Input",
            multiValue = False)

        param3 = arcpy.Parameter(
            displayName = "January Temperature",
            name = "janTemp",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Input",
            multiValue = False)

        param4 = arcpy.Parameter(
            displayName = "April Temperature",
            name = "aprilTemp",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Input",
            multiValue = False)

        param5 = arcpy.Parameter(
            displayName = "Min Winter Temp",
            name = "minWinterTemp",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Input",
            multiValue = False)

        param6 = arcpy.Parameter(
            displayName = "Clipping Region",
            name = "Clipping Region",
            datatype = "DEFeatureClass",
            parameterType = "Optional",
            direction = "Input",
            multiValue = False)

        param7 = arcpy.Parameter(
            displayName = "Output Files Folder",
            name = "Output Files",
            datatype = "DEFolder",
            parameterType = "Required",
            direction = "Input",
            multiValue = False)

        param8 = arcpy.Parameter(
            displayName = "Output Name",
            name = "outputName",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input",
            multiValue = False)

        param9 = arcpy.Parameter(
            displayName = "Testing",
            name = "Testing",
            datatype = "GPBoolean",
            parameterType = "Optional",
            direction = "Input",
            multiValue = False)

        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        HydrologicRegime.main(parameters[0].valueAsText,
            parameters[1].valueAsText,
            parameters[2].valueAsText,
            parameters[3].valueAsText,
            parameters[4].valueAsText,
            parameters[5].valueAsText,
            parameters[6].valueAsText,
            parameters[7].valueAsText,
            parameters[8].valueAsText,
            parameters[9].valueAsText)
        return
