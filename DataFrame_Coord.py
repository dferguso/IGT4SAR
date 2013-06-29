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

import arcpy, os
from arcpy import env

fclist=[]

fold = arcpy.GetParameterAsText(0)  # Set folder
folder = fold.replace('\\','/')
envr = folder + '/SAR_default.gdb'
arcpy.env.workspace = envr

#for fc in fcs:
fc="Base_Data"
sr = arcpy.Describe(fc).spatialReference
arcpy.AddMessage(sr.name)

mxd_nA = folder + '/IGT4SAR_101.mxd'

mxd_nB = "%r"%mxd_nA
mxd_name = mxd_nB[2:-1]

##
mxd = arcpy.mapping.MapDocument(mxd_name)
df = arcpy.mapping.ListDataFrames(mxd)[0]

df.spatialReference = sr
##
mxd.save()
del mxd