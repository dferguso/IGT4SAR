#-------------------------------------------------------------------------------
# Name:        CostDistanceModel_Backup.py
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

Roads = arcpy.GetParameterAsText(1)
if Roads == '#' or not Roads:
    Roads = "Roads" # provide a default value if unspecified

Trails = arcpy.GetParameterAsText(2)
if Trails == '#' or not Trails:
    Trails = "Trails" # provide a default value if unspecified

Water = arcpy.GetParameterAsText(3)
if Water == '#' or not Water:
    Water = "Water" # provide a default value if unspecified

NLCD = arcpy.GetParameterAsText(4)
if NLCD == '#' or not NLCD:
    NLCD = "NLCD" # provide a default value if unspecified

DEM2 = arcpy.GetParameterAsText(5)
if DEM2 == '#' or not DEM2:
    DEM2 = "DEM" # provide a default value if unspecified

TheoDist = arcpy.GetParameterAsText(6)
if TheoDist == '#' or not TheoDist:
    TheoDist = "0" # provide a default value if unspecified

Subject_Impedance = arcpy.GetParameterAsText(7)
if Subject_Impedance == '#' or not Subject_Impedance:
    Subject_Impedance = "100" # provide a default value if unspecified

#High_Slope_Degrees = arcpy.GetParameterAsText(8)
#if High_Slope_Degrees == '#' or not High_Slope_Degrees:
#    High_Slope_Degrees = "45" # provide a default value if unspecified

#Tables
cfcc = "cfcc"
TrailClass = "Trail_Class"
LandCoverClass = "LandCover_Class"
TimeTable = "TimeTable"

#File Names:
IPP = "Incident\Plan_Point"
IPP_dist = "IPPTheoDistance"
Roads_Clipped = "Roads_Clipped"
Roads_Buf = "Roads_Buffered"
Trails_Clipped = "Trails_Clipped"
Trails_Buf = "Trails_Buffered"
Water_Clipped = "Water_Clipped"
clip_Block = "clip_block"
NLCD_Clip = "NLCD_clipped"
#
NLCD_Resample2 = "NLCD_Resample"

# Rasters
Water_Impd = "Water_Impd"
Trail_Impd = "Trail_Impd"
Road_Impd = "Road_Impd"
Veggie_Impd = "NLCD_Impd"
ImpedPre = "Imped_Pre"

#
Sloper = "Slope"
High_Slope = "High_Slope"
walkspd_kph = "walkspd_kph"
walkspd_secpme = "walkspd_secpme"
walkspd_mph = "walkspd_mph"
Impedance = "Impedance"
Travspd_spm = "TravSpd_spm"
PthDis_travsp = "PthDis_travsp"
blnk_travsppd = "blnk_travsppd"

# Local variables:
Input_true_raster_or_constant_value = "1"
TheoSearch = str(TheoDist) + " MILES"
v3600 = "3600"
Miles_per_Km_Conversion = 0.6213711922
High_Slope_Degrees = "45"

TravTime_hrs = "TravTime_hrs"
travtimhr_rcl = "Travtimhr_rcl"
traveltime_hrs_poly = "traveltime_hrs_poly"
TravTimePoly_hrs = "TravTimePoly_hrs"


# Process: Buffer for theoretical search area
arcpy.AddMessage("Buffer IPP")
arcpy.Buffer_analysis(IPP, IPP_dist, TheoSearch)
IPPDist_Layer=arcpy.mapping.Layer(IPP_dist)
arcpy.mapping.AddLayer(df,IPPDist_Layer,"BOTTOM")
spatialRef = arcpy.Describe(IPP_dist).SpatialReference
spn =spatialRef
arcpy.AddMessage(spn.name)

# Process: Clip Roads
arcpy.AddMessage("Clip Roads and buffer to 20 meters")
arcpy.Clip_analysis(Roads, IPP_dist, Roads_Clipped, "")
# Process: Buffer for theoretical search area
arcpy.Buffer_analysis(Roads_Clipped, Roads_Buf, "20 Meters")

# Process: Clip Trails
arcpy.AddMessage("Clip Trails and buffer to 10 meters")
arcpy.Clip_analysis(Trails, IPP_dist, Trails_Clipped, "")
# Process: Buffer for theoretical search area
arcpy.Buffer_analysis(Trails_Clipped, Trails_Buf, "10 Meters")

# Process: Clip Water
arcpy.AddMessage("Clip water features")
arcpy.Clip_analysis(Water, IPP_dist, Water_Clipped, "")

# Process: Clip Raster NLCD
arcpy.AddMessage("Clip NLCD")
arcpy.Clip_management(NLCD, "#", NLCD_Clip, IPP_dist, "", "ClippingGeometry")
NLCDClip_Layer=arcpy.mapping.Layer(NLCD_Clip)
arcpy.mapping.AddLayer(df,NLCDClip_Layer,"BOTTOM")

# Process: Resample
arcpy.AddMessage("Resample NLCD")
arcpy.AddMessage(DEM2)
arcpy.Resample_management(NLCD_Clip, NLCD_Resample2, DEM2, "NEAREST")
arcpy.mapping.RemoveLayer(df,NLCDClip_Layer)
NLCDResamp=arcpy.mapping.Layer(NLCD_Resample2)
arcpy.mapping.AddLayer(df,NLCDResamp,"BOTTOM")
# Process: Add Join (3)
arcpy.AddMessage("Land Cover Impedance - Join Table w/ NLCD")
arcpy.AddJoin_management(NLCD_Resample2, "VALUE", LandCoverClass, "LCCC", "KEEP_ALL")
arcpy.AddMessage("Done")
# Process: Lookup
arcpy.AddMessage("Create Veggie Impedance Layer")
arcpy.gp.Lookup_sa(NLCD_Resample2, "LandCover_Class.Walk_Impd", Veggie_Impd)
arcpy.mapping.RemoveLayer(df,NLCDResamp)
VeggieImpd_Layer=arcpy.mapping.Layer(Veggie_Impd)
arcpy.mapping.AddLayer(df,VeggieImpd_Layer,"BOTTOM")

# Process: Add Join for Trails
TrailBuf_Layer=arcpy.mapping.Layer(Trails_Buf)
arcpy.mapping.AddLayer(df,TrailBuf_Layer,"BOTTOM")
arcpy.AddJoin_management(Trails_Buf, "MAINT_LVL", TrailClass, "Trail_Clas", "KEEP_ALL")
# Process: Polyline to Raster
arcpy.AddMessage("create Trail Impedance Layer")
arcpy.PolygonToRaster_conversion(Trails_Buf, "Trail_Class.Walk_Impd", Trail_Impd, "CELL_CENTER", "NONE", DEM2)
arcpy.mapping.RemoveLayer(df,TrailBuf_Layer)
TrailImpd_Layer=arcpy.mapping.Layer(Trail_Impd)
arcpy.mapping.AddLayer(df,TrailImpd_Layer,"BOTTOM")


# Process: Add Join for Roads
RoadBuf_Layer=arcpy.mapping.Layer(Roads_Buf)
arcpy.mapping.AddLayer(df,RoadBuf_Layer,"BOTTOM")
arcpy.AddJoin_management(Roads_Buf, "CFCC", cfcc, "CFCC", "KEEP_ALL")
# Process: Polyline to Raster (3)
arcpy.AddMessage("create Road Impedance Layer")
arcpy.PolygonToRaster_conversion(Roads_Buf, "cfcc.Walk_Impd", Road_Impd, "CELL_CENTER", "NONE", DEM2)
arcpy.mapping.RemoveLayer(df,RoadBuf_Layer)
RoadImpd_Layer=arcpy.mapping.Layer(Road_Impd)
arcpy.mapping.AddLayer(df,RoadImpd_Layer,"BOTTOM")

# Check to see if the water polygon already has a "Impd" field.  If not create on
WaterImpedance = 99
if len(arcpy.ListFields(Water_Clipped,"Impedance")) > 0:
    arcpy.CalculateField_management(Water_Clipped,"Impedance",WaterImpedance)
else:
    # Add the new field and calculate the value
    arcpy.AddField_management(Water_Clipped, "Impedance", "SHORT")
    arcpy.CalculateField_management(Water_Clipped,"Impedance",WaterImpedance)

# Process: Polygon to Raster
arcpy.AddMessage("create Water Impedance Layer")
arcpy.PolygonToRaster_conversion(Water_Clipped, "Impedance", Water_Impd, "CELL_CENTER", "NONE", DEM2)
WaterImpd_Layer=arcpy.mapping.Layer(Water_Impd)
arcpy.mapping.AddLayer(df,WaterImpd_Layer,"BOTTOM")


# Process: Slope (2)
arcpy.AddMessage("Get Slope from DEM")
# Execute Slope
outSlope = Slope(DEM2, "DEGREE", "0.304800609601219")
# Save the output
outSlope.save(Sloper)


# Process: Con
arcpy.AddMessage("High Slope")
HighSlopeImpedance = 99
inTrueRaster = (HighSlopeImpedance)
whereClause = "VALUE >= 45"
outCon = Con(Raster(Sloper), inTrueRaster, "", whereClause)
# Save the outputs
outCon.save(High_Slope)
del outCon
HighSlope_Layer=arcpy.mapping.Layer(High_Slope)
arcpy.mapping.AddLayer(df,HighSlope_Layer,"BOTTOM")

#arcpy.AddMessage("Mosaic the following Rasters: Road_Impd, Trail_Impd, Water_Impd")
#inputRas = '"' + str(Road_Impd) + ';' + str(Trail_Impd) + ';' + str(Water_Impd) + '"'
#arcpy.AddMessage(inputRas)
#arcpy.MosaicToNewRaster_management(inputRas,env.workspace, ImpedPre, spn, "8_BIT_UNSIGNED", "", "1", "MINIMUM","MATCH")
#ImpedPre_Layer=arcpy.mapping.Layer(ImpedPre)
#arcpy.mapping.AddLayer(df,ImpedPre_Layer,"BOTTOM")

# Process: Raster Calculator (9)
arcpy.AddMessage("Get Impedance layer")
outCon = Con(IsNull(Raster(Road_Impd)), Con(IsNull(Raster(Trail_Impd)), Con(IsNull(Raster(High_Slope)), Con(IsNull(Raster(Water_Impd)),Raster(Veggie_Impd), Raster(Water_Impd)),Raster(High_Slope)),Raster(Trail_Impd)), Raster(Road_Impd))
#outCon = Con(IsNull(Raster(ImpedPre)), Con(IsNull(Raster(High_Slope)), Raster(Veggie_Impd), Raster(High_Slope)),Raster(ImpedPre))
outCon.save(Impedance)
del outCon
arcpy.mapping.RemoveLayer(df,TrailImpd_Layer)
arcpy.mapping.RemoveLayer(df,RoadImpd_Layer)
arcpy.mapping.RemoveLayer(df,WaterImpd_Layer)
arcpy.mapping.RemoveLayer(df,HighSlope_Layer)
arcpy.mapping.RemoveLayer(df,VeggieImpd_Layer)
#arcpy.mapping.RemoveLayer(df,ImpedPre_Layer)

arcpy.AddMessage("Slope Speed")
Div1 = 57.29578
outDivide = Exp(-3.5*Abs(Tan(Raster(Sloper)/Div1)+0.05))*6.0
outDivide.save(walkspd_kph)
del outDivide
arcpy.AddMessage("Seconds per meter")
outTimes = 3.6/Raster(walkspd_kph)
outTimes.save(walkspd_secpme)
del outTimes
arcpy.AddMessage("Traveling spm")
#outDivide = Raster(walkspd_secpme)*(1.0+Float(Raster(Impedance))/100.0)
outDivide = Raster(walkspd_secpme)*Exp(Float(Raster(Impedance)))
outDivide.save(Travspd_spm)
del outDivide


# Process: Times
#outTimes = Raster(walkspd_kph)*Miles_per_Km_Conversion
#outTimes.save(walkspd_mph)

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
arcpy.mapping.RemoveLayer(df,IPPDist_Layer)
arcpy.Delete_management(IPP_dist)
arcpy.Delete_management(NLCD_Clip)
arcpy.Delete_management(NLCD_Resample2)
arcpy.Delete_management(Trails_Clipped)
arcpy.Delete_management(Roads_Clipped)
arcpy.Delete_management(Water_Clipped)
arcpy.Delete_management(Roads_Buf)
arcpy.Delete_management(Trails_Buf)

arcpy.Delete_management(Impedance)
arcpy.Delete_management(High_Slope)
arcpy.Delete_management(PthDis_travsp)
arcpy.Delete_management(blnk_travsppd)
arcpy.Delete_management(travtimhr_rcl)
arcpy.Delete_management(traveltime_hrs_poly)
arcpy.Delete_management(Water_Impd)
arcpy.Delete_management(Trail_Impd)
arcpy.Delete_management(Road_Impd)
arcpy.Delete_management(Veggie_Impd)
#arcpy.Delete_management(ImpedPre)
arcpy.Delete_management(TravTime_hrs)
arcpy.Delete_management(Travspd_spm)



