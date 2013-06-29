#-------------------------------------------------------------------------------
# Name:        CostDistanceModel.py
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
#workspc = arcpy.GetParameterAsText(0)
#env.workspace = workspc
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

mxd = arcpy.mapping.MapDocument("CURRENT")
df=arcpy.mapping.ListDataFrames(mxd,"*")[0]

Roads = arcpy.GetParameterAsText(0)
if Roads == '#' or not Roads:
    Roads = "Roads" # provide a default value if unspecified

Trails = arcpy.GetParameterAsText(1)
if Trails == '#' or not Trails:
    Trails = "Trails" # provide a default value if unspecified

Water = arcpy.GetParameterAsText(2)
if Water == '#' or not Water:
    Water = "Base_Data\Water" # provide a default value if unspecified

NLCD = arcpy.GetParameterAsText(3)
if NLCD == '#' or not NLCD:
    NLCD = "NLCD" # provide a default value if unspecified

DEM2 = arcpy.GetParameterAsText(4)
if DEM2 == '#' or not DEM2:
    DEM2 = "DEM" # provide a default value if unspecified

Fence = arcpy.GetParameterAsText(5)
if Fence == '#' or not Fence:
    Fence = "FenceLine" # provide a default value if unspecified

Electric = arcpy.GetParameterAsText(6)
if Electric == '#' or not Electric:
    Electric = "PowerLines" # provide a default value if unspecified

TheoDist = arcpy.GetParameterAsText(7)
if TheoDist == '#' or not TheoDist:
    TheoDist = "0" # provide a default value if unspecified

#High_Slope_Degrees = arcpy.GetParameterAsText(8)
#if High_Slope_Degrees == '#' or not High_Slope_Degrees:
#    High_Slope_Degrees = "45" # provide a default value if unspecified

#Tables
cfcc = "cfcc"
TrailClass = "Trail_Class"
LandCoverClass = "LandCover_Class"
TimeTable = "TimeTable"

#File Names:
#Fence = "Base_Data\FenceLine"
#Electric = "Base_Data\PowerLines"
IPP = "Incident\Plan_Point"
#IPP = "Plan_Point"
IPP_dist = "IPPTheoDistance"
Roads_Clipped = "Roads_Clipped"
Roads_Buf = "Roads_Buffered"
Trails_Clipped = "Trails_Clipped"
Trails_Buf = "Trails_Buffered"
Electric_Clipped = "Electric_Clipped"
Electric_Buf = "Electric_Buffered"
Fence_Clipped = "Fence_Clipped"
Fence_Buf = "Fence_Buffered"
Water_Clipped = "Water_Clipped"
clip_Block = "clip_block"
NLCD_Clip = "NLCD_clipped"
DEM_Clip = "DEM_clipped"
#
NLCD_Resample2 = "NLCD_Resample"

# Rasters
Water_Impd = "Water_Impd"
Trail_Impd = "Trail_Impd"
Road_Impd = "Road_Impd"
Utility_Impd = "Utility_Impd"
Fence_Impd = "Fence_Impd"
Veggie_Impd = "NLCD_Impd"
ImpedPre = "Imped_Pre"

#
Sloper = "Slope"
High_Slope = "High_Slope"
walkspd_kph = "walkspd_kph"
walkspd_secpme = "walkspd_secpme"
walkspd_mph = "walkspd_mph"
Impedance = "Impedance"
Travspd_kph = "TravSpd_kph"

# Local variables:
Input_true_raster_or_constant_value = "1"
TheoSearch = str(TheoDist) + " MILES"
v3600 = "3600"
Miles_per_Km_Conversion = 0.6213711922
High_Slope_Degrees = "45"

travspd_rcl = "TravSpd_rcl"
travelspd_poly = "TravelSpd_poly"
TravSpd_kph = "TravSpdPoly_kph"


try:
    arcpy.Delete_management(IPP_dist)
except:
    pass



# Set the cell size environment using a raster dataset.
arcpy.env.cellSize = DEM2


# Process: Buffer for theoretical search area
arcpy.AddMessage("Buffer IPP")
arcpy.Buffer_analysis(IPP, IPP_dist, TheoSearch)
IPPDist_Layer=arcpy.mapping.Layer(IPP_dist)
arcpy.mapping.AddLayer(df,IPPDist_Layer,"BOTTOM")
spatialRef = arcpy.Describe(IPP_dist).SpatialReference
spn =spatialRef
arcpy.AddMessage(spn.name)

desc = arcpy.Describe(IPP_dist)
extent = desc.extent
YDist = abs(extent.YMax-extent.YMin)
XDist =abs(extent.XMax-extent.XMin)

if YDist >= XDist:
    CellSize=XDist/250.0
else:
    CellSize=YDist/250.0
##XCell = arcpy.GetRasterProperties_management(DEM2,"CELLSIZEX")
##YCell =arcpy.GetRasterProperties_management(DEM2,"CELLSIZEY")
##CellSize = "'" + str(XCell) + " " + str(YCell) + "'"
##arcpy.AddMessage(CellSize)


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

# Process: Clip PowerLines
arcpy.AddMessage("Clip Power Lines and buffer to 10 meters")
arcpy.Clip_analysis(Electric, IPP_dist, Electric_Clipped, "")
# Process: Buffer for theoretical search area
arcpy.Buffer_analysis(Electric_Clipped, Electric_Buf, "10 Meters")

# Process: Clip Fences
arcpy.AddMessage("Clip Fences and buffer to 10 meters")
arcpy.Clip_analysis(Fence, IPP_dist, Fence_Clipped, "")
# Process: Buffer for theoretical search area
arcpy.Buffer_analysis(Fence_Clipped, Fence_Buf, "10 Meters")

# Process: Clip Raster NLCD
arcpy.AddMessage("Clip NLCD")
arcpy.Clip_management(NLCD, "#", NLCD_Clip, IPP_dist, "", "ClippingGeometry")
NLCDClip_Layer=arcpy.mapping.Layer(NLCD_Clip)
arcpy.mapping.AddLayer(df,NLCDClip_Layer,"BOTTOM")


# Process: Resample
arcpy.AddMessage("Resample NLCD")
arcpy.AddMessage(DEM2)
arcpy.Resample_management(NLCD_Clip, NLCD_Resample2, CellSize, "NEAREST")
arcpy.mapping.RemoveLayer(df,NLCDClip_Layer)
NLCDResamp=arcpy.mapping.Layer(NLCD_Resample2)
arcpy.mapping.AddLayer(df,NLCDResamp,"BOTTOM")
# Process: Add Join (3)
arcpy.AddMessage("Land Cover Impedance - Join Table w/ NLCD")
arcpy.AddJoin_management(NLCD_Resample2, "VALUE", LandCoverClass, "LCCC", "KEEP_ALL")
arcpy.AddMessage("Done")

#####################
### Process: Lookup
##arcpy.AddMessage("Create Veggie Impedance Layer")
###arcpy.gp.Lookup_sa(NLCD_Resample2, "LandCover_Class.Walk_Impd", Veggie_Impd)  --- old one
### Execute Lookup --- New one
##outRaster = Lookup(NLCD_Resample2, "LandCover_Class.Walk_Impd")
### Save the output
##outRaster.save(Veggie_Impd)

# Process: Lookup
arcpy.AddMessage("Create Veggie Impedance Layer")
arcpy.gp.Lookup_sa(NLCD_Resample2, "LandCover_Class.Walk_Impd", Veggie_Impd)
arcpy.mapping.RemoveLayer(df,NLCDResamp)
VeggieImpd_Layer=arcpy.mapping.Layer(Veggie_Impd)
arcpy.mapping.AddLayer(df,VeggieImpd_Layer,"BOTTOM")
#####################

#arcpy.mapping.RemoveLayer(df,NLCDResamp)
VeggieImpd_Layer=arcpy.mapping.Layer(Veggie_Impd)
arcpy.mapping.AddLayer(df,VeggieImpd_Layer,"BOTTOM")

# Process: Add Join for Trails
TrailBuf_Layer=arcpy.mapping.Layer(Trails_Buf)
arcpy.mapping.AddLayer(df,TrailBuf_Layer,"BOTTOM")
arcpy.AddJoin_management(Trails_Buf, "MAINT_LVL", TrailClass, "Trail_Clas", "KEEP_ALL")
# Process: Polyline to Raster
arcpy.AddMessage("create Trail Impedance Layer")
arcpy.PolygonToRaster_conversion(Trails_Buf, "Trail_Class.Walk_Impd", Trail_Impd, "CELL_CENTER", "NONE", CellSize)
arcpy.mapping.RemoveLayer(df,TrailBuf_Layer)
TrailImpd_Layer=arcpy.mapping.Layer(Trail_Impd)
arcpy.mapping.AddLayer(df,TrailImpd_Layer,"BOTTOM")

# Process: Add Join for Roads
RoadBuf_Layer=arcpy.mapping.Layer(Roads_Buf)
arcpy.mapping.AddLayer(df,RoadBuf_Layer,"BOTTOM")
arcpy.AddJoin_management(Roads_Buf, "CFCC", cfcc, "CFCC", "KEEP_ALL")
# Process: Polyline to Raster (3)
arcpy.AddMessage("create Road Impedance Layer")
arcpy.PolygonToRaster_conversion(Roads_Buf, "cfcc.Walk_Impd", Road_Impd, "CELL_CENTER", "NONE", CellSize)
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
arcpy.PolygonToRaster_conversion(Water_Clipped, "Impedance", Water_Impd, "CELL_CENTER", "NONE", CellSize)
WaterImpd_Layer=arcpy.mapping.Layer(Water_Impd)
arcpy.mapping.AddLayer(df,WaterImpd_Layer,"BOTTOM")

# Check to see if the Utility polyline already has a "Impd" field.  If not create on
UtilityImpedance = 30
if len(arcpy.ListFields(Electric_Buf,"Impedance")) > 0:
    arcpy.CalculateField_management(Electric_Buf,"Impedance",UtilityImpedance)
else:
    # Add the new field and calculate the value
    arcpy.AddField_management(Electric_Buf, "Impedance", "SHORT")
    arcpy.CalculateField_management(Electric_Buf,"Impedance",UtilityImpedance)

# Process: Polyline to Raster
arcpy.AddMessage("create Utility Impedance Layer")
arcpy.PolygonToRaster_conversion(Electric_Buf, "Impedance", Utility_Impd, "CELL_CENTER", "NONE", CellSize)
UtilityImpd_Layer=arcpy.mapping.Layer(Utility_Impd)
arcpy.mapping.AddLayer(df,UtilityImpd_Layer,"BOTTOM")


# Check to see if the Fence polyline already has a "Impd" field.  If not create on
FenceImpedance = 99
if len(arcpy.ListFields(Fence_Buf,"Impedance")) > 0:
    arcpy.CalculateField_management(Fence_Buf,"Impedance",FenceImpedance)
else:
    # Add the new field and calculate the value
    arcpy.AddField_management(Fence_Buf, "Impedance", "SHORT")
    arcpy.CalculateField_management(Fence_Buf,"Impedance",FenceImpedance)

# Process: Polyline to Raster
arcpy.AddMessage("create Fence Impedance Layer")
arcpy.PolygonToRaster_conversion(Fence_Buf, "Impedance", Fence_Impd, "CELL_CENTER", "NONE", CellSize)
FenceImpd_Layer=arcpy.mapping.Layer(Fence_Impd)
arcpy.mapping.AddLayer(df,FenceImpd_Layer,"BOTTOM")

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

arcpy.AddMessage("Mosaic the following Rasters: Road_Impd, Trail_Impd, Water_Impd, Utility_Impd, Fence_Impd")
inputRas = '"' + str(Road_Impd) + ';' + str(Trail_Impd) + ';' + str(Water_Impd) + ';' + str(Utility_Impd) + ';' + str(Fence_Impd) + '"'
##inputRas = '"' + str(Road_Impd) + ';' + str(Trail_Impd) + ';' + str(Water_Impd) +'"'
arcpy.AddMessage(inputRas)
arcpy.MosaicToNewRaster_management(inputRas,env.workspace, ImpedPre, spn, "8_BIT_UNSIGNED", "", "1", "MINIMUM","MATCH")
ImpedPre_Layer=arcpy.mapping.Layer(ImpedPre)
arcpy.mapping.AddLayer(df,ImpedPre_Layer,"BOTTOM")

# Process: Raster Calculator (9)
arcpy.AddMessage("Get Impedance layer")
##outCon = Con(IsNull(Raster(Road_Impd)), Con(IsNull(Raster(Trail_Impd)), Con(IsNull(Raster(High_Slope)), Con(IsNull(Raster(Veggie_Impd)),Raster(Water_Impd), Raster(Veggie_Impd)),Raster(High_Slope)),Raster(Trail_Impd)), Raster(Road_Impd))
outCon = Con(IsNull(Raster(Fence_Impd)),Con(IsNull(Raster(Road_Impd)), Con(IsNull(Raster(Trail_Impd)), Con(IsNull(Raster(Utility_Impd)), Con(IsNull(Raster(High_Slope)), Con(IsNull(Raster(Veggie_Impd)),Raster(Water_Impd), Raster(Veggie_Impd)),Raster(High_Slope)),Raster(Utility_Impd)),Raster(Trail_Impd)), Raster(Road_Impd)), Raster(Fence_Impd))
##outCon = Con(IsNull(Raster(ImpedPre)), Con(IsNull(Raster(High_Slope)), Raster(Veggie_Impd), Raster(High_Slope)),Raster(ImpedPre))
outCon.save(Impedance)
del outCon
arcpy.mapping.RemoveLayer(df,TrailImpd_Layer)
arcpy.mapping.RemoveLayer(df,RoadImpd_Layer)
arcpy.mapping.RemoveLayer(df,WaterImpd_Layer)
arcpy.mapping.RemoveLayer(df,UtilityImpd_Layer)
arcpy.mapping.RemoveLayer(df,FenceImpd_Layer)
arcpy.mapping.RemoveLayer(df,HighSlope_Layer)
##arcpy.mapping.RemoveLayer(df,VeggieImpd_Layer)
arcpy.mapping.RemoveLayer(df,ImpedPre_Layer)

arcpy.AddMessage("Tobler Slope Speed")
Div1 = 57.29578
outDivide = Exp(-3.5*Abs(Tan(Raster(Sloper)/Div1)+0.05))*6.0
outDivide.save(walkspd_kph)
del outDivide

arcpy.AddMessage("Traveling Speed - kph")
outDivide = Raster(walkspd_kph)/Exp(0.0212*Float(Raster(Impedance)))
outDivide.save(Travspd_kph)
del outDivide

#Travspd_Layer=arcpy.mapping.Layer(Travspd_kph)
#arcpy.mapping.AddLayer(df,Travspd_Layer,"BOTTOM")


arcpy.mapping.RemoveLayer(df,IPPDist_Layer)
arcpy.Delete_management(IPP_dist)
arcpy.Delete_management(NLCD_Clip)
arcpy.Delete_management(NLCD_Resample2)
arcpy.Delete_management(Trails_Clipped)
arcpy.Delete_management(Roads_Clipped)
arcpy.Delete_management(Water_Clipped)
arcpy.Delete_management(Roads_Buf)
arcpy.Delete_management(Trails_Buf)
arcpy.Delete_management(Electric_Clipped)
arcpy.Delete_management(Fence_Clipped)
arcpy.Delete_management(Electric_Buf)
arcpy.Delete_management(Fence_Buf)
####
arcpy.Delete_management(Impedance)
arcpy.Delete_management(High_Slope)
arcpy.Delete_management(Water_Impd)
arcpy.Delete_management(Trail_Impd)
arcpy.Delete_management(Road_Impd)
arcpy.Delete_management(Utility_Impd)
arcpy.Delete_management(Fence_Impd)
##arcpy.Delete_management(Veggie_Impd)
arcpy.Delete_management(ImpedPre)
arcpy.Delete_management(walkspd_kph)

