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
fc2 = "Hasty_Line"
fc3 = "Search_Segments"
fc4 = "Hasty_Points"
fc5 = "Probability_Regions"

myList =[]

arcpy.CalculateField_management(fc3, "Area_seg", "!shape.area@acres!", "PYTHON_9.3", "")

#arcpy.AddMessage("Area Name ")
try:
    rows1 = arcpy.SearchCursor(fc2)
    row1 = rows1.next()

    while row1:
        AName = row1.getValue("Area_Name")
        myList.append(AName)


        row1 = rows1.next()
    del row1
    del rows1

    rows1 = arcpy.UpdateCursor(fc3)
    row1 = rows1.next()

    while row1:
        AName = row1.getValue("Area_Name")
        myList.append(AName)
        RegionName = row1.Region_Name

        SegArea=row1.Area_seg

        where2 = '"Region_Name" = ' + "'" + RegionName + "'"
        rows2 = arcpy.SearchCursor(fc5, where2)
        row2 = rows2.next()

        while row2:
            RegArea = row2.Area
            RegPOA0 = row2.POA
            row2 = rows2.next()

        row1.sPOC_Orig = RegPOA0*SegArea/RegArea
        rows1.updateRow(row1)

        del where2
        del row2
        del rows2
        #arcpy.AddMessage(AName)

        row1 = rows1.next()

    del row1
    del rows1

    rows1 = arcpy.SearchCursor(fc4)
    row1 = rows1.next()

    while row1:
        AName = row1.getValue("Area_Name")
        myList.append(AName)
        #arcpy.AddMessage(AName)

        row1 = rows1.next()
    del row1
    del rows1

    # Remove duplicates by turning the list into a set and
    # then turning the set back into a list
    myList = list(set(myList))

    arcpy.DeleteRows_management(fc1)

    for xd in myList:
    ##        arcpy.AddMessage(xd)

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
    domDesc = "Area_Names"
    arcpy.AddMessage("Area Name = " + AName)

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
