#-------------------------------------------------------------------------------
# Name:        MissingPersomForm.py
#
# Purpose:     Create Missing Person Flyer from data stored in the Subject
#              Information data layer within MapSAR
#
# Author:      Don Ferguson
#
# Created:     12/12/2011
# Copyright:   (c) Don Ferguson 2011
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
#!/usr/bin/env python

import arcpy
from datetime import datetime

#workspc = arcpy.GetParameterAsText(0)
output = arcpy.GetParameterAsText(0)

#arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"

fc3="Incident_Information"
fc2="Lead Agency"

rows = arcpy.SearchCursor(fc3)
row = rows.next()
arcpy.AddMessage("Get Incident Info")

while row:
    # you need to insert correct field names in your getvalue function
    LeadAgency = row.getValue("Lead_Agency")
    where2 = '"Lead_Agency" = ' + "'" + LeadAgency + "'"
    arcpy.AddMessage(where2)
    rows2 = arcpy.SearchCursor(fc2, where2)
    row2 = rows2.next()

    Phone = 'none'
    email = 'none'

    while row2:
        # you need to insert correct field names in your getvalue function
        Phone = row2.getValue("Lead_Phone")
        if Phone == 'none':
            Phone = " "
            arcpy.AddWarning("No Phone number provided for Lead Agency")
        email = row2.getValue("E_Mail")
        if email == 'none':
            email = " "
            arcpy.AddWarning("No e-mail address provided for Lead Agency")
        row2 = rows2.next()
    del rows2
    del row2

    row = rows.next()
del rows
del row


Callback = "If you have information please call: " + str(LeadAgency) + " at phone: " + str(Phone) + " or e-mail:" + str(email)

fc1="Subject_Information"
rows = arcpy.SearchCursor(fc1)
row = rows.next()
while row:
    # you need to insert correct field names in your getvalue function
    try:
        Subject_Name = row.getValue("Name")
        if len(Subject_Name) == 0:
            arcpy.AddWarning('Need to provide a Subject Name')
    except:
        Subject_Name = " "
        arcpy.AddWarning('Need to provide a Subject Name')
    try:
        fDate = row.getValue("Date_Seen")
        Date_Seen = fDate.strftime("%m/%d/%Y")
    except:
        Date_Seen = " "

    try:
        fTime = row.getValue("Time_Seen")
    except:
        fTime = " "
    Where_Last = row.getValue("WhereLastSeen")
    Age = row.getValue("Age")
    Gender = row.getValue("Gender")
    Race = row.getValue("Race")
    try:
        Height1 = (row.getValue("Height"))/12.0
        feet = int(Height1)
        inches = int((Height1 - feet)*12.0)
        fInches = "%1.0f" %inches
        Height = str(feet) + " ft " + fInches +" in"
    except:
        Height = "NA"
    Weight = row.getValue("Weight")
    Build = row.getValue("Build")
    Complex = row.getValue("Complexion")
    Hair = row.getValue("Hair")
    Eyes = row.getValue("Eyes")
    Other = row.getValue("Other")
    Shirt = row.getValue("Shirt")
    Pants = row.getValue("Pants")
    Jacket = row.getValue("Jacket")
    Hat = row.getValue("Hat")
    Footwear = row.getValue("Footwear")
    Info = row.getValue("Info")
    try:
        QRCode = row.getValue("QRCode")
    except:
        QRCode = " "

    filename = output + "/" + str(Subject_Name) + ".fdf"

    txt= open (filename, "w")
    txt.write("%FDF-1.2\n")
    txt.write("%????\n")
    txt.write("1 0 obj<</FDF<</F(MissingPersonForm.pdf)/Fields 2 0 R>>>>\n")
    txt.write("endobj\n")
    txt.write("2 0 obj[\n")

    txt.write ("\n")

    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Name[0])/V(" + str(Subject_Name) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPFAge[0])/V(" + str(Age) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPFSex[0])/V(" + str(Gender) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Location[0])/V(" + str(Where_Last) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_TimeMissing[0])/V(" + fTime + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_DateMissing[0])/V(" + str(Date_Seen) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Race[0])/V(" + str(Race) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Height[0])/V(" + Height + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Weight[0])/V(" + str(Weight) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Build[0])/V(" + str(Build) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Complex[0])/V(" + str(Complex) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_HairColor[0])/V(" + str(Hair) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_EyeColor[0])/V(" + str(Eyes) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_OtherPhy[0])/V(" + str(Other) + ")>>\n")
    #txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_OtherPhy[1])/V(" + str(Incident_Name) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_ShirtClothing[0])/V(" + str(Shirt) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_PantsClothing[0])/V(" + str(Pants) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_JacketClothing[0])/V(" + str(Jacket) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_HatClothing[0])/V(" + str(Hat) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_FootClothing[0])/V(" + str(Footwear) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_OtherInfo[0])/V(" + str(Info) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_CallNumber[0])/V(" + str(Callback) + ")>>\n")
    #txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].ImageField1[0])/V(" + str(Incident_Name) + ")>>\n")

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