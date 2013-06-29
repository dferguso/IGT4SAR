# ---------------------------------------------------------------------------
# IPP_EuclideanDistance.py
# Created on: 2011-12-15
# Author: Don Ferguson
# Usage: IPP_EuclideanDistance <IPP> <Subject_Category> <Distances> (optional) <outputDistFromIPP>
# Description:
# Utilizes the multiple ring buffer tool to determine the statistical Horizontal Distance
# from the IPP table (book ?Lost Person Behavior?
# by Robert J. Koester)

# Import arcpy module
import arcpy
import string

# Script arguments
SubNum = arcpy.GetParameterAsText(0)  # Get the subject number
IPP = arcpy.GetParameterAsText(1)  # Determine to use PLS or LKP
UserSelect = arcpy.GetParameterAsText(2)  # Subejct Category or User Defined Values
IPPDists = arcpy.GetParameterAsText(3)  # Optional - User entered distancesDetermine to use PLS or LKP
bufferUnit = arcpy.GetParameterAsText(4) # Optional -
IPPBuffer = arcpy.GetParameterAsText(5)

#arcpy.env.workspace = workspc

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True
#IPPBuffer = "Planning\StatisticalArea"

SubNum = int(SubNum)
fc1="Incident_Info"
rows = arcpy.SearchCursor(fc1)
row = rows.next()

while row:
    # you need to insert correct field names in your getvalue function
    EcoReg = row.getValue("Eco_Region")
    Terrain = row.getValue("Terrain")
    PopDen = row.getValue("Pop_Den")
    row = rows.next()
del rows
del row

fc2 = "Subject_Information"
where = '"Subject_Number"= %d' % (SubNum)
rows = arcpy.SearchCursor(fc2, where)
row = rows.next()

while row:
    # you need to insert correct field names in your getvalue function
    Subject_Category = row.getValue("Category")
    row = rows.next()
del rows
del row
del where

if UserSelect=='User Defined Values':
    Dist = IPPDists.split(',')
    Distances=map(float,Dist)
    Distances.sort()
    arcpy.AddMessage(Distances)

else:
    bufferUnit = "miles"
    arcpy.AddMessage(Subject_Category)

    if Subject_Category == "Abduction":
        Distances = [0.2,1.5,12.0]

    elif Subject_Category == "Aircraft":
        Distances = [0.4,0.9,3.7,10.4]

    elif Subject_Category == "Angler":
        if EcoReg == "Temperate":
            if Terrain == "Mountainous":
                Distances = [0.2,0.9,3.4,6.1]
            else:
                Distances = [0.5,1.0,3.4,6.1]
        elif EcoReg == "Dry":
            Distances = [2.0,6.0,6.5,8.0]
        else:
            Distances = [0.5,1.0,3.4,6.1]

    elif Subject_Category == "All Terrain Vehicle":
        Distances = [1.0,2.0,3.5,5.0]

    elif Subject_Category == "Autistic":
        if EcoReg == "Urban":
            Distances = [0.2,0.6,2.4,5.0]
        else:
            Distances = [0.4,1.0,2.3,9.5]

    elif Subject_Category == "Camper":
        if Terrain == "Mountainous":
            if EcoReg == "Dry":
                Distances = [0.4,1.0,2.6,20.3]
            else:
                Distances = [0.1,1.4,1.9,24.7]
        else:
            Distances = [0.1,0.7,2.0,8.0]

    elif Subject_Category == "Child (1-3)":
        if EcoReg == "Dry":
            Distances = [0.4,0.8,2.4,5.6]
        elif EcoReg == "Urban":
            Distances = [0.1,0.3,0.5,0.7]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.1,0.2,0.6,2.0]
        else:
            Distances = [0.1,0.2,0.6,2.0]

    elif Subject_Category == "Child (4-6)":
        if EcoReg == "Dry":
            Distances = [0.4,1.2,2.0,5.1]
        elif EcoReg == "Urban":
            Distances = [0.06,0.3,0.6,2.1]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.1,0.5,0.9,2.3]
        else:
            Distances = [0.1,0.4,0.9,4.1]

    elif Subject_Category == "Child (7-9)":
        if EcoReg == "Dry":
            Distances = [0.3,0.8,2.0,4.5]
        elif EcoReg == "Urban":
            Distances = [0.1,0.3,0.9,3.2]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.5,1.0,2.0,7.0]
        else:
            Distances = [0.1,0.5,1.3,5.0]

    elif Subject_Category == "Child (10-12)":
        if EcoReg == "Dry":
            Distances = [0.5,1.3,4.5,10.0]
        elif EcoReg == "Urban":
            Distances = [0.2,0.9,1.8,3.6]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.5,1.0,2.0,5.6]
        else:
            Distances = [0.3,1.0,3.0,6.2]

    elif Subject_Category == "Child (13-15)":
        if EcoReg == "Dry":
            Distances = [1.5,2.0,3.0,7.4]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.5,1.3,3.0,13.3]
        else:
            Distances = [0.4,0.8,2.0,6.2]

    elif Subject_Category == "Climber":
        Distances = [0.1,1.0,2.0,9.2]

    elif Subject_Category == "Dementia":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            Distances = [0.6,1.2,1.9,3.8]
        elif EcoReg == "Dry" and Terrain == "Flat":
            Distances = [0.3,1.0,2.2,7.3]
        elif EcoReg == "Urban":
            Distances = [0.2,0.7,2.0,7.8]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.2,0.5,1.2,5.1]
        else:
            Distances = [0.2,0.6,1.5,7.9]

    elif Subject_Category == "Despondent":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            Distances = [0.5,1.0,2.1,11.1]
        elif EcoReg == "Dry" and Terrain == "Flat":
            Distances = [0.3,1.2,2.3,12.8]
        elif EcoReg == "Urban":
            Distances = [0.06,0.3,0.9,8.1]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.2,0.7,2.0,13.3]
        else:
            Distances = [0.2,0.5,1.4,10.7]

    elif Subject_Category == "Gatherer":
        if EcoReg == "Dry":
            Distances = [1.0,1.6,3.6,6.9]
        else:
            Distances = [0.9,2.0,4.0,8.0]

    elif Subject_Category == "Hiker":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            Distances = [1.0,2.0,4.0,11.9]
        elif EcoReg == "Dry" and Terrain == "Flat":
            Distances = [0.8,1.3,4.1,8.1]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.7,1.9,3.6,11.3]
        else:
            Distances = [0.4,1.1,2.0,6.1]

    elif Subject_Category == "Horseback Rider":
        Distances = [0.2,2.0,5.0,12.2]

    elif Subject_Category == "Hunter":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            Distances = [1.3,3.0,5.0,13.8]
        elif EcoReg == "Dry" and Terrain == "Flat":
            Distances = [1.0,1.9,4.0,7.0]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.6,1.3,3.0,10.7]
        else:
            Distances = [0.4,1.0,1.9,8.5]

    elif Subject_Category == "Mental Illness":
        if EcoReg == "Urban":
            Distances = [0.2,0.4,0.9,7.7]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.4,1.4,5.1,9.0]
        else:
            Distances = [0.5,0.6,1.4,5.0]

    elif Subject_Category == "Mental Retardation":
        if EcoReg == "Dry":
            Distances = [0.7,2.5,5.4,38.9]
        elif EcoReg == "Urban":
            Distances = [0.2,0.5,2.3,6.14]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.4,1.0,2.0,7.0]
        else:
            Distances = [0.2,0.6,1.3,7.3]

    elif Subject_Category == "Mountain Biker":
        if EcoReg == "Dry":
            Distances = [1.7,4.0,8.2,18.1]
        else:
            Distances = [1.9,2.5,7.0,15.5]

    elif Subject_Category == "Other (Extreme Sport)":
        Distances = [0.3,1.6,3.5,8.3]

    elif Subject_Category == "Runner":
        Distances = [0.9,1.6,2.1,3.6]

    elif Subject_Category == "Skier-Alpine":
        Distances = [0.7,1.7,3.0,9.4]

    elif Subject_Category == "Skier-Nordic":
        if EcoReg == "Dry":
            Distances = [1.2,2.7,4.0,12.1]
        else:
            Distances = [1.0,2.2,4.0,12.2]

    elif Subject_Category == "Snowboarder":
        Distances = [1.0,2.0,3.8,9.5]

    elif Subject_Category == "Snowmobiler":
        if EcoReg == "Dry":
            Distances = [1.0,3.0,8.7,18.9]
        elif EcoReg == "Temperate" and Terrain == "Flat":
                Distances = [0.8,2.9,25.5,59.7]
        else:
            Distances = [2.0,4.0,6.9,10.0]

    elif Subject_Category == "Substance Abuse":
        Distances = [0.3,0.7,2.6,6.0]

    else:
        Distances = [0.4,1.1,2.0,6.1]


# Buffer areas of impact around major roads
fc3 = "Plan_Point"

where1 = '"Subject_Number" = ' + str(SubNum)
where2 = ' AND "IPPType" = ' + "'" + IPP + "'"
where = where1 + where2

dissolve_option = "ALL"

arcpy.AddMessage(where)

rows = arcpy.SearchCursor(fc3, where)
row = rows.next()

while row:
    # you need to insert correct field names in your getvalue function
    arcpy.MultipleRingBuffer_analysis(fc3, IPPBuffer, Distances, bufferUnit, "DistFrmIPP", dissolve_option, "FULL")
    row = rows.next()
del rows
del row
del where

perct = ['25%', '50%', '75%', '95%']
inFeatures = IPPBuffer
fieldName1 = "Descrip"
fieldName2 = "Area_Ac"
fieldName3 = "Area_SqMi"

fieldAlias1 = "Description"
fieldAlias2 = "Area (Acres)"
fieldAlias3 = "Area (sq miles)"

expression2 = "!shape.area@acres!"
expression3 = "!shape.area@squaremiles!"

arcpy.AddField_management(inFeatures, fieldName1, "TEXT", "", "", "25",
                          fieldAlias1, "NULLABLE", "","PrtRange")
arcpy.AddField_management(inFeatures, fieldName2, "DOUBLE", "", "", "",
                          fieldAlias2, "NULLABLE")
arcpy.AddField_management(inFeatures, fieldName3, "DOUBLE", "", "", "",
                          fieldAlias3, "NULLABLE")
arcpy.CalculateField_management(IPPBuffer, fieldName2, expression2,
                                    "PYTHON")
arcpy.CalculateField_management(IPPBuffer, fieldName3, expression3,
                                    "PYTHON")

rows = arcpy.UpdateCursor(IPPBuffer)
row = rows.next()

k=0
while row:
    # you need to insert correct field names in your getvalue function
    row.setValue(fieldName1, perct[k])
    rows.updateRow(row)
    k=k+1
    row = rows.next()

del rows
del row
##del where

# get the map document
mxd = arcpy.mapping.MapDocument("CURRENT")

# get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

# create a new layer
insertLayer = arcpy.mapping.Layer(IPPBuffer)
#Reference layer
refLayer = arcpy.mapping.ListLayers(mxd, "Hasty_Points", df)[0]
# add the layer to the map at the bottom of the TOC in data frame 0

arcpy.mapping.InsertLayer(df, refLayer, insertLayer,"BEFORE")



