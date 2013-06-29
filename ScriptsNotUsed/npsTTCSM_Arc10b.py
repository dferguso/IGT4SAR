###########################################
# Master Script for the Travel Time Cost Surface Model (TTCSM)
# The TTCSM models travel time based on user defined Cost Surfaces, Speed Surface
# and least cost path modeling techniques.  See the TTCSM Standard Operating Procedure document
# for details about running the TTCSM.
# Script has been migrated to be compatiable with Arc10.
#
# Draft version Date: 20111027
# Script Written By:  Kirk Sherrill NPS-NRPC-I&M GIS Program
#
#
# Suggested Citation:
#   Sherrill, K.R., B. Frakes, and S. Schupbach. 2010. Travel time cost surface model: standard operating procedure.
#   Natural Resource Report NPS/NRPC/IMD/NRR 2010/238. National Park Service, Fort Collins, Colorado.
#
##########################################


# Import system modules
import sys, string, os, arcgisscripting, math, arcpy

# Create the Geoprocessor objects
gp = arcgisscripting.create()

# Check out any necessary ArcGIS licenses
arcpy.CheckOutExtension("spatial")

# Load required toolboxes...
#gp.AddToolbox("C:/Program Files/ArcGIS/Desktop10.0/ArcToolbox/Toolboxes/Spatial Analyst Tools.tbx")
#gp.AddToolbox("C:/Program Files/ArcGIS/Desktop10.0/ArcToolbox/Toolboxes/Conversion Tools.tbx")



###################################################
# Start of Parameters requiring set up.
###################################################

## Required Data Layers
##startLocation= "D:\\KIMO\\data\\KIMO_TTCSM.gdb\\Boundary_Road_Instersect"        ## Start location(s) point data for cost or path distance calculation
startLocation= "N:\GISData\Searches\TableTopExercises\DollySods\SAR_Default.gdb\\Plan_Point"
#roadsData = "D:\\KIMO\\data\\KIMO_TTCSM.gdb\\KIMO_Roads_AOA"                              ## Road Network
roadsData = "N:\GISData\Searches\TableTopExercises\DollySods\SAR_Default.gdb\\Roads"                             ## Road Network
trailsData = "na"                            ## Trail Network
#DEM = "D:\\KIMO\\data\\KIMO_TTCSM.gdb\\dem_KIMO_AOA_30m"                                          ## Digital Elevation Model
DEM = "N:\GISData\Searches\TableTopExercises\DollySods\Base_Data\DEM\\dollysods_dem"                                          ## Digital Elevation Model
destinations = "na"           ## Destinations feature class
#costSurfaceTable = "D:\\KIMO\\CstSurfTable.txt"           ## costSurface Cost Surface Table location
#workspace = "D:\\KIMO\\workspace\\"                                      ## Setting workspace variable
workspace = arcpy.env.workspace
logFileName = workspace + "AA_TTCSM_KIMO.txt"                                       ## Log File for the costSurfaceModelMS.py

## General Model Parameters
walkingSpeed = "2.5"                                                                   ## Average walking speed for the scenario when walking a smooth flat surface (Miles/Hr)
maxSlope = "40"                                                                        ## Value in degrees defined as being to steep for travel
timeCap = "28800"                                                                      ## Maximum cost distance travel time calculated in seconds (28800/3600 = 8 hours).
trails = "no"                                                                         ## Variable defining if a trail network is being used.  If a trail network is not available set to "no", so speed surface calculation doesn't attempt to use a trail network.
memory = "no"                                                                         ## ("Yes"|"No") Switch defining if memory preservation processing is to be performed.

##Travel Time Modeling Parameters
usePathDistance = "no"                                                                ## Switch to use path distance or cost distance travel time calculation ("yes" |"no"). no = normal cost distance travel time calculation yes = path distance travel time calculation.
vertValueZero = "1"                                                                    ## Value of the vertical factor graph at a slope value of zero.  This usually will be 1, but can be changed as desired.
verticalGraphType = "Inverse_Linear"                                                   ## Select one of the following vertical factor graph (weights)to be used in path distance modeling: ("Binary" | "Linear" | "Sym_linear" | "Inverse_Linear" | "Sym_Inverse_Linear" | "Cos" | "Sec" | "Cos_Sec" | "Sec_Cos" | "Table").  See documentation for further definition.
verticalGraph = "na"                                                                   ## Path to the user specified vertical factor graph if "Table" is selected for the VerticalGraphyType ("na" | "path to user defined VFG").
leastCostPath = "no"                                                                   ## Switch defining if travel time least cost paths are to be derived ("yes"| "no")
timeCalculation = "oneway"                                                             ## Switch defining if one way or round trip time calculations are desired. ("oneway" | "roundtrip")

###################################################
# End of Parameters requiring set up.
###################################################

############################################
## Below are paths which are hard coded

# Setting the Geoprocessing workspace
gp.Workspace = workspace

usePDLC = usePathDistance.lower()
if usePDLC == "yes":
    suffix = verticalGraphType  #determining which suffix to use for output files flagging for either cost or path distance with the respective vfg type used.
else:
    suffix = "Cost_Distance"    #determining which suffix to use for output files flagging for either cost or path distance with the respective vfg type used.

extentDEM = workspace + "extentDEM"
belowSlope = workspace + "belowSlope"
slope = workspace + "slope"
roadSpeed = workspace + "roadSpeed"
costSurface = workspace + "output\\costSurface.img"                  #Cost Surface Grid
speedSurface = workspace + "output\\speedSurface.img"                #has Road and Trail Speed as well as Speed everywhere else in Seconds per Meter with out impedence included.
travelCost = workspace + "output\\travelCost.img"                     #Final travel cost surface grid to be input into the cost/path distance models. It is costSuface * speedSurface
travelTimeOut = workspace + "travelTimeOut_" + suffix + ".img"         #calculated one way (travel out) travel time - output from the cost distance model (using either Cost Distance or Path Distance).
costPathsOut = workspace + "output\\costPathsOut_" + suffix + ".shp"            #merged Out travel cost paths shapefile
indexFileName = workspace + "AA_TTCSM_Index.txt"                                       # Index File used for memory - windows scheduler processing if Memory = yes


##################################
# Checking for working directories
##################################

if os.path.exists(workspace + "output"):
    pass
else:
    os.makedirs(workspace + "output")
if os.path.exists(workspace + "paths"):
    pass
else:
    os.makedirs(workspace + "paths")
if os.path.exists(workspace + "back"):
    pass
else:
    os.makedirs(workspace + "back")

########################
##Loading TTCSM modules
#######################
import npsTTCSMModule_Arc10
reload (npsTTCSMModule_Arc10)
from npsTTCSMModule_Arc10 import *

scriptMsg = ""


###################################################################################################
#Setting up index file to shut down Script after completion of each function and after path or cost surface calculation
#when the memory preservation swith is set to yes.
###################################################################################################
if os.path.exists(indexFileName):
    pass
else:
    WriteIndex(indexFileName, "")

##########################################################
#Function to Test Setup Parameters for logical consistancy
##########################################################
logFile = open(logFileName, "a")
z = setupTest (startLocation, roadsData, trailsData, DEM, destinations, costSurfaceTable, workspace, leastCostPath, timeCalculation, trails)
messageTime = timeFun()
if z[0] == 0:
    scriptMsg = "TTCSM bailed on setupTest" + str(z[0]) + " << " + str(z[1]) + " " + messageTime
    logFile.write(scriptMsg)
    logFile.close()
    raise Exception, scriptMsg
statusZ = "setupTest " + " << " + str(z[0])
logFile.write(statusZ + "\n")
logFile.close()


if memory.lower() == "yes":
    #Opening memory index file for writing
    IndexFile = open(indexFileName, "a")
    Start_Index = str(GetIndex(indexFileName))  #Grabbing the Start_Index value to determine where script has previously ran
    IndexFile.close()
    if Start_Index == "0":          #Defining Start_Index as 0 when the script is starting from beginning.
        WriteIndex(indexFileName, "0")
    elif Start_Index == "f travelTimeBackMS completed":
        logFile = open(logFileName, "a")
        messageTime = timeFun()
        scriptMsg = "TTCSM script completed each of the functions - End of Processing " + messageTime
        logFile.write(scriptMsg + "\n")
        logFile.close()
        print "TTCSM script completed each of the functions - End of Processing"
        raise Exception, scriptMsg

    else:
        pass

else:       #When memory not set to yes
    pass

#################################################
##Beginning routine to run indivual TTCSM modules
#################################################
try:
    # Open log file for writing
    logFile = open(logFileName, "a")

    Start_Index = str(GetIndex(indexFileName))  #Grabbing the Start_Index value

    if (memory.lower() == "no" or (memory.lower() == "yes" and Start_Index == "0")):        #If true perform demBasedMS function

        a = demBasedMS (DEM, extentDEM, slope, maxSlope, belowSlope, workspace)        #Dem Module
        print "demBased return code = " + str(a)
        statusA = "demBasedMS " + " << " + str(a)
        logFile.write(statusA + "\n")
        if a == 0:
            scriptMsg = "ttcsm model bailed...\nProblems with demBasedMS.py "
            logFile.write(scriptMsg)
            raise Exception, scriptMsg
        elif memory.lower() == "yes":       #If memory set to yes
            WriteIndex(indexFileName, "a demBased completed")
            messageTime = timeFun()
            scriptMsg = "Exiting - To Clear Memory - a demBased completed " + messageTime
            logFile.write(scriptMsg + "\n")
            raise Exception, scriptMsg

        else:
            pass

    else:   #demBased has already been performed
        pass

    ####################################################
    # Start of custSurfaceMS function
    ####################################################
    Start_Index = str(GetIndex(indexFileName))  #Grabbing the Start_Index value
    if (memory.lower() == "no" or (memory.lower() == "yes" and Start_Index == "a demBased completed")):       #If true perform costSurfaceMS function
        b = costSurfaceMS (costSurfaceTable, belowSlope, DEM, workspace, costSurface)       #Cost Surface Module
        print "costSurfaceMS return code = " + str(b)
        statusB = "costSurfaceMS " + " << " + str(b)
        logFile.write(statusB + "\n")
        if b == 0:
            scriptMsg = "ttcsm model bailed...\nProblems with costSurfaceMS.py "
            logFile.write(scriptMsg)
            raise Exception, scriptMsg
        elif memory.lower() == "yes":       #If memory set to yes and costSurfaceMS successful
            WriteIndex(indexFileName, "b costSurfaceMS completed")
            messageTime = timeFun()
            scriptMsg = "Exiting - To Clear Memory - b costSurfaceMS completed " + messageTime
            logFile.write(scriptMsg + "\n")
            raise Exception, scriptMsg
        else:
            pass

    else:   #costSurfaceMS has already been performed
        pass



    #########################################################
    # Start of speedSurfaceMS Function
    #########################################################
    Start_Index = str(GetIndex(indexFileName))  #Grabbing the Start_Index value
    if (memory.lower() == "no" or (memory.lower() == "yes" and Start_Index == "b costSurfaceMS completed")):       #If true perform speedSurfaceMS function
        c = speedSurfaceMS (roadsData, DEM, workspace, extentDEM, slope, roadSpeed, trailsData, speedSurface, trails, walkingSpeed)   #Speed Surface Module
        print "speedSurfaceMS return code = " + str(c)
        statusC = "speedSurfaceMS " + " << " + str(c)
        logFile.write(statusC + "\n")
        if c == 0:
            scriptMsg = "ttcsm model bailed...\nProblems with speedSurfaceMS.py "
            logFile.write(scriptMsg)
            raise Exception, scriptMsg
        elif memory.lower() == "yes":       #If memory set to yes and speedSurfaceMS successful
            WriteIndex(indexFileName, "c speedSurfaceMS completed")
            messageTime = timeFun()
            scriptMsg = "Exiting - To Clear Memory - c speedSurfaceMS completed " + messageTime
            logFile.write(scriptMsg + "\n")
            raise Exception, scriptMsg
        else:
            pass

    else:   #speedSurfaceMS has already been performed
        pass


    #################################################################
    # Start of travelCostSurfaceMS function
    #################################################################


    Start_Index = str(GetIndex(indexFileName))  #Grabbing the Start_Index value
    if (memory.lower() == "no" or (memory.lower() == "yes" and Start_Index == "c speedSurfaceMS completed")):       #If true perform travelCostSurfaceMS function
        d = travelCostSurfaceMS (speedSurface, costSurface, travelCost, DEM, suffix, workspace)  #Travel Cost Surface Module
        print "travelCostSurfaceMS return code = " + str(d)
        statusD = "travelCostSurfaceMS " + " << " + str(d)
        logFile.write(statusD + "\n")
        if d == 0:
            scriptMsg = "ttcsm model bailed...\nProblems with travelCostSurfaceMS.py "
            logFile.write(scriptMsg)
            raise Exception, scriptMsg
        elif memory.lower() == "yes":       #If memory set to yes and travelCostSurfaceMS successful
            WriteIndex(indexFileName, "d travelCostSurfaceMS completed")
            messageTime = timeFun()
            scriptMsg = "Exiting - To Clear Memory - d travelCostSurfaceMS completed " + messageTime
            logFile.write(scriptMsg + "\n")
            raise Exception, scriptMsg
        else:
            pass

    else:   #travelCostSurfaceMS has already been performed
        pass


    Start_Index = str(GetIndex(indexFileName))  #Grabbing the Start_Index value
    if (memory.lower() == "no" or (memory.lower() == "yes" and Start_Index == "d travelCostSurfaceMS completed")):       #If true perform travelTimeOutMS function
        e = travelTimeOutMS (startLocation, travelCost, DEM, maxSlope, usePathDistance, verticalGraphType, vertValueZero, verticalGraph, timeCap, workspace, suffix, leastCostPath, destinations, memory, logFileName)  #Travel Time out (i.e. Oneway) module
        print "travelTimeOutMS return code = " + str(e)
        statusE = "travelTimeOutMS " + " << " + str(e)
        logFile.write(statusE + "\n")
        if e == 0:
            scriptMsg = "ttcsm model bailed...travelTimeOutMS.py not completed "
            logFile.write(scriptMsg)
            raise Exception, scriptMsg
        elif memory.lower() == "yes":       #If memory set to yes and travelTimeOutMS successful
            WriteIndex(indexFileName, "e travelTimeOutMS completed")
            messageTime = timeFun()
            scriptMsg = "Exiting - To Clear Memory - e travelTimeOutMS completed " + messageTime
            logFile.write(scriptMsg + "\n")
            raise Exception, scriptMsg
        else:
            pass

    else:   #travelTimeOutMS has already been performed
        pass

    timeCalculationLC = timeCalculation.lower()
    if timeCalculationLC == "roundtrip":
        Start_Index = str(GetIndex(indexFileName))  #Grabbing the Start_Index value
        if (memory.lower() == "no" or (memory.lower() == "yes" and Start_Index == 'e travelTimeOutMS completed')):       #If true perform travelTimeBackMS function
            f = travelTimeBackMS (startLocation, travelCost, travelTimeOut, DEM, maxSlope,usePathDistance, verticalGraphType, vertValueZero, verticalGraph, timeCap, workspace, suffix, timeCalculation, leastCostPath, destinations, costPathsOut, memory, logFileName)  #Travel Time back (i.e. Round Trip) module
            print "travelTimeBackMS return code = " + str(f)
            statusF = "travelTimeBackMS " + " << " + str(f)
            logFile.write(statusF + "\n")
            if f == 0:
                scriptMsg = "ttcsm model exited..travelTimeBackMS.py not completed "
                logFile.write(scriptMsg)
                raise Exception, scriptMsg
            elif memory.lower() == "yes":       #If memory set to yes and travelTimeBaskMS successful
                WriteIndex(indexFileName, "f travelTimeBackMS completed")
                messageTime = timeFun()
                scriptMsg = "Exiting - To Clear Memory - f travelTimeBackMS completed " + messageTime
                logFile.write(scriptMsg + "\n")
            else:
                pass
    else:
        print "Out Back Travel Time Not Selected"

except:
    print scriptMsg
    print "ttcsm model Script Exited\nSee log file " + logFileName + " for more details"

finally:
    logFile.close()
