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
arcpy.env.overwriteOutput = "True"

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

rows = arcpy.SearchCursor(fc2)
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
#    Notes = row.getValue("Safety_note")
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


    row = rows.next()
del rows
del row

