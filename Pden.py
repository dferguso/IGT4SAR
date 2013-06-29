#-------------------------------------------------------------------------------
# Name:        Pden.py
# Purpose:  Using the Regional and Segment probabilities to determine the
#  Probability Density.
#
# Author:      Don Ferguson
#
# Created:     06/12/2011
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

# Import arcpy module
import arcpy
import string

#workspc = arcpy.GetParameterAsText(0)

#arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"

fc1 = "Planning\Probability_Regions"
fc2 = "Planning\Search_Segments"

where2 = '"Region_Name" = '

rows1 = arcpy.SearchCursor(fc1)
row1 = rows1.next()

while row1:
    # you need to insert correct field names in your getvalue function
    RegionName = row1.Region_Name
    RegArea = row1.Area
    POAcum = row1.POAcum
    where2 = '"Region_Name" = ' + "'" + RegionName + "'"
    rows2 = arcpy.UpdateCursor(fc2, where2)
    row2 = rows2.next()

    while row2:
        arcpy.AddMessage(RegionName)
        # you need to insert correct field names in your getvalue function
        Pden = POAcum/row2.Area
        row2.Probability_Density = Pden
        rows2.updateRow(row2)
        row2 = rows2.next()

    del where2
    del row2
    del rows2

    row1 = rows1.next()

del POAcum
del RegionName
del RegArea
del rows1
del row1
