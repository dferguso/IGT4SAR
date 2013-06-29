#-------------------------------------------------------------------------------
# Name:        CostDistanceModel2.py
# Purpose:     Modified version of Liz Sarow's Cost Distance Model
# Usage: CostDistanceModel <DEM> <Roads> <Trails> <FenceLines> <PowerLines> <NLCD>
# Author:      Don Ferguson
#
# Created:     12/12/2011
# Copyright:   (c) ferguson 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# Import arcpy module
import arcpy
import arcpy.mapping
from arcpy import env
from arcpy.sa import *

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# Script arguments
workspc = arcpy.GetParameterAsText(0)
env.workspace = workspc
env.overwriteOutput = "True"
#arcpy.env.extent = "MAXOF"

mxd = arcpy.mapping.MapDocument("CURRENT")
df=arcpy.mapping.ListDataFrames(mxd,"*")[0]

DEM2 = arcpy.GetParameterAsText(1)
if DEM2 == '#' or not DEM2:
    DEM2 = "DEM" # provide a default value if unspecified

Subject_Impedance = arcpy.GetParameterAsText(2)
if Subject_Impedance == '#' or not Subject_Impedance:
    Subject_Impedance = "100" # provide a default value if unspecified

#High_Slope_Degrees = arcpy.GetParameterAsText(8)
#if High_Slope_Degrees == '#' or not High_Slope_Degrees:
#    High_Slope_Degrees = "45" # provide a default value if unspecified

#Tables
TimeTable = "TimeTable"
Travspd_spm = "TravSpd_spm"

# Process: Path Distance (2)
arcpy.gp.PathDistance_sa(IPP, PthDis_travsp, Travspd_spm, DEM2, "", "BINARY 1 45", "", "BINARY 1 -30 30", "", blnk_travsppd)

# Process: Divide (6)
outDivide = Raster(PthDis_travsp)/3600.0
outDivide.save(TravTime_hrs)
del outDivide

# Process: Reclassify
arcpy.AddMessage("Reclassify Travel Time - hrs")
# Execute Reclassify
outRaster = ReclassByTable(TravTime_hrs, TimeTable,"FROM_","TO","OUT","NODATA")
# Save the output
outRaster.save(travtimhr_rcl)

# Process: Raster to Polygon
arcpy.AddMessage("Raster to Polygon")
arcpy.RasterToPolygon_conversion(travtimhr_rcl, traveltime_hrs_poly, "SIMPLIFY", "VALUE")

# Process: Add Field
arcpy.AddMessage("Add field: Hours")
arcpy.AddField_management(traveltime_hrs_poly, "Hours", "LONG", 6, "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (2)
arcpy.AddMessage("Calculate Hours Field")
arcpy.CalculateField_management(traveltime_hrs_poly, "Hours", "!grid_code!", "PYTHON")

# Process: Add Field (2)
arcpy.AddMessage("Add field: DateHrsTxt")
arcpy.AddField_management(traveltime_hrs_poly, "DateHrsTxt", "TEXT", "", "", "30", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Dissolve
arcpy.AddMessage("Dissolve")
arcpy.Dissolve_management(traveltime_hrs_poly, TravTimePoly_hrs, "Hours;DateHrsTxt", "", "MULTI_PART", "DISSOLVE_LINES")

TravTime_Layer=arcpy.mapping.Layer(TravTimePoly_hrs)
arcpy.mapping.AddLayer(df,TravTime_Layer,"BOTTOM")

#arcpy.Delete_management(walkspd_kph)
arcpy.Delete_management(walkspd_secpme)

arcpy.Delete_management(PthDis_travsp)
arcpy.Delete_management(blnk_travsppd)
arcpy.Delete_management(travtimhr_rcl)
arcpy.Delete_management(traveltime_hrs_poly)
arcpy.Delete_management(TravTime_hrs)
