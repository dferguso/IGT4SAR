#-------------------------------------------------------------------------------
# Name:        UpdateLayout.py
# Purpose:
#
# Author:      Don Ferguson
#
# Created:     18/06/2012
# Copyright:   (c) ferguson 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

# Take courage my friend help is on the way
import arcpy

mxd=arcpy.mapping.MapDocument("CURRENT")

# Get UTM and USNG Zones
# Get declination from Incident Information
arcpy.AddMessage("Checking for Planning Point\n")
try:
    cPlanPt =arcpy.GetCount_management("Plan_Point")
    if int(cPlanPt.getOutput(0)) > 0:
        try:
            cIncident=arcpy.GetCount_management("Incident_Information")
            arcpy.AddMessage("Checking Incident Information")
            if int(cIncident.getOutput(0)) > 0:
                mapLyr = arcpy.mapping.ListLayers(mxd, "Incident_Information")[0]
                MagDeclin=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MagDecl")[0]
                rows=arcpy.SearchCursor(mapLyr)
                row = rows.next()
                MD=row.getValue("MagDec")
                if not MD:
                    arcpy.AddWarning("No Magnetic Declination provided in Incident Information")
                else:
                    MagDeclin.text = row.getValue("MagDec")
                    arcpy.AddMessage("Magnetic Declination is " + MagDeclin.text + "\n")
                del rows
                del row
                del MagDeclin
            else:
                arcpy.AddWarning("No Incident Information provided\n")
        except:
            arcpy.AddMessage("Error: Update Magnetic Declination Manually\n")
        try:
            arcpy.AddMessage("Updating UTM and USNG grid info")
            mapLyr=arcpy.mapping.ListLayers(mxd, "MGRSZones_NA")[0]
            arcpy.SelectLayerByLocation_management("14 Base_Data_Group\Grids\MGRSZones_NA","INTERSECT","1 Incident_Group\Planning Point")
            UTMZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "UTMZone")[0]
            USNGZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "USNGZone")[0]
            rows=arcpy.SearchCursor(mapLyr)
            row = rows.next()
            UTMZn.text = row.getValue("GRID1MIL")
            USNGZn.text = row.getValue("GRID100K")
            arcpy.AddMessage("UTM Zone is " + UTMZn.text + "and USNG Grid is " + USNGZn.text + "\n")
            del rows
            del row
            del mapLyr
            del UTMZn
            del USNGZn
            arcpy.AddMessage("Refresh display when complete, View > Refresh or F5\n")
        except:
            arcpy.AddMessage("Error: Update USNG Grid and UTM Zone text fields on map layout manually\n")
    else:
        arcpy.AddWarning("Warning: Need to add Planning Point prior to updating map layout\n")

except:
    arcpy.AddWarning("There was an error")
del mxd