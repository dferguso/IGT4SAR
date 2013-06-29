#-------------------------------------------------------------------------------
# Name:        Assignments.py
# Purpose:     Create Task Assignment Forms from selected rows in the
#              Assignments data layer.  New TAFs are stored by Task ID in the
#              Assignments folder
#
# Author:      Don Ferguson
#
# Created:     12/12/2011
# Copyright:   (c) ferguson 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

# Take courage my friend help is on the way
import arcpy
from arcpy import env

# Set overwrite option
arcpy.env.overwriteOutput = True

output = arcpy.GetParameterAsText(0)
AssignNumber = arcpy.GetParameterAsText(1)

arcpy.env.overwriteOutput = "True"

#######
#Automate map production - July 27, 2012
mxd=arcpy.mapping.MapDocument("CURRENT")


fc4 = "Search Segments"
fc5 = "Hasty_Points"
fc6 = "Hasty_Line"
fc7 = "Hasty_Segments"
fcS_lyr = "Operations/AreaSegments"
fcL_lyr = "Operations/LineSegments"
fcP_lyr = "Operations/PointSegments"

clearLyrs = [fc4, fc5, fc6, fc7]

df = arcpy.mapping.ListDataFrames(mxd)[0]
###############
fc1="Incident_Info"
rows = arcpy.SearchCursor(fc1)
row = rows.next()
arcpy.AddMessage("Get Incident Info")

while row:
    # you need to insert correct field names in your getvalue function
    Incident_Name = row.getValue("Incident_Name")
    MapDatum = row.getValue("MapDatum")
    MagDec = row.getValue("MagDec")
    MapCoord = row.getValue("MapCoord")
    Base_Phone = row.getValue("Base_PhoneNumber")
    Base_Freq = row.getValue("Comms_Freq")
    row = rows.next()
del rows
del row

arcpy.AddMessage("Get Assignment Info")
fc2="Assignments"
fc3 = "Operation_Period"

AssignNum = AssignNumber.split(";")
#arcpy.AddMessage(AssignNum[1])
for AssNum in AssignNum:
    arcpy.AddMessage(AssNum)
    where2 = '"Assignment_Number" = ' + "'" + AssNum + "'"

    rows = arcpy.SearchCursor(fc2, where2)
    row = rows.next()
    while row:
        # you need to insert correct field names in your getvalue function
        TaskInstruct = row.getValue("Description")
        PlanNo = row.getValue("Planning_Number")
        ResourceType = row.getValue("Resource_Type")
        Priority = row.getValue("Priority")
        TaskNo = row.getValue("Assignment_Number")
        PreSearch = row.getValue("Previous_Search")
        TeamID = row.getValue("Team")
        TaskMap = row.getValue("Area_Name")
        arcpy.AddMessage("Task Assignment Number " + str(TaskNo))
    ################
    ## Added a joint safety note for the TAF that includes Safety note from Op
    ## Period and any specific safety note from Assignment
        Assign_Safety = row.getValue("Safety_note")

        OpPeriod = row.getValue("Period")
        where3 = '"Period"= %d' % (OpPeriod)
        rows3 = arcpy.SearchCursor(fc3, where3)
        row3 = rows3.next()
        while row3:
            Op_Safety = row3.getValue("Safety_Message")
            row3 = rows3.next()
        del row3
        del rows3
        Notes = "Specific Safety: " + str(Assign_Safety) + "     General Safety: " + \
            str(Op_Safety)
    ################
        PrepBy = row.getValue("Prepared_By")

        #filename = output + "/" + str(PlanNo) + ".fdf"
        filename = output + "/" + str(TaskNo) + ".fdf"

        txt= open (filename, "w")
        txt.write("%FDF-1.2\n")
        txt.write("%????\n")
        txt.write("1 0 obj<</FDF<</F(TAF_Page1_Task.pdf)/Fields 2 0 R>>>>\n")
        txt.write("endobj\n")
        txt.write("2 0 obj[\n")
        txt.write ("\n")
        txt.write("<</T(topmostSubform[0].Page1[0].MissNo[0])/V(" + str(Incident_Name) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].TeamFreq[0])/V(" + str(Base_Freq) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].MagDec[0])/V(" + str(MagDec) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].TaskInstruct[0])/V(" + str(TaskInstruct) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].PlanNo[0])/V(" + str(PlanNo) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].MapDatum[0])/V(" + str(MapDatum) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].MapCoord[0])/V(" + str(MapCoord) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].Table2[0].Row1[1].TactFreq1[0])/V(" + str(TactFreq1) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].ResourceType[0])/V(" + str(ResourceType) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].Priority[0])/V(" + str(Priority) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].TaskNo[0])/V(" + str(TaskNo) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].TeamId[0])/V(" + str(TeamID) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].TaskMap[0])/V(" + str(TaskMap) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].PreSearch[0])/V(" + str(PreSearch) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].EquipIssued[0])/V(" + str(EquipIssued) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].Phone_Base[0])/V(" + str(Base_Phone) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].Phone_Team[0])/V(" + str(Phone_Team) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].GPSIdOut[0])/V(" + str(GPSIdOut) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].Notes[0])/V(" + str(Notes) + ")>>\n")
        txt.write("<</T(topmostSubform[0].Page1[0].PrepBy[0])/V(" + str(PrepBy) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].BriefBy[0])/V(" + str(BriefBy) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].DateOut[0])/V(" + str(DateOut) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].TimeOut[0])/V(" + str(TimeOut) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].GPSDatumOut[0])/V(" + str(GPSDatumOut) + ")>>\n")
        txt.write("]\n")
        txt.write("endobj\n")
        txt.write("trailer\n")
        txt.write("<</Root 1 0 R>>\n")
        txt.write("%%EO\n")
        txt.close ()

    ##Automate map production - July 27, 2012
        try:
            for clearLyr in clearLyrs:
                lyr = arcpy.mapping.ListLayers(mxd, clearLyr,df)[0]
                arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")

            fc_lyr = "none"
            fc = "none"
            PrintMap = row.getValue("Create_Map")
            if PrintMap == 'Yes':
                where4 = '"Area_Name" = ' + "'" + TaskMap + "'"
                arcpy.AddMessage(TaskMap)
                if arcpy.Exists(fc4):
                    rows4 = arcpy.UpdateCursor(fc4, where4)
                    for row4 in rows4:
                        if fc != "none":
                            arcpy.AddWarning("Another feature has the same name")
                        else:
                            fc = fc4
                            fc_lyr = fcS_lyr
                            row4.Status = "Planned"
                            pSearch = row4.getValue("Searched")
                            row4.Searched = pSearch + 1
                            rows4.updateRow(row4)
                            arcpy.SelectLayerByAttribute_management (fc, "NEW_SELECTION", where4)

                if arcpy.Exists(fc5):
                    rows4 = arcpy.SearchCursor(fc5, where4)
                    for row4 in rows4:
                        arcpy.SelectLayerByAttribute_management (fc5, "NEW_SELECTION", where4)
                        if fc != "none":
                            arcpy.AddWarning("Another feature has the same name")
                        else:
                            fc = fc5
                            fc_lyr = fcP_lyr

                if arcpy.Exists(fc6):
                    rows4 = arcpy.SearchCursor(fc6, where4)
                    for row4 in rows4:
                        arcpy.SelectLayerByAttribute_management (fc6, "NEW_SELECTION", where4)
                        if fc != "none":
                            arcpy.AddWarning("Another feature has the same name")
                        else:
                            fc = fc6
                            fc_lyr = fcL_lyr

                if arcpy.Exists(fc7):
                    rows4 = arcpy.SearchCursor(fc7, where4)
                    for row4 in rows4:
                        arcpy.SelectLayerByAttribute_management (fc7, "NEW_SELECTION", where4)
                        if fc != "none":
                            arcpy.AddWarning("Another feature has the same name")
                        else:
                            fc = fc7
                            fc_lyr = fcS_lyr

                if fc == "none":
                    arcpy.AddWarning("No features had this area name and No map created.")
                else:
                    arcpy.DeleteRows_management(fc_lyr)
                    shapeName = arcpy.Describe(fc).shapeFieldName
                    feat = row4.getValue(shapeName)
                    rows5 = arcpy.InsertCursor(fc_lyr)
                    row5 = rows5.newRow()
                    row5.SHAPE = feat
                    rows5.insertRow(row5)
                    del rows5
                    del row5

                    df.zoomToSelectedFeatures()
                    mapScale = row.getValue("Map_Scale")
                    if mapScale > 0:
                        df.scale = row.getValue("Map_Scale")
                    else:
                        df.scale = 24000

                    arcpy.AddMessage(df.scale)
                    arcpy.RefreshActiveView()

                    MapName=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MapName")[0]
                    MapName.text = "  " + TaskMap
                    PlanNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "PlanNum")[0]
                    PlanNum.text = "  " + PlanNo
                    TaskNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "AssignNum")[0]
                    TaskNum.text = "  " + AssNum

                    arcpy.RefreshActiveView()
                    outFile = output + "\\" + str(TaskNo) + "_map.pdf"
                    arcpy.mapping.ExportToPDF(mxd, outFile)
                    arcpy.DeleteRows_management(fc_lyr)
                    arcpy.RefreshActiveView()
                    del rows4
                    del row4

            else:
                arcpy.AddMessage('No map created')
        except:
            arcpy.AddWarning("Unable to produce map for Assignment: " + str(AssNum))
            for clearLyr in clearLyrs:
                lyr = arcpy.mapping.ListLayers(mxd, clearLyr,df)[0]
                arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")

        row = rows.next()


del rows
del row

#######

del mxd
del df
