#-------------------------------------------------------------------------------
# Name:        Assignments.py
# Purpose:     Create Task Assignment Forms from selected rows in the
#              Assignments data layer.  New TAFs are stored by Task ID in the
#              Assignments folder
#
# Author:      Don Ferguson
#
# Created:     08/03/2012
# Copyright:   (c) ferguson 2012
#-------------------------------------------------------------------------------
#!/usr/bin/env python

# Take courage my friend help is on the way
import arcpy
from arcpy import env
import arcpy.da as da

# Set overwrite option
arcpy.env.overwriteOutput = True

mxd=arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]

fc = "Search Segments"
output="C:\MapSAR_Ex\Searches\New_Incident_17N\Assignments"
TaskNo = "T01-02"
AssNum = TaskNo

try:
    where4 = '"Area_Name" = ' + "'AA01'"

    desc = arcpy.Describe(fc)
    shapeName = desc.shapeFieldName
    rows6 = arcpy.da.SearchCursor(fc, ['SHAPE@'],where4, \
        r'GEOGCS["GCS_WGS_1984",' + \
        'DATUM["D_WGS_1984",' + \
        'SPHEROID["WGS_1984",6378137,298.257223563]],' + \
        'PRIMEM["Greenwich",0],' + \
        'UNIT["Degree",0.017453292519943295]]')

    filegpx = output + "/" + str(TaskNo) + ".gpx"
    txt= open (filegpx, "w")
    txt.write('<?xml version="1.0"?>\n')
    txt.write('<gpx version="1.1">\n')

    shpType = desc.featureClass.shapeType
    if shpType == "Point":
        for row6 in rows6:
            feat = row6.getValue(shapeName)
            pnt = feat.getPart()
            txt.write(' <wpt lat="' + str(pnt.Y) + '" lon= "'+ str(pnt.X) + '" >\n')
            txt.write('  <name>' +str(k) + '</name>\n')
            txt.write('  <type>WAYPOINT</type>\n')
            txt.write(' </wpt>\n')

    else:
        txt.write('<trk>\n')
        txt.write('   <name>' + str(AssNum) + '</name>\n')
        txt.write('<trkseg>\n')
        for row6 in rows6:
            for part in row6[0].getPart():
                k=1
                for pnt in part:
                    txt.write('<trkpt lat="' + str(pnt.Y) + '" lon= "'+ str(pnt.X) + '" >\n')
                    txt.write(' <name>' +str(k) + '</name></trkpt>\n')
                    k+=1
                txt.write('  </trkseg>\n')
            txt.write(' </trk>\n')

    txt.write('</gpx>')

    del rows6
    del row6

except:
    arcpy.AddWarning("Unable to produce gpx for Assignment: " + where4)