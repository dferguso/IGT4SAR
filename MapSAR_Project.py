#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Don Ferguson
#
# Created:     06/12/2012
# Copyright:   (c) Don Ferguson 2012
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
# Name: BatchProject.py
# Description: Changes coordinate systems of several datasets in a batch.

import arcpy
from arcpy import env

# Script arguments
#env.workspace = arcpy.GetParameterAsText(0)  # Set workspace environment
#out_workspace = arcpy.GetParameterAsText(1)  # Output workspace
#out_cs = arcpy.GetParameterAsText(2)  # Output coordinate system
#transformation = arcpy.GetParameterAsText(3) # Geographic transformation - Optional

env.workspace = "F:\GISData\Searches\MapSAR_Start\New_Incident_22N\SAR_Default.gdb"
out_workspace = "F:\GISData\Searches\MapSAR_Start\New_Incident_23N\SAR_Default.gdb"
out_cs = '"WGS_1984_UTM_Zone_23N"'
transformation = ''

#mxd = arcpy.mapping.MapDocument("CURRENT")
#df = arcpy.mapping.ListDataFrames(mxd)[0]
sr = arcpy.SpatialReference("WGS_1984_UTM_Zone_23N")
print sr

# Input feature classes
input_features = ["Base_Data"]#, "GPS_Data", "Incidents", "Operations", "Planning", "Resources_Comms", "Clue_Photos"]

# Template dataset - Leave it empty
template = ''

#try:
arcpy.BatchProject_management(input_features, out_workspace, sr, template, transformation)
#    arcpy.AddMessage("projection of all datasets successful")

#   res = arcpy.BatchProject(input_features, out_workspace, out_cs, template, transformation)
#   if res.maxSeverity == 0:
#      print "projection of all datasets successful"
#   else:
#      print "failed to project one or more datasets"
#except:
#    arcpy.AddWarning("failed to project one or more datasets")
#   print res.getMessages()