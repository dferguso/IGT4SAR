#Draft version Date: 20111027
# npsTTCSMModule_Arc10.py
def demBasedMS(DEM,
             extentDEM,
             slope,
             maxSlope,
             belowSlope,
             workspace):

    '''
    SCRIPT NAME: demBased.py

    ABSTRACT: Script is to be used as a module in the ttcsmMasterScript.py script.  demBased.py outputs three grids based on analysis from the supplied DEM.  These grids are used in subsequent
    TTCSM analyses.  Outputs are an area of analysis grid (extentDEM), a slope grid (slope)in degrees, and a grid (belowSlope) representing all areas with slope less than the defined maxSlope
    variable.

    ARGUMENTS passed from the the ttCostSurfaceMasterScript.py:


    EXAMPLE:

    RETURNS:
    Outputs are an area of analysis grid (extentDEM), a slope grid (slope)in degrees, and a grid (belowSlope) representing all areas with slope less than the defined maxSlope
    variable.

    Scripts CREATED BY: Kirk Sherrill NPS-NRPC-I&M GIS Program, Spring 2010.
    Suggested Citation: NPS NRPC (2010). Travel Time Cost Surface Model, Version 2.0, Natural Resource Program Center, Inventory and Monitoring Program, Fort Collins, Colorado.
    '''

    try:
        # Import system modules
        import sys, string, os, arcgisscripting, math, arcpy

        # Create the Geoprocessor object
        gp = arcgisscripting.create()

        # Setting the Geoprocessing workspace
        gp.Workspace = workspace

        # Check out any necessary licenses
        arcpy.CheckOutExtension("spatial")

        # Set the Geoprocessing environment...
        gp.extent = DEM
        gp.cellSize = DEM

        # Set overwrite files to True
        gp.overwriteoutput = True

        # Process: Create Empty Grid for Resizing...
        gp.IsNull_sa(DEM, extentDEM)

        # Process: Create a Degree Slope
        gp.Slope_sa(DEM, slope, "DEGREE", "1")

        # Process: Create maximum slope surface above which no travel
        gp.LessThanEqual_sa(slope, maxSlope, belowSlope)
        return 1
    except:
        print ("demBased.py Not Working")
        return 0

def costSurfaceMS(costSurfaceTable,
                belowSlope,
                DEM,
                workspace,
                costSurface):

    '''
    SCRIPT NAME: costSurface.py

    ABSTRACT: Script is to be used as a module in the ttcsmMasterScript.py script.  costSurface.py creates a cost surface layer which is used
    in conjunction with the developed speedSurface (output from the speedCalculation.py script) to yield a travel cost layer.  The developed cost surface grid
    (costSurface) defines the weight/impedance encountered when crossing the cell.  Cell values can be from 0 - 100, where 100 equals no impedance, while
    a 0 value represents an absolute barrier.  The costSurfaceTable defines the data layers (either feature class or raster) that are used to define the cost surface.
    The costSurface table defines the field to use as a weight per each input layer.  Additionally the costSurface table defines the rank, or presidance, that each input
    layers has with respect the other inputs.  This rank or presidance can be considered the overlay order, where a rank of 1 equals the highest presidance or the final overlay.


    ARGUMENTS:


    costSurfaceTable = "S:\\ksherrill\\costsurface_test\\workspace3\\costSurfaceTable.txt"           ## Cost Surface Table location
    belowSlope = workspace + "belowSlope"
    DEM = "S:\\ksherrill\\costsurface_test\\test_data\\dem"                                         ## Digital Elevation Model location
    workspace = "S:\\ksherrill\\costsurface_test\\workspace3\\"                               ## Setting workspace variable

    EXAMPLE:


    RETURNS:
    Final output is the costSurface.grid which defines the weight or impedance of traveling through a cell.  costSurface.grid cell values can range from 0 - 100.

    '''


    try:
        # Import system modules
        import sys, string, os, arcgisscripting, math, arcpy

        # Create the Geoprocessor object
        gp = arcgisscripting.create()

        # Setting the Geoprocessing workspace
        gp.Workspace = workspace

        # Check out any necessary licenses
        arcpy.CheckOutExtension("spatial")

        # Set the Geoprocessing environment...
        gp.extent = DEM
        gp.cellSize = DEM

        # Set overwrite files to True
        gp.overwriteoutput = True

        #For loop reading the cost surface table inorder to get a count of the number of costSurface layers

        tableArray = []
        for line in open(costSurfaceTable):
            print "Reading costSurface Table line " + line
            tableArray.append(line)
        totalLines = len(tableArray)
        layers = totalLines - 1
        print "Number of costSurface layers " + str(layers)

        #for loop to convert all costSurface layers to raster format if needed and to give appropiate null values of 0 where the layer is undefined
        count = 0
        for line in tableArray:
            if count == 0:
                print "Reading Header Line"
                count = count + 1
            else:
                print "Converting inputs to Raster, Table line " + str(count) + " " + line
                lineStr = tableArray[count]
                line_split = lineStr.split(",")
                file = line_split[0]
                path = line_split[1]
                format = line_split[3]
                formatLc = format.lower()
                field = line_split[4]
                output = workspace + file[0:5]
                if formatLc == "raster":

                    # Process: Copy Raster and give name defined by output.
                    gp.CopyRaster_management(path, output, "", "", "", "NONE", "NONE", "")
                    count = count + 1


                else:
                    gp.FeatureToRaster_conversion(path, field, output, DEM)
                    count = count + 1

        #for loop overlaying layers to create costSurface layer - Start with base layer and overlayer ontop of this base layer (usually will be a continous layer such as
        #landcover or DEM) from decreasing to increasing order of presidence.  The layers with the highest rank will be overlaided last on the impedence surface.
        count = 1
        for t in tableArray:

            #if count + 1 == totalLines and totalLines != 3:             #If reached end of impedence Table exit loop, no more layers to overlay
            #    break

            if count == 1:            #Loop for the intitial costSurface layer (Base layer) and first overlay

                baseLayer = tableArray[totalLines - count]
                overLayer = tableArray[(totalLines - (count + 1))]
                print "Base Layer " + baseLayer + " Overlay Layer " + overLayer

                # Process: Overlay Layers..

                #base layer info
                baseSplit = baseLayer.split(",")
                baseFile = baseSplit[0]
                basePath = workspace + baseFile[0:5]     #Path to the grid to use as the base layer (usually will be landcover or someother continous data layer)

                belowSlopeNull = belowSlope      #Is null max slope layer (i.e. areas above the max slope = 0, all else = 1)
                slopeRemoved = workspace + "slopeRemoved"       #Grid with a defined impedance based on the baselayer and with areas greater than the defined Max Slope equal to zero
                mSlopeZero = workspace + "mSlopeZero"

                #Initially removing the areas defined as being to step for travel (The belowSlope grid).  If a road or trail cross then it will be passable.
                #Process: Is Null...Set input over layer with data equal to zero (0) all else (where no data) equal to 1
                # Process: Reclassify Max Slope

                gp.Reclassify_sa(belowSlopeNull, "VALUE", "0 0;1 NODATA", mSlopeZero, "DATA")
                gp.Con_sa(belowSlopeNull, basePath, slopeRemoved, mSlopeZero, "")   #Where equal to overlay raster = overlay raster, else equals overlayer output from previous loop

                #First Overlay layer info
                overSplit = overLayer.split(",")
                overFile = overSplit[0]
                overPath =  workspace + overFile[0:5]                    #Path to the overlay grid layer which is not null
                overPathNull = workspace + overFile[0:5] + "isNull"      #Path to the overlay grid layer which is null
                overOutput = workspace + "Overlay" + str(count)  #Output path and name for this overlay

                #Process: Is Null...Set input over layer with data equal to zero (0) all else (where no data) equal to 1
                gp.IsNull_sa(overPath, overPathNull)

                gp.Con_sa(overPathNull, slopeRemoved, overOutput, overPath, "")   #Where equal to overlay raster = overlay raster, else equals overlayer output from previous loop
                count = count + 1


            elif count + 1 == totalLines: # Loop for the final cost surface overlay output is the final costSurface grid.

                overLayer = tableArray[(totalLines - (count))]
                overLayer = tableArray[(totalLines - (count))]
                print "Base Layer " + baseLayer + " Overlay Layer " + overLayer

                # Process: Overlay Layers..
                #Baselayer information from previous overlay loop
                basePath = workspace + "Overlay" + str(count - 1)        #Path to the grid out put from the previous overlay operation

                #Overlay layer information for this loop
                overSplit = overLayer.split(",")
                overFile = overSplit[0]
                overPath =  workspace + overFile[0:5]                    #Path to the overlay grid layer which is not null
                overPathNull = workspace + overFile[0:5] + "isNull"      #Path to the overlay grid layer which is null


                #Process: Is Null...Set input over layer with data equal to zero (0) all else (where no data) equal to 1
                gp.IsNull_sa(overPath, overPathNull)
                gp.Con_sa(overPathNull, basePath, costSurface, overPath, "")   #Where equal to overlay raster = overlay raster, else equals baselayer
                #costSurface is the final costSurface overaly
                count = count + 1

            elif count == totalLines:               #If reached end of impedence Table exit loop, no more layers to overlay
                break

            else:       # Loop for all overlays between the first and last overlays.  (i.e. the middle overlays)


                overLayer = tableArray[(totalLines - (count + 1))]
                print "Base Layer " + baseLayer + " Overlay Layer " + overLayer

                # Process: Overlay Layers..
                #Baselayer information from previous overlay loop
                basePath = workspace + "Overlay" + str(count - 1)        #Path to the grid out put from the previous overlay operation

                #Overlay layer information for this loop
                overSplit = overLayer.split(",")
                overFile = overSplit[0]
                overPath =  workspace + overFile[0:5]                    #Path to the overlay grid layer which is not null
                overPathNull = workspace + overFile[0:5] + "isNull"      #Path to the overlay grid layer which is null



                overOutput = workspace + "Overlay" + str(count)          #Output path and name for this overlay

                #Process: Is Null...Set input over layer with data equal to zero (0) all else (where no data) equal to 1
                gp.IsNull_sa(overPath, overPathNull)
                gp.Con_sa(overPathNull, basePath, overOutput, overPath, "")   #Where equal to overlay raster = overlay raster, else equals baselayer

                count = count + 1

        return 1

    except:
        print ("costSurface.py Not Working")
        return 0

def speedSurfaceMS(roadsData,
                 DEM,
                 workspace,
                 extentDEM,
                 slope,
                 roadSpeed,
                 trailsData,
                 speedSurface,
                 trails,
                 walkingSpeed):
    '''
    SCRIPT NAME: speedCalculation.py

    ABSTRACT: Script is to be used as a module in the ttcsmMasterScript.py script.  This script generates a speed surface grid (speedSurface.grid) which has
    calculated speed (seconds/per meter) across the extent of the input DEM.  Cells coincident with the road network have speed defined by the road network speed (which is defined
    in miles per hour and then converted to seconds/per meter).  Cells coincident with the trail network have a speed defined by the only the trail slope, while all remaining
    areas have speed defined by hillside slope.  The trail and hillside slope velocity calculations are defined by the equation in the SOP, with the original equation being derived by Tobler 1993).

    ARGUMENTS passed by the ttcsmMasterScript.py:


    RETURNS:
    Final output is the speedSurface.grid which defines the speed (seconds/per meter) at which movement within the cell occurs.

    '''

    try:
        # Import system modules
        import sys, string, os, arcgisscripting, math, arcpy

        # Create the Geoprocessor object
        gp = arcgisscripting.create()

        # Setting the Geoprocessing workspace
        gp.Workspace = workspace

        # Check out any necessary licenses
        arcpy.CheckOutExtension("spatial")

        # Set the Geoprocessing environment...
        gp.extent = DEM
        gp.cellSize = DEM

        # Set overwrite files to True
        gp.overwriteoutput = True

        #internal hard coded paths below
        road1 = workspace + "road1"
        road2 = workspace + "road2.img"
        road_sm = workspace + "road_sm"

        trailRaster = workspace + "trailRaster"
        reclassTrail = workspace + "reclassTrail"
        rcTrailDem = workspace + "reTrailDem"
        slopeTrails = workspace + "slopeTrails"
        isNullSlope2 = workspace + "isNullSlope2"
        burnSlope = workspace + "burnSlope"
        speed1 = workspace + "speed1"
        trailElseSpd = workspace + "trailElseSpd"
        speedNoTrail = workspace + "speedNoTrail.img"
        speedAdjusted = workspace + "speedAdjusted.img"

        #########################
        ##Road Speed Calculations
        #########################
        Roads_Speed = "Velocity" # Field to use in the RoadShapefile
        # Process: Roads to Raster...
        gp.FeatureToRaster_conversion(roadsData, Roads_Speed, road1, DEM)

        # Process: Single Output Map Algebra... Converting from miles/per hour to seconds/per meter
        gp.SingleOutputMapAlgebra_sa("3600 / (" + road1 + " * 1.609 * 1000)", road_sm)

        # Process: Resize Roads to DEM Extent...
        algebraRoads1 = "((" + road_sm + ") + (" + extentDEM + " ) )"           #Note When the area of interest is large in size, computational limitations for simple map algebra
        gp.SingleOutputMapAlgebra_sa(algebraRoads1, road2)                      #can be an issue

        # Process: Replace Null Values with 99999...
        # Note Road3 raster has roads identified and the calculated travel time all else equals 9999
        algebraRoads2 = "CON ( ISNULL ( " + road2 + " ), 99999 , " + road2 + " )"
        #algebraRoads2 = "CON ( ISNULL ( " + road_sm + " ), 99999 , " + road_sm + " )"     #Skipping the resize to DEM extent
        gp.SingleOutputMapAlgebra_sa(algebraRoads2, roadSpeed)

        ##########################
        ##Calculate Trail Speed and Speed everywhere else based on Slope
        ##########################

        trailLC = trails.lower()
        if trails == "no":                          #routine to use if a trail network is not available

            # Process: Travel Speed from slope (Kilometers per hour)...Note Tan is in radians

            algebraTrailSpeed1 = "(6 * exp(-3.5 * (abs (tan ( ( " + slope + ") / (57.29578)) + .05))))"
            gp.SingleOutputMapAlgebra_sa(algebraTrailSpeed1, speed1)

            # Process: Calculate Travel Speed Seconds per Meter...
            #Note speedNoTrail is Travel speed in Seconds per Meter, prior to including impedence costs, also no road speed incorporated yet
            algebraTrailSpeed2 = "( 1 / (" + speed1 + " / 3.6))"
            gp.SingleOutputMapAlgebra_sa(algebraTrailSpeed2, speedNoTrail)

            ############################################
            # Adjusting speed surface to the user specific average walking speed
            # everywhere but the road surface.  The adjusted speed is a ratio of the
            # defined "walkingSpeed" divided by 3.13
            ############################################

            fltWalking = float(walkingSpeed)
            ratio = fltWalking / 3.13         # walking speed adjustment ratio
            strRatio = str(ratio)
            # Process: Divide...applying the walking speed adjustment ratio
            gp.Divide_sa(speedNoTrail, strRatio, speedAdjusted)

            ############################################
            # Overlay Road Travel Speed (roadSpeed) on Hillside slope speed (speedAdjusted)
            # Note Speed Calculation output: speedSurface has Road Speed on the road network and hillside slope speed everywhere else (unit Seconds per Meter).
            ############################################

            algebraRT = "CON (( " + roadSpeed + " <> 99999 ), (" + roadSpeed + " ), (" + speedAdjusted + "))"
            gp.SingleOutputMapAlgebra_sa(algebraRT, speedSurface)


        else:           #normal routine to use when trail network is being used

            # Process: TrailShapefile to raster...
            gp.PolylineToRaster_conversion(trailsData, "FID", trailRaster, "MAXIMUM_LENGTH", "NONE", "30")

            # Process: Reclassify all trails to a value of 1
            gp.Reclassify_sa(trailRaster, "VALUE", "0 100000 1", reclassTrail, "DATA")

            # Process: trail grid x DEM elevation, getting elevation along trails
            gp.Times_sa(reclassTrail, DEM, rcTrailDem)

            # Process: Calculate Slope of Trail in Degrees
            gp.Slope_sa(rcTrailDem, slopeTrails, "DEGREE", "1")

            # Process: Is Slope Null...
            gp.IsNull_sa(slopeTrails, isNullSlope2)

            # Process: Con: Pick Slope
            #Note output burnSlope is trail slope (via slopeTrails in degrees) else percent slope from slope raster (Degress).
            gp.Con_sa(isNullSlope2, slope, burnSlope, slopeTrails, "")

            # Process: Travel Speed from slope (Kilometers per hour)...Note Tan is in radians

            algebraTrailSpeed1 = "(6 * exp(-3.5 * (abs (tan ( ( " + burnSlope + ") / (57.29578)) + .05))))"
            gp.SingleOutputMapAlgebra_sa(algebraTrailSpeed1, speed1)

            # Process: Calculate Travel Speed Seconds per Meter...
            #Note trailElseSpeed is Travel speed in Seconds per Meter, prior to including impedence costs, also no road speed incorporated yet
            algebraTrailSpeed2 = "( 1 / (" + speed1 + " / 3.6))"
            gp.SingleOutputMapAlgebra_sa(algebraTrailSpeed2, trailElseSpd)

            ############################################
            # Adjusting speed surface to the user specific average walking speed
            # everywhere but the road surface.  The adjusted speed is a ratio of the
            # defined "walkingSpeed" divided by 3.13
            ############################################

            fltWalking = float(walkingSpeed)
            ratio = fltWalking / 3.13         # walking speed adjustment ratio
            strRatio = str(ratio)
            # Process: Divide...applying the walking speed adjustment ratio
            gp.Divide_sa(trailElseSpd, strRatio, speedAdjusted)

            ############################################
            # Overlay Road Travel Time on trailElseSpeed
            # Note Speed Calculation output: speedSurface has Road Speed, Trail Speed as well as Speed everywhere else in Seconds per Meter with out impedence included.
            ############################################

            algebraRT = "CON (( " + roadSpeed + " <> 99999 ), (" + roadSpeed + " ), (" + speedAdjusted + "))"
            gp.SingleOutputMapAlgebra_sa(algebraRT, speedSurface)


        return 1

    except:
        print ("speedCalculation.py Not Working")
        return 0



def travelCostSurfaceMS (speedSurface,
                  costSurface,
                  travelCost,
                  DEM,
                  suffix,
                  workspace):

    '''
    SCRIPT NAME: travelCostSurfaceMS.py

    ABSTRACT: Script is to be used as a module in the ttcsmMasterScript.py script.  Calculates the Travel Cost Surface, which is the derived by dividing the speed surface (Output from the costSurfaceMS.py script)
    by the Cost Surface (Output from the costSurfaceMS.py script).  The travel cost surface has the velocity (seconds per meter)at which movement within the cell occurs. From the travel cost surface a travel
    time surface (travelTimeOut.grid) is modeled using either cost distance or path distance modeling methods.  Please see the SOP document for further details.


    ARGUMENTS passed from the ttcsmMasterScript.py:


    RETURNS:
    A travel cost surface grid which has the velocity (seconds per meter)at which movement within the cell occurs.

    '''

    try:
        # Import system modules
        import sys, string, os, arcgisscripting, glob, arcpy

        # Create the Geoprocessor object
        gp = arcgisscripting.create()

        # Setting the Geoprocessing workspace
        gp.Workspace = workspace

        # Check out any necessary licenses
        arcpy.CheckOutExtension("spatial")


        # Set the Geoprocessing environment...
        gp.extent = DEM
        gp.cellSize = DEM

        # Set overwrite files to True
        gp.overwriteoutput = True

        impedFloat = workspace + "impedFloat_" + suffix + ".img"
        speedMph = workspace + "output\\travelCostMph.img"                #Travel Cost Surface Speed in Miles per Hour


        #########################################
        #Calculate The Final Travel Cost Surface:  speedSurface / costSurface = travelCost
        #########################################

        # Process: Convert costSurface grid to floating point with values from 0-1.
        algebraFlt = "((float ( " + costSurface + " )) / 100)"
        gp.SingleOutputMapAlgebra_sa(algebraFlt, impedFloat)

        # Process: Create Travel Cost surface
        algebraTC = "((" + speedSurface + ") / ("+ impedFloat +"))"
        gp.SingleOutputMapAlgebra_sa(algebraTC, travelCost)

        # Process: Convert seconds/meter to miles/hour for the travelcost travel cost surface grid
        algebraMph = "((0.62137119 * .001 * 3600) / ( " + travelCost + "))"
        gp.SingleOutputMapAlgebra_sa(algebraMph, speedMph)
        return 1

    except:
        print ("travelCostSurfaceMS.py Not Working")
        return 0

def travelTimeOutMS (startLocation,
                  travelCost,
                  DEM,
                  maxSlope,
                  usePathDistance,
                  verticalGraphType,
                  vertValueZero,
                  verticalGraph,
                  timeCap,
                  workspace,
                  suffix,
                  leastCostPath,
                  destinations,
                  memory,
                  logFileName):

    '''
    SCRIPT NAME: TravelTimeOutMS.py

    ABSTRACT: Script is to be used as a module in the ttcsmMasterScript.py script.  Using the travel cost surface (from the travelCostSurfaceMS.py script) a travel
    time out surface (travelTime{model type}.img) is modeled using either cost distance or path distance modeling methods.  Travel time out output grids are given in seconds
    (timeSecondsOut{model type}.img), minutes (timeMinutesOut{model Type}.img), and hours (timeHoursOut{model type}.img).  If path distance travel time modeling is selected it is necessary
    to define the desired vertical factor graph.  If Least Cost Paths are desired (i.e. "leastCostPath" = "yes"), then the "Destinations" path to a shapefile with the desired travel
    "To" points must be defined.  Least cost path output is a  shapefile (costPathsOut{model type}.shp) with the least cost paths from the start point(s) to the defined destination(s) points.

    Please see the TravelTimeCostSurfaceModelSOP document for further details.


    ARGUMENTS passed from the ttcsmMasterScript:


    RETURNS:
    One way cumulative travel times are calculated from the defined start point(s) and or start corridors(s) to all other locations within the area of interest.
    Travel time output grids are given in seconds (timeSeconds.grid), minutes (timeMinutes.grid), and hours (timeHours.grid).  If least cost paths are selected
    then a travel out least cost path shapefile will be made for each destination point.

    '''

    try:
        # Import system modules
        import sys, string, os, arcgisscripting, glob, arcpy

        # Create the Geoprocessor object
        gp = arcgisscripting.create()

        # Setting the Geoprocessing workspace
        gp.Workspace = workspace

        # Check out any necessary licenses
        arcpy.CheckOutExtension("spatial")

        # Set the Geoprocessing environment...
        gp.extent = DEM
        gp.cellSize = DEM

        # Set overwrite files to True
        gp.overwriteoutput = True
        arcpy.overwriteout = True


        timecap1 = workspace + "timecap1_" + suffix + ".img"
        maxsec1 = workspace + "maxsec1_" + suffix + ".img"
        nullMaxSec = workspace + "nullMaxSec_" + suffix + ".img"
        timeFloat = workspace + "timeFloat_" + suffix + ".img"
        timeMinflt = workspace + "timeMinFlt_" + suffix + ".img"
        timeMinOut = workspace + "output\\timeMinOut_" + suffix + ".img"
        timeHoursOut = workspace + "output\\timeHoursOut_" + suffix + ".img"
        timeSecondsOut = workspace + "output\\timeSecondsOut_" + suffix + ".img"
        backLine = workspace + "backLineOut_" + suffix + ".img"                        #backline output from the cost/path distance modeling out calculations
        usePathDistanceLc = usePathDistance.lower()
        costPathsOut = workspace + "output\\costPathsOut_" + suffix + ".shp"            #merged Out travel cost paths shapefile
        travelTimeOut = workspace + "output\\travelTimeOut_" + suffix + ".img"         #calculated one way (travel out) travel time - output from the cost distance model (using either Cost Distance or Path Distance).
        indexFileOut = workspace + "AA_TravelTimeIndex.txt"                                #index file used to clear memory within the Travel Time Out and Back functions


        ###################################################################################################
        #Setting up index file to shut down Script after completion of section in TravelTimeOutMS
        ###################################################################################################
        if os.path.exists(indexFileOut):
            pass
        else:
            WriteIndex(indexFileOut, "")


        if memory.lower() == "yes":
            #Opening indexfileOut for writing
            IndexFile = open(indexFileOut, "a")
            Start_Index = str(GetIndex(indexFileOut))  #Grabbing the Start_Index value to determine where script has previously ran
            IndexFile.close()
            if Start_Index == "0":          #Defining Start_Index as 0 when the script is starting from beginning.
                WriteIndex(indexFileOut, "0")
            elif Start_Index == "TravelTimeOutMS Step 3 Done":
                logFile = open(logFileName, "a")
                messageTime = timeFun()
                scriptMsg = "TravelTimeOutMS Completed - Ready for TravelTimeBackMS if selected " + messageTime
                logFile.write(scriptMsg)
                logFile.close()
                print "TravelTimeOutMS Completed - Ready for TravelTimeBackMS if selected"
                raise Exception, scriptMsg

            else:
                pass

        else:       #When memory not set to yes
            pass


        #################################################################
        # Cost Distance travel time modeling using either traditional Cost Distance modeling, or Path Distance modeling
        # Path Distance modeling default parameters for the vertical factor graphs are a zero factor value of 1, and
        # low and high cut angle values of -45, and 45.
        # Output travelTimeOut is the calculated one way (travel out) distance travel cost time in seconds.
        #################################################################


        Start_Index = str(GetIndex(indexFileOut))  #Grabbing the Start_Index value
        if (memory.lower() == "no" or (memory.lower() == "yes" and Start_Index == "0")):       #If true perform travelTimeOutMS function
            # if pathDistance travel time modeling is desired, finding the selected vertical factor graph
            if usePathDistanceLc == "yes":
                negSlope = "-" + maxSlope
                pathDistanceLC = verticalGraphType.lower()
                if pathDistanceLC == "binary":              #binary vertical factor graph
                    type = "BINARY"
                    binarySyntax = type + " " + vertValueZero + " " + negSlope + " " + maxSlope
                    gp.PathDistance_sa(startLocation, travelTimeOut, travelCost, "", "", "", DEM, binarySyntax, "", backLine)

                elif pathDistanceLC == "linear":            #linear vertical factor graph
                    type = "LINEAR"
                    linearSyntax = type + " " + vertValueZero + " " + negSlope + " " + maxSlope + " 0.011111"
                    gp.PathDistance_sa(startLocation, travelTimeOut, travelCost, "", "", "", DEM, linearSyntax, "", backLine)

                elif pathDistanceLC == "sym_linear":        #symetrical vertical factor graph
                    type = "SYM_LINEAR"
                    symlinearSyntax = type + " " + vertValueZero + " " + negSlope + " " + maxSlope + " 0.011111"
                    gp.PathDistance_sa(startLocation, travelTimeOut, travelCost, "", "", "", DEM, symlinearSyntax, "", backLine)

                elif pathDistanceLC == "inverse_linear":    #inverse linear vertical factor graph
                    type = "INVERSE_LINEAR"
                    inverseLinearSyntax = type + " " + vertValueZero + " " + negSlope + " " + maxSlope + " -0.022222"
                    gp.PathDistance_sa(startLocation, travelTimeOut, travelCost, "", "", "", DEM, inverseLinearSyntax, "", backLine)

                elif pathDistanceLC == "sym_inverse_linear":    #symetrical inverse linear vertical factor graph
                    type = "SYM_INVERSE_LINEAR"
                    symInverseLinearSyntax = type + " " + vertValueZero + " " + negSlope + " " + maxSlope + " -0.022222"
                    gp.PathDistance_sa(startLocation, travelTimeOut, travelCost, "", "", "", DEM, symInverseLinearSyntax, "", backLine)

                elif pathDistanceLC == "cos":       #COS vertical factor graph
                    type = "COS"
                    cosSyntax = type + " -90 90 1"
                    gp.PathDistance_sa(startLocation, travelTimeOut, travelCost, "", "", "", DEM, cosSyntax, "", backLine)

                elif pathDistanceLC == "sec":       #SEC vertical factor graph
                    type = "SEC"
                    secSyntax = type + " -90 90 1"
                    gp.PathDistance_sa(startLocation, travelTimeOut, travelCost, "", "", "", DEM, secSyntax, "", backLine)

                elif pathDistanceLC == "cos_sec":   #COS SEC vertical factor graph
                    type = "COS-SEC"
                    cossecSyntax = type + " -90 90 1 1"
                    gp.PathDistance_sa(startLocation, travelTimeOut, travelCost, "", "", "", DEM, cossecSyntax, "", backLine)

                elif pathDistanceLC == "sec_cos":   #SEC COS vertical factor graph
                    type = "SEC-COS"
                    seccosSyntax = type + " -90 90 1 1"
                    gp.PathDistance_sa(startLocation, travelTimeOut, travelCost, "", "", "", DEM, seccosSyntax, "", backLine)

                elif pathDistanceLC == "table":     #user defined vertical factor graph
                    type = "TABLE"
                    tableSyntax = type + " " + verticalGraph
                    gp.PathDistance_sa(startLocation, travelTimeOut, travelCost, "", "", "", DEM, tableSyntax, "", backLine)

                else:
                    print "Vertical Graph Type is undefined Travel Time Not Calculated"
                    return 0


            else:  #If Cost Distance travel time modeling is desired
                gp.CostDistance_sa(startLocation, travelCost, travelTimeOut, "", backLine)

            if memory.lower() == "yes":       #If memory set to yes and travelTimeOutMS successful
                WriteIndex(indexFileOut, "TravelTimeOutMS Step 1 Done")
                messageTime = timeFun()
                scriptMsg = "Exiting - To Clear Memory - TravelTimeOutMS Step 1 Done " + messageTime
                logFile = open(logFileName, "a")
                logFile.write(scriptMsg + "\n")
                raise Exception, scriptMsg
            else:
                pass

        else:   #TravelTimeOut Step 1 has already been performed
            pass

        Start_Index = str(GetIndex(indexFileOut))  #Grabbing the Start_Index value
        if (memory.lower() == "no" or (memory.lower() == "yes" and Start_Index == "TravelTimeOutMS Step 1 Done")):
            ###################################################
            # Process to convert travel time from seconds to minutes and hours
            ###################################################

            # Process: GTE: Travel Time >= Time Cap (2)... Making the timecap1 data layer with identifying
            # locations with a travel time greater then defined maximum travel time.  These areas will be given
            # a value of 1 all else = 0.
            gp.GreaterThanEqual_sa(travelTimeOut, timeCap, timecap1)

            # Process: Con: Maxsec1 grid is the output grid for this function.
            # Setting areas where timecap1 equals 1 (all areas with a time > than the time cap),
            # to the time cap value (i.e. 28800 seconds), otherwise the maxsec1 grid equals
            # the travelTimeOut grid.

            gp.Con_sa(timecap1, timeCap, maxsec1, travelTimeOut, "")

            # Process: Making the nullMaxSec grid.  Areas with no data (i.e. null)
            # in the maxsec1 grid are assigned a value of 1, and all other areas a value of zero.
            gp.IsNull_sa(maxsec1, nullMaxSec)

            # Process: IsNull: timeFloat grid is the output grid for this function.
            # Setting areas where nullMaxSec equals 1 (i.e. locations of not data) to the the timecap value,
            # otherwise the timeFloat grid equals the maxsec1 grid.
            # If no data values are desired to have a value different from the timecap value (i.e. -9999)
            # then define a "nodata" variable and replace the timeCap variable in this function with the "nodata" variable

            gp.Con_sa(nullMaxSec, timeCap, timeFloat, maxsec1, "")

            # Process: Convert travel time to Minutes...

            algebraCostDistance1 =  "((( " + timeFloat + ") / 60))"
            gp.SingleOutputMapAlgebra_sa(algebraCostDistance1, timeMinflt)

             # Process: Convert timeMinflt to an integer grid.
            gp.Int_sa(timeMinflt, timeMinOut)

            # Process: Convert timeFloat to a time Hours grid.
            algebraCostDistance2 = "((( " + timeFloat + ") / 3600))"
            gp.SingleOutputMapAlgebra_sa(algebraCostDistance2, timeHoursOut)

            # Process: Convert timeFloat to an integer grid (travel time seconds integer).
            gp.Int_sa(timeFloat, timeSecondsOut)
            if memory.lower() == "yes":       #If memory set to yes and travelTimeOutMS successful
                messageTime = timeFun()
                WriteIndex(indexFileOut, "TravelTimeOutMS Step 2 Done")
                scriptMsg = "Exiting - To Clear Memory - TravelTimeOutMS Step 2 Done " + messageTime
                logFile = open(logFileName, "a")
                logFile.write(scriptMsg + "\n")
                raise Exception, scriptMsg
            else:
                pass


        else:   #TravelTimeOut Step 2 has already been performed
            pass


        Start_Index = str(GetIndex(indexFileOut))  #Grabbing the Start_Index value
        if (memory.lower() == "no" or (memory.lower() == "yes" and Start_Index == "TravelTimeOutMS Step 2 Done")):

            #############################################################
            # Least cost path analysis for the travel out travel times.
            #############################################################
            leastCostPathLC = leastCostPath.lower()
            if leastCostPathLC == "yes":
                #while loop to populate the fidList variable for each defined destination point
                fidList = []
                rowsDest = gp.searchcursor(destinations,"","","","")
                rowDest = rowsDest.next()

                while rowDest:
                    rowFID = rowDest.FID
                    fidList.append(rowFID)
                    rowDest = rowsDest.next()

                ##################################################################
                #loop to derive the least cost paths per defined destination point
                ##################################################################

                for fid in fidList:
                    # Process: Select each individual Desintation Shapefile to process
                    syntax = "\"FID\" = " + str(fid)
                    pathOut = workspace + "paths\\fid_" + str(fid) + ".shp"     #Individual Destination Point Shapefile
                    pathOutImg = workspace + "paths\\fid_" + str(fid) + ".img"  #Individual Cost Path Raster
                    costPathShp = workspace + "paths\\costPathId_" + str(fid) + ".shp"  #Individual Cost Path Shapefile
                    extractShp = workspace + "paths\\extractId_" + str(fid) + ".shp"  #Individual Cost Path Shapefile
                    gp.Select_analysis(destinations, pathOut , syntax)          #Creating Individual Destination Shapefiles

                   # Process: Cost Path Calculation per individual destination
                    gp.CostPath_sa(pathOut, travelTimeOut, backLine, pathOutImg , "EACH_CELL", "FID")  #Creating Individual Destination Cost Paths
                    # Process: Raster to Polyline...
                    gp.RasterToPolyline_conversion(pathOutImg, costPathShp, "NODATA", "0", "NO_SIMPLIFY", "VALUE") #Converting raster cost paths to shapefiles

                    # Process: Add travel time fields
                    arcpy.AddField_management(costPathShp, "seconds", "LONG", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
                    arcpy.AddField_management(costPathShp, "minutes", "FLOAT", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
                    arcpy.AddField_management(costPathShp, "hours", "FLOAT", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
                    arcpy.AddField_management(costPathShp, "uniqueid", "TEXT", "", "", "20", "", "NON_NULLABLE", "NON_REQUIRED", "")

                    # Process: Defining the uniequeid field
                    gp.CalculateField_management(costPathShp, "uniqueid", str(fid), "PYTHON_9.3", "")

                    ######################################
                    #Routine to find the travel cost value at the original start point (i.e. the end point of the travel back routine)
                    ######################################

                    # Process: Extract Travel Time value from the original start point (which is the destination point in this case)
                    gp.ExtractValuesToPoints_sa(pathOut, travelTimeOut, extractShp, "NONE", "VALUE_ONLY")

                    timeBack = []
                    rowsExt = gp.searchcursor(extractShp,"","","","")       #grabbing the travel back time to
                    rowExt = rowsExt.next()

                    while rowExt:               #populating the travel back time to the timeBack list
                        rowValue = rowExt.rastervalu
                        timeBack.append(rowValue)
                        rowExt = rowsExt.next()
                    timeBackStr = str(timeBack)
                    b = timeBackStr[1:-1]
                    fl = float(b)
                    inputLong = long(fl)        #the travel back time from the least cost path analysis.

                    # Process: Calculating the travel back times for the costPathShp shapefile
                    arcpy.CalculateField_management(costPathShp, "seconds", inputLong, "PYTHON_9.3", "")
                    arcpy.CalculateField_management(costPathShp, "minutes", "(!seconds!/ 60)", "PYTHON_9.3", "")
                    arcpy.CalculateField_management(costPathShp, "hours", "(!seconds!/ 3600)", "PYTHON_9.3", "")



                ###########################################
                ##Merging all Cost Paths into one shapefile
                ###########################################

                pathCostPath = workspace + "paths\\"
                costPaths = glob.glob(workspace + "paths\\" + "costpathId*.shp")
                inter = str(costPaths)
                inter2 = inter.replace('[','"')
                inter3 = inter2.replace(']','"')
                inter4 = inter3.replace("'",'')
                mergeSyntax = inter4.replace(',', ';')
                costPathsMrg = workspace + "paths\\costPathsMrg_" + suffix + ".shp"         #intermediate data layer with all mergeded cost paths prior to dissolving
                #Process Merging all out distance cost paths into one shapefile
                gp.Merge_management(mergeSyntax, costPathsMrg, "")

                # Process: Dissolving merged cost paths on the uniqueid field
                gp.Dissolve_management(costPathsMrg, costPathsOut, "minutes;seconds;uniqueid", "", "MULTI_PART", "DISSOLVE_LINES")

                if memory.lower() == "yes":       #If memory set to yes and travelTimeOutMS successful
                    WriteIndex(indexFileOut, "TravelTimeOutMS Step 3 Done")

                else:
                    pass

            else:
                print "Least Cost Path Option Not Selected"

        return 1

    except:
        print ("travelTimeOutMS.py Not Working")
        return 0

def travelTimeBackMS (startLocation,
                  travelCost,
                  travelTimeOut,
                  DEM,
                  maxSlope,
                  usePathDistance,
                  verticalGraphType,
                  vertValueZero,
                  verticalGraph,
                  timeCap,
                  workspace,
                  suffix,
                  timeCalculation,
                  leastCostPath,
                  destinations,
                  costPathsOut,
                  memory,
                      logFileName):

    '''
    SCRIPT NAME: travelTimeBackMS.py

    ABSTRACT: Script is to be used as a module in the ttcsmMasterScript.py script.  Using the travel cost surface (from the travelCostSurfaceMS.py script) travel
    time back from the defined destination points back to the defined start location are calculated, using either cost distance or path distance modeling.  Travel time back calculations
    are only performed if "timeCalculation" is set to "RoundTrip".  Least Cost Paths are calculated from each destination point back to the start location(s).  Travel time back output is a
    least cost path shapefile (costPathsBack{model type}.shp).


    ARGUMENTS:


    EXAMPLE:

    RETURNS:

    Travel back travel time least cost path shapefile, with the travel time(s) from the defined destination point(s) back to the closest start locations.

    '''

    try:
        # Import system modules
        import sys, string, os, arcgisscripting, shutil, glob, arcpy

        # Create the Geoprocessor object
        gp = arcgisscripting.create()

        # Setting the Geoprocessing workspace
        gp.Workspace = workspace

        # Check out any necessary licenses
        arcpy.CheckOutExtension("spatial")

        import glob
        # Set the Geoprocessing environment...
        gp.extent = DEM
        gp.cellSize = DEM

        # Set overwrite files to True
        gp.overwriteoutput = True

        timecap1 = workspace + "timecap1_" + suffix + ".img"
        maxsec1 = workspace + "maxsec1_" + suffix + ".img"
        nullMaxSec = workspace + "nullMaxSec_" + suffix + ".img"
        usePathDistanceLc = usePathDistance.lower()
        costPathsBack = workspace + "output\\costPathsBack_" + suffix + ".shp"                      #merged back travel cost paths shapefile
        indexFileOut = workspace + "AA_TravelTimeIndex.txt"                                #index file used to clear memory within the Travel Time Out and Back functions


        ###################################################################################################
        #Setting up index file to shut down Script after completion of  individual sections in TravelTimeBackMS
        ###################################################################################################
        if os.path.exists(indexFileOut):
            pass
        else:
            WriteIndex(indexFileOut, "")

        if memory.lower() == "yes":
            #Opening indexfileOut for writing
            IndexFile = open(indexFileOut, "a")
            Start_Index = str(GetIndex(indexFileOut))  #Grabbing the Start_Index value to determine where script has previously ran
            IndexFile.close()
            if Start_Index == "0" or Start_Index == "TravelTimeOutMS Step 3 Done":          #Defining Start_Index as 0 when the script is starting from beginning.
                WriteIndex(indexFileOut, "0")
            elif Start_Index == "TravelTimeBackMS Step 3 Done":
                logFile = open(logFileName, "a")
                messageTime = timeFun()
                scriptMsg = "TravelTimeBackMS Completed - TTCSM Processing Completed " + messageTime
                logFile.write(scriptMsg)
                logFile.close()
                print "TravelTimeBackMS Completed - TTCSM Processing Completed"
                raise Exception, scriptMsg

            else:
                pass

        else:       #When memory not set to yes
            pass


        #################################################################################################################
        # If Out and Back travel Time Calculation is desired performs the selected path distance or cost distance modeling.
        # for each destination point back to the original source location.  Allowing for the calculation of a round trip time.
        #################################################################################################################

        Start_Index = str(GetIndex(indexFileOut))  #Grabbing the Start_Index value
        if (memory.lower() == "no" or (memory.lower() == "yes" and Start_Index == "0")):       #If true perform travelTimeOutMS function

            #while loop to populate the destList variable for each destination point
            destList = []
            rowsDest = gp.searchcursor(destinations,"","","","")
            rowDest = rowsDest.next()

            while rowDest:
                rowFID = rowDest.FID
                destList.append(rowFID)
                rowDest = rowsDest.next()

            ###########################################
            #For loop to derive the Travel Back Travel Time Surfaces & Cost Paths for each destination point
            ###########################################


            if usePathDistanceLc == "yes":                      #if path distance selected, find the vertical factor graph which was selected.


                for dest in destList:
                    travelTimeBack = workspace + "back\\TravelTimeBack_" + suffix + "_FID" + str(dest) + ".img"         #calculated one way (travel back) travel time - output from the cost distance model (using either Cost Distance or Path Distance).
                    backLineBack = workspace + "back\\backLineBack_" + suffix + "_FID" + str(dest) + ".img"                        #backline output from the cost/path distance modeling back calculations
                    syntax = "\"FID\" = " + str(dest)
                    destShp = workspace + "back\\fid_" + str(dest) + ".shp"     #Individual Destination Point Shapefile

                    gp.Select_analysis(destinations, destShp , syntax)          #Creating Individual Destination Shapefiles for use in back travel time modeling

                    negSlope = "-" + maxSlope
                    pathDistanceLC = verticalGraphType.lower()
                    if pathDistanceLC == "binary":              #binary vertical factor graph
                        type = "BINARY"
                        binarySyntax = type + " " + vertValueZero + " " + negSlope + " " + maxSlope
                        gp.PathDistance_sa(destShp, travelTimeBack, travelCost, "", "", "", DEM, binarySyntax, "",  backLineBack)

                    elif pathDistanceLC == "linear":            #linear vertical factor graph
                        type = "LINEAR"
                        linearSyntax = type + " " + vertValueZero + " " + negSlope + " " + maxSlope + " 0.011111"
                        gp.PathDistance_sa(destShp, travelTimeBack, travelCost, "", "", "", DEM, linearSyntax, "",  backLineBack)

                    elif pathDistanceLC == "sym_linear":        #symetrical vertical factor graph
                        type = "SYM_LINEAR"
                        symlinearSyntax = type + " " + vertValueZero + " " + negSlope + " " + maxSlope + " 0.011111"
                        gp.PathDistance_sa(destShp, travelTimeBack, travelCost, "", "", "", DEM, symlinearSyntax, "",  backLineBack)

                    elif pathDistanceLC == "inverse_linear":    #inverse linear vertical factor graph
                        type = "INVERSE_LINEAR"
                        inverseLinearSyntax = type + " " + vertValueZero + " " + negSlope + " " + maxSlope + " -0.022222"
                        gp.PathDistance_sa(destShp, travelTimeBack, travelCost, "", "", "", DEM, inverseLinearSyntax, "",  backLineBack)

                    elif pathDistanceLC == "sym_inverse_linear":    #symetrical inverse linear vertical factor graph
                        type = "SYM_INVERSE_LINEAR"
                        symInverseLinearSyntax = type + " " + vertValueZero + " " + negSlope + " " + maxSlope + " -0.022222"
                        gp.PathDistance_sa(destShp, travelTimeBack, travelCost, "", "", "", DEM, symInverseLinearSyntax, "",  backLineBack)

                    elif pathDistanceLC == "cos":       #COS vertical factor graph
                        type = "COS"
                        cosSyntax = type + " -90 90 1"
                        gp.PathDistance_sa(destShp, travelTimeBack, travelCost, "", "", "", DEM, cosSyntax, "",  backLineBack)

                    elif pathDistanceLC == "sec":       #SEC vertical factor graph
                        type = "SEC"
                        secSyntax = type + " -90 90 1"
                        gp.PathDistance_sa(destShp, travelTimeBack, travelCost, "", "", "", DEM, secSyntax, "",  backLineBack)

                    elif pathDistanceLC == "cos_sec":   #COS SEC vertical factor graph
                        type = "COS-SEC"
                        cossecSyntax = type + " -90 90 1 1"
                        gp.PathDistance_sa(destShp, travelTimeBack, travelCost, "", "", "", DEM, cossecSyntax, "",  backLineBack)

                    elif pathDistanceLC == "sec_cos":   #SEC COS vertical factor graph
                        type = "SEC-COS"
                        seccosSyntax = type + " -90 90 1 1"
                        gp.PathDistance_sa(destShp, travelTimeBack, travelCost, "", "", "", DEM, seccosSyntax, "",  backLineBack)

                    elif pathDistanceLC == "table":     #user defined vertical factor graph
                        type = "TABLE"
                        tableSyntax = type + " " + verticalGraph
                        gp.PathDistance_sa(destShp, travelTimeBack, travelCost, "", "", "", DEM, tableSyntax, "",  backLineBack)

                    else:
                        print "Vertical Graph Type is undefined Travel Time Not Calculated"
                        return 0

            else:  #If Cost Distance modeling is desired
                print "Using the already derived cost distance travel cost surface"

            if memory.lower() == "yes":       #If memory set to yes and travelTimeBackMS section 1 successful
                WriteIndex(indexFileOut, "TravelTimeBackMS Step 1 Done")
                messageTime = timeFun()
                scriptMsg = "Exiting - To Clear Memory - TravelTimeBackMS Step 1 Done " + messageTime
                logFile = open(logFileName, "a")
                logFile.write(scriptMsg + "\n")
                raise Exception, scriptMsg
            else:
                pass

        else:   #TravelTimeBackMS Step 1 has already been performed
            pass


        ##########################################################################################################
        ##Perform the least cost path analysis using each destinations unique travel time surface (travelTimeBack)
        ##########################################################################################################

        Start_Index = str(GetIndex(indexFileOut))  #Grabbing the Start_Index value
        if (memory.lower() == "no" or (memory.lower() == "yes" and Start_Index == "TravelTimeBackMS Step 1 Done")):       #If true perform travelTimeOutMS function

            #while loop to populate the destList variable for each destination point
            destList = []
            rowsDest = gp.searchcursor(destinations,"","","","")
            rowDest = rowsDest.next()

            while rowDest:
                rowFID = rowDest.FID
                destList.append(rowFID)
                rowDest = rowsDest.next()


            for dest in destList:
                leastCostPathLC = leastCostPath.lower()
                if leastCostPathLC == "yes" and usePathDistanceLc == "yes":
                    syntax = "\"FID\" = " + str(dest)
                    pathBackImg = workspace + "back\\fid_" + str(dest) + ".img"  #Individual Cost Path Raster
                    costPathShp = workspace + "back\\costPathId_" + str(dest) + ".shp"  #Individual Cost Path Shapefile
                    extractShp = workspace + "back\\extractId_" + str(dest) + ".shp"  #Individual Cost Path Shapefile
                    travelTimeBack = workspace + "back\\TravelTimeBack_" + suffix + "_FID" + str(dest) + ".img"         #calculated one way (travel back) travel time - output from the cost distance model (using either Cost Distance or Path Distance).
                    backLineBack = workspace + "back\\backLineBack_" + suffix + "_FID" + str(dest) + ".img"                        #backline output from the cost/path distance modeling back calculations

                    # Process: Cost Path Calculation
                    gp.CostPath_sa(startLocation, travelTimeBack, backLineBack, pathBackImg , "BEST_SINGLE", "FID")
                    # Process: Raster to Polyline...
                    gp.RasterToPolyline_conversion(pathBackImg, costPathShp, "NODATA", "0", "NO_SIMPLIFY", "VALUE") #Converting raster cost paths to shapefiles

                    # Process: Add Fields
                    arcpy.AddField_management(costPathShp, "seconds", "LONG", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
                    arcpy.AddField_management(costPathShp, "minutes", "FLOAT", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
                    arcpy.AddField_management(costPathShp, "hours", "FLOAT", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
                    arcpy.AddField_management(costPathShp, "uniqueid", "TEXT", "", "", "20", "", "NON_NULLABLE", "NON_REQUIRED", "")

                    # Process: Calculate Field...
                    arcpy.CalculateField_management(costPathShp, "uniqueid", str(dest), "PYTHON_9.3", "")

                    ######################################
                    #Routine to find the travel cost value at the original start point (i.e. the end point of the travel back routine)
                    ######################################

                    #Checking to see if the startLocation data layer is linear or point
                    checkStart = gp.Describe(startLocation)
                    test = checkStart.shapeType

                    if test == "Point":
                        # Process: Extract Values to Points...
                        gp.ExtractValuesToPoints_sa(startLocation, travelTimeBack, extractShp, "NONE", "VALUE_ONLY")

                    else:   #Must convert the linear Start Location data layer to a point file so points can be extarcted below
                        roadOut = workspace + "roadPoints.shp"
                        if os.path.exists(roadOut):
                            pass
                        else:
                            roadPoints = gp.FeatureToPoint_management(startLocation, roadOut, "CENTROID") #Note this is taking the centroid of the polylines this might not be desirable
                        # Process: Extract Values to Points...
                        gp.ExtractValuesToPoints_sa(roadOut, travelTimeBack, extractShp, "NONE", "VALUE_ONLY")

                    timeBack = []
                    rowsExt = gp.searchcursor(extractShp,"","","","")
                    rowExt = rowsExt.next()

                    while rowExt:
                        rowValue = rowExt.rastervalu
                        timeBack.append(rowValue)
                        rowExt = rowsExt.next()
                    timeBack.sort()                 #sorting the timeBack list to get the fastest travel time destination when multiple starting points are an option.
                    for value in timeBack:  #loop to find the smallest value (i.e. fastest time) which is not negative (i.e. no data)
                        if value <= 0:  #when < 0
                            pass
                        else:       #Assigning the first value > 0, the fastest value (i.e. fastest time)
                            fastest = value
                            break

                    timeBackStr = str(fastest)
                    fl = float(timeBackStr)
                    inputLong = long(fl)

                    # Process: Calculate Seconds, Minutes, and Hour Fields in the costPathShp shapefile
                    arcpy.CalculateField_management(costPathShp, "seconds", inputLong, "PYTHON_9.3", "")
                    arcpy.CalculateField_management(costPathShp, "minutes", "(!seconds!/ 60)", "PYTHON_9.3", "")
                    arcpy.CalculateField_management(costPathShp, "hours", "(!seconds!/ 3600)", "PYTHON_9.3", "")

                #IF cost distance travel time modeling is selected
                elif leastCostPathLC == "yes":
                    outLoc = workspace + "output\\"       #location of the Travel Back directory
                    backLoc = workspace + "back\\"
                    costPathCopy = glob.glob(outLoc + "costPathsOut_Cost_Distance.*")
                    for files in costPathCopy:
                        shutil.copy(files, backLoc)

                        #os.rename(outLocCost,costPathsBack)
                    rename = glob.glob(backLoc + "costPathsOut_Cost_Distance.*")
                    for files in rename:
                       if os.path.exists(files.replace("Out","Back")):
                           os.remove(files.replace("Out","Back"))
                       else:
                           pass
                       os.rename(files, files.replace("Out","Back"))
                else:
                    print "Least Cost Path Option Not Selected"

            if leastCostPathLC == "yes" and usePathDistanceLc == "no":
                backFile = glob.glob(backLoc + "costPathsBack_Cost_Distance.*")
                for files in backFile:          #Loop to copy over the travel back least cost path(s) shapefile when cost distance modeling (note this is a copy of the travel out file).
                    shutil.copy(files, outLoc)

            else:  #When path distance modeling is performed merge all individual travel back cost paths.

                ###########################################
                ##Merging all Path Distance Modeling Cost Paths into one shapefile
                ###########################################

                costPaths = glob.glob(workspace + "back\\costpathId*.shp")
                inter = str(costPaths)
                inter2 = inter.replace('[','"')
                inter3 = inter2.replace(']','"')
                inter4 = inter3.replace("'",'')
                mergeSyntax = inter4.replace(',', ';')
                costPathsInt = workspace + "back\\costPathsInt_" + suffix + ".shp"
                #Process Merging all out distance cost paths into one shapefile
                gp.Merge_management(mergeSyntax, costPathsInt, "")

                # Process: Dissolving merged cost paths on the uniqueid field
                gp.Dissolve_management(costPathsInt, costPathsBack, "minutes;seconds;uniqueid", "", "MULTI_PART", "DISSOLVE_LINES")

                if memory.lower() == "yes":       #If memory set to yes and travelTimeOutMS successful
                    WriteIndex(indexFileOut, "TravelTimeBackMS Step 2 Done")

                else:
                    pass

            if memory.lower() == "yes":       #If memory set to yes and travelTimeOutMS successful
                WriteIndex(indexFileOut, "TravelTimeBackMS Step 2 Done")
            else:
                print "Least Cost Path Option Not Selected"

        return 1


    except:
        print ("travelTimeBackMS.py Not Working")
        return 0


def WriteIndex(filename, value):
    outfile = open (filename, "w")
    outfile.write(str(value))
    outfile.close()
    return 'Success'

def GetIndex(filename):
    infile = open(filename, 'r')
    numLines = infile.readlines()
    t=len(numLines)
    if t == 0:
        indexLine = 0
    else:
        indexLine = numLines[t-1]   #Defining the last line in the index file
        infile.close()
    return indexLine

def timeFun():
    ###############################################################
    # timeFun.function
    #
    # ABSTRACT:
    # Functions to get a time for logFile Tracking
    #
    # CREATED BY:
    # Kirk Sherrill Geospatial Specialist, I&M Division, NRPC, NPS.
    ###############################################################

    from datetime import datetime
    b=datetime.now()
    messageTime = b.isoformat()
    return messageTime


def setupTest(startLocation, roadsData, trailsData, DEM, destinations, costSurfaceTable, workspace, leastCostPath, timeCalculation, trails):
    ###############################################################
    # setupText.function
    #
    # ABSTRACT:
    # Testing set up parameters to verify if they are logically possible
    # and that defined data layers exist
    # CREATED BY:
    # Kirk Sherrill Geospatial Specialist, I&M Division, NRPC, NPS.
    ###############################################################

    import sys, string, os, arcgisscripting, math, arcpy
    try:
        variable = "all defined data sources exists"
        #Checking that defined data layers exist

        check = startLocation
        gdbTest = ".gdb"
        if gdbTest in check:
            name = os.path.basename(startLocation)
            gdbPath = startLocation.replace("\\" + name,"")
            arcpy.geoprocessing.env.workspace = gdbPath
            fcList = arcpy.ListFeatureClasses()
            if name in fcList:
                print startLocation + " exists"
            else:
                variable = startLocation + " does not exist"
                return 0, variable
        elif os.path.exists(startLocation):
            print startLocation + " exists"
        else:
            variable = startLocation + " does not exist"
            return 0, variable

        check2 = roadsData
        gdbTest = ".gdb"
        if gdbTest in check2:
            name2 = os.path.basename(roadsData)
            gdbPath2 = roadsData.replace("\\" + name2,"")
            arcpy.geoprocessing.env.workspace = gdbPath2
            fcList = arcpy.ListFeatureClasses()
            if name2 in fcList:
                print roadsData + " exists"
            else:
                variable = roadsData + " does not exist"
                return 0, variable
        elif os.path.exists(roadsData):
            print roadsData + " exists"
        else:
            variable = roadsData + " does not exist"
            return 0, variable

        if trails.lower() == "no":
            pass
        else:
            check3 = trailsData
            gdbTest = ".gdb"
            if gdbTest in check3:
                name3 = os.path.basename(roadsData)
                gdbPath3 = trailsData.replace("\\" + name3,"")
                arcpy.geoprocessing.env.workspace = gdbPath3
                fcList = arcpy.ListFeatureClasses()
                if name3 in fcList:
                    print trailsData + " exists"
                else:
                    variable = trailsData + " does not exist"
            elif os.path.exists(trailsData):
                print trailsData + " exists"
            else:
                variable = trailsData + " does not exist"
                return 0, variable

        check4 = DEM
        gdbTest = ".gdb"
        if gdbTest in check4:
            name4 = os.path.basename(DEM)
            gdbPath4 = DEM.replace("\\" + name4,"")
            arcpy.geoprocessing.env.workspace = gdbPath4
            fcList = arcpy.ListRasters()
            if name4 in fcList:
                print DEM + " exists"
            else:
                variable = DEM + " does not exist"
                return 0, variable

        elif os.path.exists(DEM):
            print DEM + " exists"
        else:
            variable = DEM + " does not exist"
            return 0, variable

        if leastCostPath.lower()== "no":
            pass
        else:

            check5 = destinations
            gdbTest = ".gdb"
            if gdbTest in check5:
                name5 = os.path.basename(destinations)
                gdbPath5 = destinations.replace("\\" + name5,"")
                arcpy.geoprocessing.env.workspace = gdbPath5
                fcList = arcpy.ListFeatureClasses()
                if name5 in fcList:
                    print destinations + " exists"
                else:
                    variable = destinations + " does not exist"
                    return 0, variable

            elif os.path.exists(destinations):
                print destinations + " exists"
            else:
                variable = destinations + " does not exist"
                return 0, variable

        if os.path.exists(costSurfaceTable):
            print costSurfaceTable + " exists"
        else:
            variable = costSurfaceTable + " does not exist"
            return 0, variable
        if os.path.exists(workspace):
            print workspace + " exists"
        else:
            variable = workspace + " does not exist"
            return 0, variable
        if timeCalculation.lower() == "roundtrip":
            if leastCostPath.lower() == "yes" :
                print "timeCalculation set to " + timeCalculation + " and leastCostPath is correctly set to " + leastCostPath
            else:
                variable = "If roundtrip calculation selected leastCostPath must be set to yes"
                return 0, variable
        else:
            print "Roundtrip Not Selected"
            pass

        arcpy.geoprocessing.env.workspace = workspace
        return 1, variable
    except:

        print "setupTest function failed"
        message = "setupTest function failed"
        return 0, message


