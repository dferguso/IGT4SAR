#-------------------------------------------------------------------------------
# Name:        TheoreticalSearchArea.py
# Purpose:
#  This tool utilizes the output from the Cost Distance Model to
#  determine a least cost Path Distance surface from a point.

# Author:      Don Ferguson
#
# Created:     01/25/2012
# Copyright:   (c) Don Ferguson 2012
# Licence:
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  The GNU General Public License can be found at
#  <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

# Import arcpy module
import arcpy
import arcpy.mapping
from arcpy import env
from arcpy.sa import *

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

# Script arguments
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

mxd = arcpy.mapping.MapDocument("CURRENT")
df=arcpy.mapping.ListDataFrames(mxd,"*")[0]

# Script arguments
wrkspc = arcpy.GetParameterAsText(0)  # Get the subject number
arcpy.AddMessage("\nCurrent Workspace" + '\n' + wrkspc + '\n')
env.workspace = wrkspc

SubNum = arcpy.GetParameterAsText(1)  # Get the subject number
if SubNum == '#' or not SubNum:
    SubNum = "1" # provide a default value if unspecified

ippType = arcpy.GetParameterAsText(2)  # Determine to use PLS or LKP


DEM2 = arcpy.GetParameterAsText(3)
if DEM2 == '#' or not DEM2:
    DEM2 = "DEM" # provide a default value if unspecified

# Local variables:
IPP = "Planning Point"

Travspd_spm = "TravSpd_spm"
PthDis_travsp = "PthDis_travsp"
blnk_travsppd = "blnk_travsppd"
Travspd_kph = "TravSpd_kph"
##Travspd_kph = "TravSpd_clip"
TravTime_hrs = "TravTime_hrs"
travtimhr_rcl = "Travtimhr_rcl"
traveltime_hrs_poly = "traveltime_hrs_poly"
TravTimePoly_hrs = "TravTimePoly_hrs"
TimeTable = "C:\MapSAR_Ex\Template\SAR_Default.gdb\TimeTable"
ToblerTable ="C:\MapSAR_Ex\Tools\Tables\Tobler002.txt"
##TimeTable = "TimeTable"


arcpy.env.cellSize = DEM2

XCel = arcpy.GetRasterProperties_management(DEM2,"CELLSIZEX")
XCell = float(XCel.getOutput(0))
cellSize = XCell

############################
arcpy.AddMessage("Seconds per meter")
outDivide = Con(Raster(Travspd_kph) == 0.0,36000,3600.0/(Raster(Travspd_kph) * 1000.0))
outDivide.save(Travspd_spm)
del outDivide

# Buffer areas of impact around major roads
where1 = '"Subject_Number" = ' + str(SubNum)
where2 = ' AND "IPPType" = ' + "'" + ippType + "'"
where = where1 + where2

arcpy.SelectLayerByAttribute_management(IPP, "NEW_SELECTION", where)

arcpy.AddMessage("Path Distance")

InVertFact = 'VfTable("C:\MapSAR_Ex\Tools\Tables\Tobler.txt")'
##outPathDist = PathDistance(IPP, Travspd_spm, DEM2, "", "BINARY 1 45", "", "BINARY 1 -45 45", "", blnk_travsppd)
outPathDist = PathDistance(IPP, Travspd_spm, DEM2, "", "BINARY 1 45", "", InVertFact, "", blnk_travsppd)
outPathDist.save(PthDis_travsp)
del outPathDist

# Process: Divide (6)
outDivide = Raster(PthDis_travsp)/3600.0*10.0
outDivide.save(TravTime_hrs)
del outDivide

# Process: Reclassify
arcpy.AddMessage("Reclassify Travel Time - hrs")
# Execute Reclassify
# The output from Reclassification is multiplied by 10 to allow for 1/2 hour
# increments with integer math.  Thus 5 = 0.5 hours.  Correction will be made below.
outRaster = ReclassByTable(TravTime_hrs, TimeTable , "FROM_","TO","OUT","NODATA")
# Save the output
outRaster.save(travtimhr_rcl)

# Process: Raster to Polygon
arcpy.AddMessage("Raster to Polygon")
arcpy.RasterToPolygon_conversion(travtimhr_rcl, traveltime_hrs_poly, "SIMPLIFY", "VALUE")

# Process: Add Field
arcpy.AddMessage("Add field: Hours")
arcpy.AddField_management(traveltime_hrs_poly, "HOURS", "FLOAT", 6, "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (2)
arcpy.AddMessage("Calculate Hours Field")
arcpy.CalculateField_management(traveltime_hrs_poly, "HOURS", "!grid_code!/10.0", "PYTHON")

# Process: Add Field (2)
arcpy.AddMessage("Add field: DateHrsTxt")
arcpy.AddField_management(traveltime_hrs_poly, "DateHrsTxt", "TEXT", "", "", "30", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Dissolve
arcpy.AddMessage("Dissolve")
arcpy.Dissolve_management(traveltime_hrs_poly, TravTimePoly_hrs, "HOURS;DateHrsTxt", "", "MULTI_PART", "DISSOLVE_LINES")

TravTime_Layer=arcpy.mapping.Layer(TravTimePoly_hrs)
arcpy.mapping.AddLayer(df,TravTime_Layer,"BOTTOM")

arcpy.Delete_management(wrkspc + '\\' + PthDis_travsp)
arcpy.Delete_management(wrkspc + '\\' + Travspd_spm)
arcpy.Delete_management(wrkspc + '\\' + TravTime_hrs)
arcpy.Delete_management(wrkspc + '\\' + travtimhr_rcl)
arcpy.Delete_management(wrkspc + '\\' + traveltime_hrs_poly)


tryLayer = "TravTimePoly_hrs"
try:
    # Set layer that output symbology will be based on
    symbologyLayer = "C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\MobilityModel.lyr"

    # Apply the symbology from the symbology layer to the input layer
    arcpy.ApplySymbologyFromLayer_management (tryLayer, symbologyLayer)
except:
    pass