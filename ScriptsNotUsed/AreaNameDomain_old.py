#-------------------------------------------------------------------------------
# Name:        AreaNameDomain.py
# Purpose:     Add in the search area (Hasty_Points, Hasty_Lines, Search
#              Segments) names to the geodatabase domain Area_Names
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

workspc = arcpy.GetParameterAsText(0)

arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"

fc1 = "Area_Names"
fc2 = "Hasty_Points"
fc3 = "Hasty_Line"
fc4 = "Hasty_Segments"
fc5 = "Search_Segments"

myList =[]

#arcpy.AddMessage("Area Name ")
try:
    pFeat = fc2
    cFeat=arcpy.GetCount_management(pFeat)
    if int(cFeat.getOutput(0)) > 0:
        arcpy.AddMessage("Add area names from " + pFeat)
        rows1 = arcpy.SearchCursor(pFeat)
        row1 = rows1.next()
        while row1:
            AName = row1.getValue("Area_Name")
            myList.append(AName)
            #arcpy.AddMessage(AName)

            row1 = rows1.next()
        del row1
        del rows1
    else:
        arcpy.AddMessage("No features in " + pFeat)
    del cFeat, pFeat

    pFeat = fc3
    cFeat=arcpy.GetCount_management(pFeat)
    if int(cFeat.getOutput(0)) > 0:
        arcpy.AddMessage("Add area names from " + pFeat)
        rows1 = arcpy.SearchCursor(pFeat)
        row1 = rows1.next()
        while row1:
            AName = row1.getValue("Area_Name")
            myList.append(AName)
            #arcpy.AddMessage(AName)

            row1 = rows1.next()
        del row1
        del rows1
    else:
        arcpy.AddMessage("No features in " + pFeat)
    del cFeat, pFeat

    pFeat = fc4
    cFeat=arcpy.GetCount_management(pFeat)
    if int(cFeat.getOutput(0)) > 0:
        arcpy.AddMessage("Add area names from " + pFeat)
        rows1 = arcpy.SearchCursor(pFeat)
        row1 = rows1.next()
        while row1:
            AName = row1.getValue("Area_Name")
            myList.append(AName)
            #arcpy.AddMessage(AName)

            row1 = rows1.next()
        del row1
        del rows1
    else:
        arcpy.AddMessage("No features in " + pFeat)
    del cFeat, pFeat

    pFeat = fc5
    cFeat=arcpy.GetCount_management(pFeat)
    if int(cFeat.getOutput(0)) > 0:
        arcpy.AddMessage("Add area names from " + pFeat)
        rows1 = arcpy.SearchCursor(pFeat)
        row1 = rows1.next()
        while row1:
            AName = row1.getValue("Area_Name")
            myList.append(AName)
            #arcpy.AddMessage(AName)

            row1 = rows1.next()
        del row1
        del rows1
    else:
        arcpy.AddMessage("No features in " + pFeat)
    del cFeat, pFeat

    # Remove duplicates by turning the list into a set and
    # then turning the set back into a list
    myList = list(set(myList))

    arcpy.DeleteRows_management(fc1)

    for xd in myList:
        arcpy.AddMessage(xd)

        rows = arcpy.InsertCursor(fc1)

        row = rows.newRow()
        row.Area_Name = xd
        rows.insertRow(row)

        del rows
        del row

    domTable = fc1
    codeField = "Area_Name"
    descField = "Area_Name"
    dWorkspace = workspc
    domName = "Area_Names"
    domDesc = "Search area names"


    # Process: Create a domain from an existing table
    arcpy.TableToDomain_management(domTable, codeField, descField, dWorkspace, domName, domDesc,"REPLACE")


    del fc1
    del fc3
    del fc2


except:
    # Get the tool error messages
    #
    msgs = "All tasks have been processed"

    # Return tool error messages for use with a script tool
    #
    arcpy.AddWarning(msgs)
    # Print tool error messages for use in Python/PythonWin
    #
    print msgs
