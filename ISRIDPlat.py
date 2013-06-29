#-------------------------------------------------------------------------------
# Name:        ISRIDPlat.py
# Purpose:   This tool is intended to be used to populate the ISRID platinum
#  data collection form.
#
# Author:      Don Ferguson
#
# Created:     01/25/2012
# Copyright:   (c) Don Ferguson 2012
# License:
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
#------------------------------------------------------------------------------
#!/usr/bin/env python

# Take courage my friend help is on the way
import arcpy

#workspc = arcpy.GetParameterAsText(0)
output = arcpy.GetParameterAsText(0)

#arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"

fc1="Incident_Info"
rows = arcpy.SearchCursor(fc1)
row = rows.next()

while row:
    # you need to insert correct field names in your getvalue function
    Incident_Name = row.getValue("Incident_Name")
    Incident_Type = row.getValue("Incident_Type")
    Environment = row.getValue("Environment")
    Eco_Region = row.getValue("Eco_Region")
    Pop_Den = row.getValue("Pop_Den")
    Terrain = row.getValue("Terrain")
    LandCover = row.getValue("LandCover")
    LandOwner = row.getValue("LandOwner")
    MapDatum = row.getValue("MapDatum")
    MapCoord = row.getValue("MapCoord")
    MagDec = row.getValue("MagDec")
    row = rows.next()
del rows
del row

fc2="Operation_Period"
rows = arcpy.SearchCursor(fc2)
row = rows.next()

while row:
    # you need to insert correct field names in your getvalue function
    Start_Date = row.getValue("Start_Date")
    End_Date = row.getValue("End_Date")
    Weather = row.getValue("Weather")
    Temp_max = row.getValue("Temp_max")
    Temp_min = row.getValue("Temp_min")
    Wind = row.getValue("Wind")
    Rain = row.getValue("Rain")
    Snow = row.getValue("Snow")
    Light = row.getValue("Light")
    row = rows.next()
del rows
del row

fc3="Lead_Agency"
rows = arcpy.SearchCursor(fc3)
row = rows.next()

while row:
    # you need to insert correct field names in your getvalue function
    LeadAgency = row.getValue("Lead_Agency")
    row = rows.next()
del rows
del row


fc4 = "Subject_Information"
fc5 = "Plan_Point"
fc6 = "RP"
fc7 = "Found"

rows1 = arcpy.UpdateCursor(fc4)
row1 = rows1.next()

while row1:
    # you need to insert correct field names in your getvalue function
    AssignNumber = row1.Assignment_Number
    PODunrep = row1.POD_Unresponsive
    PODrep = row1.POD_Response
    where2 = '"Assignment_Number" = ' + "'" + AssignNumber + "'"
    rows2 = arcpy.SearchCursor(fc2, where2)
    row2 = rows2.next()

    while row2:
        # you need to insert correct field names in your getvalue function
        AreaName = row2.Area_Name
        where3 = '"Area_Name" = ' + "'" + AreaName + "'"
        rows3 = arcpy.UpdateCursor(fc3, where3)
        row3 = rows3.next()

        while row3:
            row3.POScum = row3.POAcum * PODrep/100.0
            row3.POScumUn = row3.POAcum * PODunrep/100.0
            rows3.updateRow(row3)
            row3.POAcum = row3.POAcum - row3.POScumUn
            row3.Probability_Density = row3.POAcum / row3.Area*100.0
            row3.Searched = row3.Searched + 1
            row3.Status = "Complete"
            arcpy.AddMessage("Assignment_Number = " + AssignNumber)
            rows3.updateRow(row3)
            row3 = rows3.next()

        del where3
        del row3
        del rows3

        row2 = rows2.next()

    del AreaName
    del where2
    del row2
    del rows2

    row1.Recorded = "1"
    rows1.updateRow(row1)
    row1 = rows1.next()

del AssignNumber
del rows1
del row1
del where1
del fc1
del fc2


fc2="Assignments"
rows = arcpy.SearchCursor(fc2)
row = rows.next()
while row:
    # you need to insert correct field names in your getvalue function
    TaskInstruct = row.getValue("Description")
    PlanNo = row.getValue("Planning_Number")
    Priority = row.getValue("Priority")
    TaskNo = row.getValue("Assignment_Number")
    TeamID = row.getValue("Team")
    TaskMap = row.getValue("Area_Name")
    Notes = row.getValue("Safety_note")
    PrepBy = row.getValue("Prepared_By")

    arcpy.AddMessage("Task Assignment Number " + TaskNo)

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
    ## txt.write("<</T(topmostSubform[0].Page1[0].ResourceType[0])/V(" + str(ResourceType) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Priority[0])/V(" + str(Priority) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].TaskNo[0])/V(" + str(TaskNo) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].TeamId[0])/V(" + str(TeamID) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].TaskMap[0])/V(" + str(TaskMap) + ")>>\n")
    ## txt.write("<</T(topmostSubform[0].Page1[0].PreSearch[0])/V(" + str(PreSearch) + ")>>\n")
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
#arcpy.DeleteFeatures_management(fc3)



txt.write("<</T(form1[0].#subform[0].Incidentstatus[0].IncStat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Incidentstatus[0].IncStat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Incidentstatus[0].IncStat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Incidentstatus[0].IncStat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Lead[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].IncNum[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].MisNum[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Incdate[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].IncTyp[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Prepared[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Org[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Email[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Phone[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].IncEnv[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].CtyReg[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].State[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].InciTimeRp[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].PrimaryResponseArea[0].PrimeArea[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].PrimaryResponseArea[0].PrimeArea[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].SubCat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].SubCatSub[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].SubAct[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].IPPType[0].IPPType[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].IPPType[0].IPPType[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].IPPClass[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].IPPLat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].IPPLong[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].IPPFmt[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].EcoDom[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].EcoDiv[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Pop[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Ter[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Cover[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Owner[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Wx[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Tmax[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Tmin[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Wind[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Rain[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].SnowGrd[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Snow[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Light[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].TLSdate[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].TSN[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].SF[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].IClosed[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].TTL[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].TST[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].TLSTime[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].SARNotTime[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].SubFoundTime[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].ClosedTime[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Age1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Sex1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Local1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Wgt1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Hgt1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Bld1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Fit1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Exp1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Eq1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Cl1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Sur1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Mnt1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Age2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Sex2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Sex3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Sex4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Age3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Age4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Local2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Local3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Local4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Subform1[0].SubGrp[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Subform1[0].SubGrp[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Subform1[0].SubGrp[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].GrpTyp[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Wgt2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Wgt3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Wgt4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Hgt2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Hgt3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Hgt4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Bld2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Bld3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Bld4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Fit2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Fit3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Fit4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Exp2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Exp3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Exp4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Eq2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Eq3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Eq4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Cl2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Cl3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Cl4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Sur2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Sur3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Sur4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Mnt2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Mnt3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].Mnt4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[0].CntMtd[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DesLong[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DesLat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DesFmt[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].RPLSFmt[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].RPLSLat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].RPLSLong[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DECLat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DECLong[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DECFmt[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DOT[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DOThow[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].RevPLS[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DECTyp[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].RevDOT[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Dec[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].PaperFormsBarcode1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Comment[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Outcm[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Scen[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Susp[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].SubjNum[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Well[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Inj[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DOA[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Saves[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].FFmt[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].FLong[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].FLat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DisIPP[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Ffeat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Ffeat2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Det[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].MobRes[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Strat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Mob[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].TrkOff[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform2[0].Elv[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform2[0].Elv[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].ElvFt[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].BFnd[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Status1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Mech1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Inj1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Ill1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Tx1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Status2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Status3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Status4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Mech2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Mech3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Mech4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Inj2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Inj3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Inj4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Ill2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Ill3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Ill4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Tx2[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Tx3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Tx4[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].SrchInj[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].SrchInjDet[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Tasks[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].VehNum[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Peop[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].MilesDrv[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Cost[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Manhrs[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DogNum[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].AirNum[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].AirTsk[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].AirHrs[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].FndRes[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].EVol[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].Sig[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].Aeromedical[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].Helicopter[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].Swiftwater[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].Boat[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].Vehicle[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].Technical[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].SemiTech[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].Carryout[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].Walkout[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].Other[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform3[0].OtherRescue[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].Swiftwater[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].Other[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].USARCert[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].FixedWing[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].Helo[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].Other[1])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].Parks[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].Cave[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].Boats[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].Divers[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].Law[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].Tracker[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].CheckBox3[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].EMS[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].Dogs[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].TextField1[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Subform4[0].GSAR[0])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Peop[1])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Manhrs[1])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].VehNum[1])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].MilesDrv[1])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Cost[1])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].AirHrs[1])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].AirNum[1])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].AirTsk[1])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].DogNum[1])/V(" + str(Incident_Name) + ")>>\n")
txt.write("<</T(form1[0].#subform[6].Tasks[1])/V(" + str(Incident_Name) + ")>>\n")
