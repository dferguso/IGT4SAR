#-------------------------------------------------------------------------------
# Name:        Coverage_Model.py
# Purpose:
#
# Author:      Don Ferguson
# Organization: Appalachian Search and Rescue Conference
# Created:     16/12/2011
# Description: For use in MapSAR
# Feature classes impacted:


#-------------------------------------------------------------------------------
#!/usr/bin/env python

# Import arcpy module
import arcpy
import string
import math

#workspc = arcpy.GetParameterAsText(0)

#arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"

fc1 = "Routes_Line"
fc2 = "Debriefing"
fc3 = "Search_Segments"
fc4 = "Probability_Regions"
fc5 = "GPS_Data\GPSBuffer"
fc6 = "GPS_Data\GPSBuffer_Intersect"
fc7 = "GPS_Data\GPS_Overlap"
fc8 = "GPS_Data\GPS_Erase"
fc9 = "GPS_Data\GPS_Merge"
fc10 = "GPS_Data\Seg_Intersect"
fc11 = "GPS_Data\Seg_Dissolve"
fc12 = "GPS_Data\Reg_Dissolve"


# Set local variables
fieldName0 = "MilageOfTrack"
fieldName1 = "Area_1"
fieldPrecision = 9
fieldName2 = "Area_Name"
fieldName3= "Coverage"
fieldName4s = "Area_seg"
fieldName4r = "Area"
fieldName5 = "Region_Name"
fieldName6 = "PODTheo"
fieldName7 = "POStheo"
fieldName8= "COVER"
fieldName9= "XY_CENT"

try:
    arcpy.DeleteFeatures_management(fc5)
except:
    pass
try:
    arcpy.DeleteFeatures_management(fc6)
except:
    pass

check = "False"
fieldList = arcpy.ListFields(fc1)
for field in fieldList:
    if (field.name == "Sweep"):
        check="True"

if check != "True":
    arcpy.AddField_management(fc1, "Sweep", "FLOAT", fieldPrecision, "", "", "Sweep", "NULLABLE")

rows1 = arcpy.UpdateCursor(fc1)
row1 = rows1.next()

while row1:
    # you need to insert correct field names in your getvalue function
    AssignNumber = row1.Assignment_Number
    where2 = '"Assignment_Number" = ' + "'" + str(AssignNumber) + "'"
    rows2 = arcpy.SearchCursor(fc2, where2)
    row2 = rows2.next()

    arcpy.AddMessage(AssignNumber)

    while row2:
        # you need to insert correct field names in your getvalue function
        TeamSize = row2.Team_Size
        SweepWidth = row2.SweepWidth_m
        GPSLoc = row2.GPSLoc
        Sweep = TeamSize * SweepWidth*2.0
        row1.Sweep = Sweep
        row2 = rows2.next()

    del where2
    del row2
    del rows2
###############################################################################
    row1.Processed = 1
###############################################################################
##    if GPSLoc == "Left":
##        GPSLoc = "LEFT"
##    elif GPSLoc == "Right":
##        GPSLoc = "RIGHT"
##    else:
##        GPSLoc = "FULL"
##    row1.GPSLoc = GPSLoc

    rows1.updateRow(row1)
    row1 = rows1.next()

del row1
del rows1
del AssignNumber
del TeamSize
del SweepWidth
del GPSLoc

arcpy.AddMessage(" ")
arcpy.AddMessage("Calculate length of GPS tracks.")
arcpy.AddMessage(" ")
expression0 = "!shape.length@miles!"
arcpy.CalculateField_management(fc1, fieldName0, expression0,"PYTHON")

arcpy.AddMessage("Buffer GPS tracks to account for sweepwidth and team size.")
arcpy.AddMessage(" ")
# Buffer areas around GPS track
bufferUnit = "meters"
distanceField = "TeamSweep_m"
sideType = "GPSLoc"
dissolveType = "NONE"
arcpy.Buffer_analysis(fc1, fc5, Sweep, "","", dissolveType, "")
arcpy.DeleteField_management(fc1, "Sweep")

del bufferUnit
del distanceField
del sideType
del dissolveType
del Sweep



# Execute AddField
arcpy.AddField_management(fc5, fieldName8, "SHORT")
arcpy.CalculateField_management(fc5, fieldName8, "1","PYTHON")

arcpy.AddMessage("Intersection analysis between GPS tracks and Search Segments")
arcpy.AddMessage(" ")
# Process: Intersect
arcpy.Intersect_analysis(fc5, fc6, "ALL", "", "INPUT")

# Execute AddField
arcpy.AddField_management(fc6, fieldName9, "TEXT")
expression0 = "str(!shape.centroid!)"
arcpy.CalculateField_management(fc6, fieldName9, expression0,"PYTHON")

arcpy.Dissolve_management(fc6, fc7, ["XY_CENT"], [["XY_CENT", "COUNT"]],"SINGLE_PART", "DISSOLVE_LINES")
#arcpy.Delete_management(fc6)

arcpy.AddField_management(fc7, fieldName8, "SHORT")
expression0 = "!COUNT_XY_CENT!"
arcpy.CalculateField_management(fc7, fieldName8, expression0,"PYTHON")


###########################Stopped here#################3
##ERASE
arcpy.Erase_analysis(fc5, fc7, fc8)

##MERGE
# Create FieldMappings object to manage merge output fields
fieldMappings = arcpy.FieldMappings()
fieldMappings.addTable(fc7)
fieldMappings.addTable(fc8)
for field in fieldMappings.fields:
    if field.name not in [fieldName8]:
        fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))

arcpy.Merge_management([fc8, fc7], fc9, fieldMappings)
#arcpy.Delete_management(fc5)
#arcpy.Delete_management(fc7)
#arcpy.Delete_management(fc8)

####INTERSECT BY SEGMENTS
fieldName10 = "aCOVER"
arcpy.Intersect_analysis([fc9,fc3], fc10, "ALL", "", "INPUT")
arcpy.AddField_management(fc10, fieldName10, "FLOAT")
expression0 = "!COVER! * !shape.area@acres!"
arcpy.CalculateField_management(fc10, fieldName10, expression0,"PYTHON")
#arcpy.Delete_management(fc9)

####DISSOLVE by AREA_NAME and sum "AREA_SEG"
dissolveFields = "Area_Name"
statistics_fields = "aCOVER SUM"
arcpy.Dissolve_management(fc10, fc11, dissolveFields, statistics_fields,"MULTI_PART")
####DISSOLVE by REGION_NAME and sum "AREA_SEG"
dissolveFields = "Region_Name"
arcpy.Dissolve_management(fc10, fc12, dissolveFields, statistics_fields,"MULTI_PART")
#arcpy.Delete_management(fc10)
del dissolveFields
del statistics_fields
##
##
##
rows2 = arcpy.UpdateCursor(fc3)
row2 = rows2.next()
Cover = 0.0

while row2:
    AreaName = row2.Area_Name
    AreaSeg = row2.Area_seg
    where3 = '"Area_Name" = ' + "'" + AreaName + "'"

    if AreaSeg == None:
        arcpy.AddMessage("Segment: " +AreaName + ", area is Null")
    elif AreaSeg == 0.0:
        arcpy.AddMessage("Segment: " +AreaName + ", area is zero")
    else:
        AreaCov = 0.0
        rows3 = arcpy.SearchCursor(fc11,where3)
        row3 = rows3.next()

        while row3:
            AreaCov = row3.SUM_aCOVER ##+ AreaCov
            row3 = rows3.next()

        Cover = AreaCov/AreaSeg
        del AreaCov
        del row3
        del rows3

    row2.Coverage = Cover
    rows2.updateRow(row2)
    row2 = rows2.next()
##
del row2
del rows2
del AreaSeg
del AreaName
del Cover


arcpy.AddMessage("Calculate theoretical POD based on Coverage")
arcpy.AddMessage(" ")

#Calculate theoretical POS based on Coverage and POAcum
expression3 = "(1-math.exp(-!Coverage!))*100.0"
arcpy.CalculateField_management(fc3, fieldName6, expression3,"PYTHON")


rows2 = arcpy.UpdateCursor(fc4)
row2 = rows2.next()
Cover = 0.0

while row2:
    RegName = row2.Region_Name
    AreaReg = row2.Area
    where3 = '"Region_Name" = ' + "'" + RegName + "'"
    Cover = 0.0

    if AreaReg == None:
        arcpy.AddMessage("Region: " +RegName + ", area is Null")
    elif AreaReg == 0.0:
        arcpy.AddMessage("Region: " +RegName + ", area is zero")
    else:
        AreaCov = 0.0
        rows3 = arcpy.SearchCursor(fc12,where3)
        row3 = rows3.next()

        while row3:
            AreaCov = row3.SUM_aCOVER ##+ AreaCov
            row3 = rows3.next()

        Cover = AreaCov/AreaReg
        del AreaCov
        del row3
        del rows3

    row2.Coverage = Cover
    rows2.updateRow(row2)
    row2 = rows2.next()
##
del row2
del rows2
del AreaReg
del RegName
del Cover


arcpy.AddMessage("Calculate theoretical POD based on Coverage")
arcpy.AddMessage(" ")

#Calculate theoretical POS based on Coverage and POAcum
expression4 = "!POA! * (1-math.exp(-!Coverage!))"
arcpy.CalculateField_management(fc4, fieldName7, expression4,"PYTHON")



del expression0
del expression3
del expression4
#arcpy.Delete_management(fc11)
#arcpy.Delete_management(fc12)