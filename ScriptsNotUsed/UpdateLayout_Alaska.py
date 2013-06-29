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
mapLyr=arcpy.mapping.ListLayers(mxd, "MGRSZones_USContiguous_Layer")[0]
arcpy.SelectLayerByLocation_management("14 Base_Data_Group\Grids\MGRSZones_USContiguous_Layer","INTERSECT","1 Incident_Group\Planning Point")
UTMZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "UTMZone")[0]
USNGZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "USNGZone")[0]
rows=arcpy.SearchCursor(mapLyr)
row = rows.next()
UTMZn.text = row.getValue("GRID1MIL")
USNGZn.text = row.getValue("GRID100K")
arcpy.AddMessage(UTMZn.text)
del rows
del row
del mapLyr
del UTMZn
del USNGZn

# Get declination from Incident Information
mapLyr = arcpy.mapping.ListLayers(mxd, "Incident_Information")[0]
MagDeclin=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MagDecl")[0]
rows=arcpy.SearchCursor(mapLyr)
row = rows.next()
MagDeclin.text = row.getValue("MagDec")
arcpy.AddMessage("Refresh display when complete, View > Refresh or F5")
del rows
del row
del mapLyr
del MagDeclin
del mxd