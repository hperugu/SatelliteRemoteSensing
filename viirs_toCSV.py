#!/usr/bin/env python
# encoding: utf-8
file_Date = '$Date: 2017-10-30 16:33:29  +0000 (Mon Oct 30 16:33:29 PDT 2017) $'
file_Revision = '$Revision: 001 $'
file_Author = '$Author: hperugu $'
file_HeadURL = '$HeadURL:  $'
file_Id = '$Id: h5_toraster.py 001 16:33:29  hperugu $'

__author__ = 'Harikishan Perugu <harikishen.perugu@gmail.com>'
__version__ = '$Id: h5_toraster.py 001 16:33:29  hperugu $'
__docformat__ = 'Epytext'

import viirs_aerosol_products_Modified as viirsAero
import viirs_vi_products_Modified as viirsVI
import tables as pytables
from tables import exceptions as pyEx
import pdb
from os import path,uname
import string,sys,traceback
from glob import glob
import numpy as np
from ViirsData import ViirsTrimTable
from  numpy import ma as ma
#import viirs_edr_data
from osgeo import gdal
from osgeo import osr
import matplotlib.pyplot as plt
from datetime import datetime
def granuleFiles(totalGlob,geo,prod):
    '''
    Returns sorted lists of the geolocation and product files.
    '''
    prodDir = path.dirname(path.abspath(path.expanduser(totalGlob)))
    prodGlob = path.basename(path.abspath(path.expanduser(totalGlob)))

    geoPrefix = geo
    prodPrefix = prod

    prodList_in = glob("%s/%s" % (prodDir,prodGlob))
    prodList_in.sort()
    
    prodList = []
    for files in prodList_in :
        prod_arr = string.split(path.basename(files),"_")
        dateStamp = prod_arr[2]
        timeStamp = prod_arr[3]
        geoFileGlob="%s/%s-%s*%s_%s*.h5" % (prodDir,geoPrefix,prodPrefix,dateStamp,timeStamp)
        geoFile = glob("%s/%s-%s*%s_%s*.h5" % (prodDir,geoPrefix,prodPrefix,dateStamp,timeStamp))
        if (np.shape(geoFile)[0] != 0) :
            #geoList.append(geoFile[0])
            prodList.append(files)
    return prodList
    
def gran_AOT(aotList,shrink=1):
    '''
    Returns the granulated AOT
    '''

    try :
        reload(viirsAero)
        reload(viirs_edr_data)
        del(viirsAeroObj)
        del(latArr)
        del(lonArr)
        del(aotArr)
        del(retArr)
        del(qualArr)
        del(lsmArr)
    except :
        pass

    #print("Creating viirsAeroObj...")
    reload(viirsAero)
    viirsAeroObj = viirsAero.viirsAero()
    #print("done")

    # Determine the correct fillValue
    trimObj = ViirsTrimTable()
    eps = 1.e-6

    # Build up the swath...
    for grans in np.arange(len(aotList)):

        #print("\nIngesting granule {} ...".format(grans))
        retList = viirsAeroObj.ingest(aotList[grans],'aot',shrink,'linear')
        try :
            latArr  = np.vstack((latArr,viirsAeroObj.Lat[:,:]))
            lonArr  = np.vstack((lonArr,viirsAeroObj.Lon[:,:]))
            #ModeGran = viirsAeroObj.ModeGran
            #print("subsequent geo arrays...")
        except NameError :
            latArr  = viirsAeroObj.Lat[:,:]
            lonArr  = viirsAeroObj.Lon[:,:]
            #ModeGran = viirsAeroObj.ModeGran
            #print("first geo arrays...")

        try :
            aotArr  = np.vstack((aotArr ,viirsAeroObj.ViirsAProdSDS[:,:]))
            retArr  = np.vstack((retArr ,viirsAeroObj.ViirsAProdRet[:,:]))
            qualArr = np.vstack((qualArr,viirsAeroObj.ViirsCMquality[:,:]))
            #lsmArr  = np.vstack((lsmArr ,viirsAeroObj.LandSeaMask[:,:]))
            #print("subsequent aot arrays...")
        except NameError :
            aotArr  = viirsAeroObj.ViirsAProdSDS[:,:]
            retArr  = viirsAeroObj.ViirsAProdRet[:,:]
            qualArr = viirsAeroObj.ViirsCMquality[:,:]
        #print("Intermediate aotArr.shape = {}".format(str(aotArr.shape)))
        #print("Intermediate retArr.shape = {}".format(str(retArr.shape)))
        #print("Intermediate qualArr.shape = {}".format(str(qualArr.shape)))
        #print("Intermediate lsmArr.shape = {}".format(str(lsmArr.shape)))

    lat_0 = latArr[np.shape(latArr)[0]/2,np.shape(latArr)[1]/2]
    lon_0 = lonArr[np.shape(lonArr)[0]/2,np.shape(lonArr)[1]/2]

    #print("lat_0,lon_0 = ",lat_0,lon_0)

    try :
        # Determine masks for each fill type, for the VCM IP
        aotFillMasks = {}
        for fillType in trimObj.sdrTypeFill.keys() :
            fillValue = trimObj.sdrTypeFill[fillType][aotArr.dtype.name]
            if 'float' in fillValue.__class__.__name__ :
                aotFillMasks[fillType] = ma.masked_inside(aotArr,fillValue-eps,fillValue+eps).mask
                if (aotFillMasks[fillType].__class__.__name__ != 'ndarray') :
                    aotFillMasks[fillType] = None
            elif 'int' in fillValue.__class__.__name__ :
                aotFillMasks[fillType] = ma.masked_equal(aotArr,fillValue).mask
                if (aotFillMasks[fillType].__class__.__name__ != 'ndarray') :
                    aotFillMasks[fillType] = None
            else :
                #print("Dataset was neither int not float... a worry")
                pass

        # Construct the total mask from all of the various fill values
        fillMask = ma.array(np.zeros(aotArr.shape,dtype=np.bool))
        for fillType in trimObj.sdrTypeFill.keys() :
            if aotFillMasks[fillType] is not None :
                fillMask = fillMask * ma.array(np.zeros(aotArr.shape,dtype=np.bool),\
                    mask=aotFillMasks[fillType])

        # Define any masks based on the quality flags...
        ViirsCMqualityMask = ma.masked_equal(qualArr,0)     # VCM quality == poor
        ViirsAProdRetMask  = ma.masked_not_equal(retArr,0)  # Interp/NAAPS/Climo

        # Define the land and water masks
        #ViirsLandMask      = ma.masked_greater(lsmArr,1)
        #ViirsWaterMask     = ma.masked_less(lsmArr,2)

        # Define the total mask
        totalMask = fillMask * ViirsCMqualityMask * ViirsAProdRetMask

        try :
            data = ma.array(aotArr,mask=totalMask.mask)
            lats = ma.array(latArr,mask=totalMask.mask)
            lons = ma.array(lonArr,mask=totalMask.mask)
        except ma.core.MaskError :
            #print(">> error: Mask Error, probably mismatched geolocation and product array sizes, aborting...")
            sys.exit(1)

    except Exception, err :
        #print(">> error: {}...".format(str(err)))
        sys.exit(1)

    #print("gran_AOT ModeGran = ",ModeGran)

    #return lats,lons,data,lat_0,lon_0,ModeGran
    return lats,lons,data,lat_0,lon_0



def gran_NDVI(ndviList,prodName='NDVI',shrink=1):
    '''
    Returns the granulated NDVI
    '''
    try :
        reload(viirsVI)
        reload(viirs_edr_data)
        del(viirsVIObj)
        del(latArr)
        del(lonArr)
        del(ndviArr)
        #del(qf2Arr)
    except :
        pass
    reload(viirsVI)
    viirsVIObj = viirsVI.viirsVI()

    # Determine the correct fillValue
    trimObj = ViirsTrimTable()
    # Build up the swath...
    for grans in np.arange(len(ndviList)):
        retList = viirsVIObj.ingest(ndviList[grans],prodName,shrink)
        
        try :
            latArr  = np.vstack((latArr,viirsVIObj.Lat[:,:]))
            lonArr  = np.vstack((lonArr,viirsVIObj.Lon[:,:]))
            ModeGran = viirsVIObj.ModeGran

        except NameError :
            latArr  = viirsVIObj.Lat[:,:]
            lonArr  = viirsVIObj.Lon[:,:]
            ModeGran = viirsVIObj.ModeGran

        try :
            ndviArr  = np.vstack((ndviArr ,viirsVIObj.ViirsVIprodSDS[:,:]))
            #qf1Arr = np.vstack((qf1Arr,viirsVIObj.ViirsVI_QF1[:,:]))
            qf2Arr = np.vstack((qf2Arr,viirsVIObj.ViirsVI_QF2[:,:]))
            #qf3Arr = np.vstack((qf3Arr,viirsVIObj.ViirsVI_QF3[:,:]))

        except NameError :
            ndviArr  = viirsVIObj.ViirsVIprodSDS[:,:]
            #qf1Arr = viirsVIObj.ViirsVI_QF1[:,:]
            qf2Arr = viirsVIObj.ViirsVI_QF2[:,:]
            #qf3Arr = viirsVIObj.ViirsVI_QF3[:,:]

    lat_0 = latArr[np.shape(latArr)[0]/2,np.shape(latArr)[1]/2]
    lon_0 = lonArr[np.shape(lonArr)[0]/2,np.shape(lonArr)[1]/2]


    try :
        #Determine masks for each fill type, for the NDVI EDR
        ndviFillMasks = {}
        for fillType in trimObj.sdrTypeFill.keys() :
            fillValue = trimObj.sdrTypeFill[fillType][ndviArr.dtype.name]
            if 'float' in fillValue.__class__.__name__ :
                ndviFillMasks[fillType] = ma.masked_inside(ndviArr,fillValue-eps,fillValue+eps).mask
                if (ndviFillMasks[fillType].__class__.__name__ != 'ndarray') :
                    ndviFillMasks[fillType] = None
            elif 'int' in fillValue.__class__.__name__ :
                ndviFillMasks[fillType] = ma.masked_equal(ndviArr,fillValue).mask
                if (ndviFillMasks[fillType].__class__.__name__ != 'ndarray') :
                    ndviFillMasks[fillType] = None
            else :
                print("Dataset was neither int not float... a worry")
                pass

        #Construct the total mask from all of the various fill values
        fillMask = ma.array(np.zeros(ndviArr.shape,dtype=np.bool))
        for fillType in trimObj.sdrTypeFill.keys() :
            if ndviFillMasks[fillType] is not None :
                fillMask = fillMask * ma.array(np.zeros(ndviArr.shape,dtype=np.bool),\
                    mask=ndviFillMasks[fillType])

        # UnsCalife the NDVI dataset
        ndviArr =  ndviArr * viirsVIObj.viFactors[0] + viirsVIObj.viFactors[1]

        # Define some masks...
        #fillMask = ma.masked_less(ndviArr,-800.).mask
        
        VIlandWaterFlag = np.bitwise_and(qf2Arr[:,:],7) >> 0
        VIlandWaterMask = ma.masked_greater(VIlandWaterFlag,1).mask

        VIcldConfFlag = np.bitwise_and(qf2Arr[:,:],24) >> 3
        VIcldConfMask = ma.masked_not_equal(VIcldConfFlag,0).mask

        #NDVIqualFlag = np.bitwise_and(qf1Arr,3) >> 0
        #ndviQualMask = ma.masked_equal(NDVIqualFlag,0).mask

        # Combine the fill mask and quality masks...
        #totalMask = fillMask.mask
        totalMask = fillMask.mask + VIlandWaterMask + VIcldConfMask
        #totalMask = fillMask.mask + ndviQualMask
        #totalMask = np.zeros(ndviArr.shape,dtype=np.bool)

        try :
            data = ma.array(ndviArr,mask=totalMask)
            lats = ma.array(latArr,mask=totalMask)
            lons = ma.array(lonArr,mask=totalMask)
        except ma.core.MaskError :
            print(">> error: Mask Error, probably mismatched geolocation and product array sizes, aborting...")
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)

    except Exception, err :
        print(">> error: {}...".format(str(err)))
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

    print("gran_NDVI ModeGran = ",ModeGran)

    return lats,lons,data,lat_0,lon_0,ModeGran

def csv_file(gridLat,gridLon,gridData,lat_0,lon_0,ModeGran,var,filename):
    '''
    Plots the VIIRS Normalised Vegetation Index as raster
    '''
    Calif_ll_lat,Calif_ll_lon,Calif_ur_lat,Calif_ur_lon = [31.76,-124.02,42.13,-116.76]
    tempfile= '/aa/hperugu/NASA_SRSD/EDR_2015_'+var+'_csv/'+filename+'.csv'
    nrows,ncols = np.shape(gridData)
    with open(tempfile,'w') as f:
        f.write("longitude,latitude,"+var+"\n")
        for row in xrange(0,nrows):
            for col in xrange(0,ncols):
                if not gridLon[row][col] is ma.masked:
                    if  (Calif_ll_lon <gridLon[row][col]<Calif_ur_lon) and (Calif_ll_lat <gridLat[row][col]<Calif_ur_lat):
                        f.write(str(gridLon[row][col])+","+str(gridLat[row][col])+","+str(gridData[row][col])+'\n')


  
def geoTiff_NDV(gridLat,gridLon,gridData,lat_0,lon_0,ModeGran):
    #Big problem with raster creation
    #need reformatting of lat,lon and data
    xmin,ymin,xmax,ymax = [gridLon.min(),gridLat.min(),gridLon.max(),gridLat.max()]
    nrows,ncols = np.shape(gridData)
    xres = (xmax-xmin)/float(ncols)
    yres = (ymax-ymin)/float(nrows)
    geotransform = (xmin,xres,1,ymin,0, -yres)   
    # That's (top left x, w-e pixel resolution, rotation (0 if North is up),top left y, rotation (0 if North is up), n-s pixel resolution)
    output_raster = gdal.GetDriverByName('GTiff').Create(tempfile+'.tif',ncols, nrows, 1 ,gdal.GDT_Float32)  # Open the file
    output_raster.SetGeoTransform(geotransform)  # Specify its coordinates
    output_raster.GetRasterBand(1).WriteArray( gridData ) 
    band = output_raster.GetRasterBand(1)
    band.FlushCache() 
    srs = osr.SpatialReference() 
    srs.ImportFromEPSG(4326)                           # This one specifies WGS84 lat long.
    output_raster.SetProjection( srs.ExportToWkt() )   # Exports the coordinate system to the file
    #output_raster = None   # Writes my array to the raster
 
def gran_AOT_EDR(aotList,shrink=1):
    '''
    Returns the granulated AOT EDR
    '''

    try :
        reload(viirsAero)
        reload(viirs_edr_data)
        del(viirsAeroObj)
        del(latArr)
        del(lonArr)
        del(aotArr)
        del(retArr)
        del(qualArr)
        del(lsmArr)
        del(newData)
        del(dataIdx)
    except :
        pass

    print("Creating viirsAeroObj...")
    reload(viirsAero)
    viirsAeroObj = viirsAero.viirsAero()
    print("done")

    # Determine the correct fillValue
    trimObj = ViirsTrimTable()
    eps = 1.e-6

    # Build up the swath...
    for grans in np.arange(len(aotList)):

        print("Ingesting EDR granule {} ...".format(grans))

        # Read in geolocation...
        ViirsGeoFileName = aotList[grans]
        print("Geo file name: {}".format(ViirsGeoFileName))

        try :
            ViirsGeoFileObj = pytables.open_file(ViirsGeoFileName,mode='r')
            #ViirsGeoFileObj = pytables.open_file(ViirsGeoFileName,mode='r')
            print("Successfully opened geolocation file",ViirsGeoFileName)
        except IOError :
            print(">> error: Could not open geolocation file: ",ViirsGeoFileName)
            sys.exit(1)

        # Detemine the geolocation group name and related information
        #group = getobj(ViirsGeoFileObj,'/All_Data')
        group = ViirsGeoFileObj.get_node('/All_Data')
        #geoGroupName = '/All_Data/'+group.__members__[0]
        geoGroupName = '/All_Data/VIIRS-Aeros-EDR-GEO_All'
        group._g_close()
        print("Geolocation Group : {} ".format(geoGroupName))
        isEdrGeo = ('VIIRS-Aeros-EDR-GEO_All' in geoGroupName)
        if not isEdrGeo :
            print(">> error: {} is not an EDR resolution aerosol geolocation file\n\taborting...".format(ViirsGeoFileName))
            sys.exit(1)

        # Determine if this is a day/night/both granule
        try:
            dataNode = ViirsGeoFileObj.get_node('/Data_Products/VIIRS-Aeros-EDR-GEO/VIIRS-Aeros-EDR-GEO_Gran_0')
            dayNightFlag = np.squeeze(dataNode.attrs['N_Day_Night_Flag'])
        except Exception, err :
            print(">> error: {}...".format(str(err)))
            dataNode.close()

        # Get the geolocation Latitude and Longitude nodes...
        try :
            dataName = 'Latitude'
            geoLatNode = ViirsGeoFileObj.get_node(geoGroupName+'/'+dataName)
            print("Shape of {} node is {}".format(geoGroupName+'/'+dataName,repr(geoLatNode.shape)))
            dataName = 'Longitude'
            geoLonNode = ViirsGeoFileObj.get_node(geoGroupName+'/'+dataName)
            print("Shape of {} node is {}".format(geoGroupName+'/'+dataName,repr(geoLonNode.shape)))
            dataName = 'SolarZenithAngle'
            geoSzaNode = ViirsGeoFileObj.get_node(geoGroupName+'/'+dataName)
            print("Shape of {} node is {}".format(geoGroupName+'/'+dataName,repr(geoSzaNode.shape)))
        except pyEx.NoSuchNodeError :
            print("\n>> error: No required node {}/{} in {}\n\taborting...".format(geoGroupName,dataName,ViirsGeoFileName))
            ViirsGeoFileObj.close()
            sys.exit(1)

        # Make a copy of the geolocation node data, so we can close the file
        try :
            dataName = 'Latitude'
            print("Reading {} dataset...".format(dataName))
            latArr = np.vstack((latArr,geoLatNode[:,:]))
            geoLatNode.close()
            latArr = np.squeeze(latArr)
            print("done")
            dataName = 'Longitude'
            print("Reading {} dataset...".format(dataName))
            lonArr = np.vstack((lonArr,geoLonNode[:,:]))
            geoLonNode.close()
            lonArr = np.squeeze(lonArr)
            print("done")
            dataName = 'SolarZenithAngle'
            print("Reading {} dataset...".format(dataName))
            szaArr = np.vstack((szaArr,geoSzaNode[:,:]))
            geoSzaNode.close()
            szaArr = np.squeeze(szaArr)
            print("done")
            print("Closing geolocation file")
            ViirsGeoFileObj.close()
        except NameError :
            latArr = geoLatNode[:,:]
            lonArr = geoLonNode[:,:]
            szaArr = geoSzaNode[:,:]
            geoLatNode.close()
            geoLonNode.close()
            geoSzaNode.close()
            ViirsGeoFileObj.close()
        #except :
            #print("\n>> error: Could not retrieve %/% node data in {}\n\taborting...".format(geoGroupName,dataName,ViirsGeoFileName))
            #geoLatNode.close()
            #geoLonNode.close()
            #geoSzaNode.close()
            #ViirsGeoFileObj.close()
            #sys.exit(1)

        
        # Try to determine if this is a day or night granule. Night will be determined
        # to be a SZA greater than 85 degrees.

        if vars().has_key('dayNightFlag'):
            if dayNightFlag=='Day':
                ModeGran = 1
            if dayNightFlag=='Night':
                ModeGran = 0
            if dayNightFlag=='Both':
                ModeGran = 2
            print("ModeGran = {}".format(ModeGran))
        else :
            szaMask = ma.masked_less(szaArr,85.).mask
            dayFraction = float(szaMask.sum())/float(szaArr.size)
            print("Day Fraction = {}".format(dayFraction))
            ModeGran = 2 # Default to a mixed day/night granule
            if dayFraction == 1.00 : ModeGran = 1
            if dayFraction == 0.00 : ModeGran = 0
            print("ModeGran = {}".format(ModeGran))

        # Read in dataSets...
        ViirsEDRFileName = aotList[grans]

        try :
            ViirsEDRFileObj = pytables.open_file(ViirsEDRFileName,mode='r')
            print("Successfully opened edr file",ViirsEDRFileName)
        except IOError :
            print(">> error: Could not open edr file: ",ViirsEDRFileName)
            sys.exit(1)

        # Detemine the edr group name and related information
        #group = getobj(ViirsEDRFileObj,'/All_Data')
        group = ViirsEDRFileObj.get_node('/All_Data')
        edrGroupName = '/All_Data/'+group.__members__[0]
        group._g_close()
        print("Edr Group : {} ".format(edrGroupName))
        isEdr = ('VIIRS-Aeros-EDR_All' in edrGroupName)
        if not isEdr :
            print(">> error: {} is not an EDR resolution aerosol file\n\taborting...".format(ViirsEDRFileName))
            sys.exit(1)

        # Get the edr nodes...
        try :
            dataName = 'AerosolOpticalDepth_at_550nm'
            aot550Node = ViirsEDRFileObj.get_node(edrGroupName+'/'+dataName)
            print("Shape of {} node is {}".format(edrGroupName+'/'+dataName,repr(aot550Node.shape)))
            dataName = 'AerosolOpticalDepthFactors'
            aotFactorsNode = ViirsEDRFileObj.get_node(edrGroupName+'/'+dataName)
            print("Shape of {} node is {}".format(edrGroupName+'/'+dataName,repr(aotFactorsNode.shape)))
        except pyEx.NoSuchNodeError :
            print("\n>> error: No required node {}/{} in {}\n\taborting...".format(edrGroupName,dataName,ViirsEDRFileName))
            ViirsEDRFileObj.close()
            sys.exit(1)

        # Make a copy of the edr node data, so we can close the file
        try :
            dataName = 'AerosolOpticalDepth_at_550nm'
            print("Reading {} dataset...".format(dataName))
            aot550 = np.vstack((aot550,aot550Node[:,:]))
            aot550 = np.squeeze(aot550)
            aot550Node.close()
            print("done")
            dataName = 'AerosolOpticalDepthFactors'
            print("Reading {} dataset...".format(dataName))
            aotFactors = aotFactorsNode[:]
            aotFactors = np.squeeze(aotFactors)
            aotFactorsNode.close()
            print("done")
            print("Closing edr file")
            ViirsEDRFileObj.close()

            print("Shape of aot550 is {}".format(repr(np.shape(aot550))))
            print("Shape of latsArr is {}".format(repr(np.shape(latArr))))
            print("Shape of lonsArr is {}".format(repr(np.shape(lonArr))))

        except NameError :
            aot550 = aot550Node[:,:]
            aotFactors = aotFactorsNode[:]
            aot550Node.close()
            aotFactorsNode.close()
            ViirsEDRFileObj.close()

        #except :
            #print("\n>> error: Could not retrieve %/% node data in {}\n\taborting...".format(edrGroupName,dataName,ViirsEDRFileName))
            #aot550Node.close()
            #aotFactorsNode.close()
            #ViirsEDRFileObj.close()
            #sys.exit(1)
        
        print("Creating some masks")
        try :
            
            lat_0 = latArr[np.shape(latArr)[0]/2,np.shape(latArr)[1]/2]
            lon_0 = lonArr[np.shape(lonArr)[0]/2,np.shape(lonArr)[1]/2]

            badGeo = False
            if not (-90. <= lat_0 <= 90.) :
                print("\n>> error: Latitude of granule midpoint ({}) does not satisfy (-90. <= lat_0 <= 90.)\nfor file {}\n\taborting...".format(lat_0,geoList[grans]))
                badGeo = True
            if not (-180. <= lat_0 <= 180.) :
                print("\n>> error: Longitude of granule midpoint ({}) does not satisfy (-180. <= lon_0 <= 180.)\nfor file {}\n\taborting...".format(lon_0,geoList[grans]))
                badGeo = True

            if badGeo :
                sys.exit(1)

            aotArr  = aot550[:,:]

            # Determine masks for each fill type, for the AOT EDR
            aotFillMasks = {}
            for fillType in trimObj.sdrTypeFill.keys() :
                fillValue = trimObj.sdrTypeFill[fillType][aotArr.dtype.name]
                if 'float' in fillValue.__class__.__name__ :
                    aotFillMasks[fillType] = ma.masked_inside(aotArr,fillValue-eps,fillValue+eps).mask
                    if (aotFillMasks[fillType].__class__.__name__ != 'ndarray') :
                        aotFillMasks[fillType] = None
                elif 'int' in fillValue.__class__.__name__ :
                    aotFillMasks[fillType] = ma.masked_equal(aotArr,fillValue).mask
                    if (aotFillMasks[fillType].__class__.__name__ != 'ndarray') :
                        aotFillMasks[fillType] = None
                else :
                    print("Dataset was neither int not float... a worry")
                    pass

            # Construct the total mask from all of the various fill values
            totalMask = ma.array(np.zeros(aotArr.shape,dtype=np.bool))
            for fillType in trimObj.sdrTypeFill.keys() :
                if aotFillMasks[fillType] is not None :
                    totalMask = totalMask * ma.array(np.zeros(aotArr.shape,dtype=np.bool),\
                        mask=aotFillMasks[fillType])

            try :
                data = ma.array(aotArr,mask=totalMask.mask)
                lats = ma.array(latArr,mask=totalMask.mask)
                lons = ma.array(lonArr,mask=totalMask.mask)
            except ma.core.MaskError :
                print(">> error: Mask Error, probably mismatched geolocation and product array sizes, aborting...")
                sys.exit(1)

            data = data * aotFactors[0] + aotFactors[1]

        except :
            print(">> error: There was an exception...")
            sys.exit(1)

    print("lat_0,lon_0 = {},{}".format(lat_0,lon_0))
    print("Shape of data is {}".format(repr(np.shape(data))))
    print("Shape of lats is {}".format(repr(np.shape(lats))))
    print("Shape of lons is {}".format(repr(np.shape(lons))))
    return lats,lons,data,lat_0,lon_0,ModeGran

def main():
    #ipProd = 'NDVI'
    ipProd = 'AOT'
    stride = 1
    strtTime = datetime.now()
    for jday in xrange(2015217,2015274):
        jday = str(jday)
        date = datetime.strptime(jday,"%Y%j").strftime('%Y%m%d')
        filename = 'd'+str(date)
        prodList = granuleFiles("/share/tornado/bb/hperugu/NASA_EDR/GAERO-VAOOO_npp_"+filename+"*","GAERO","VAOOO")
        #prodList = granuleFiles("/share/tornado/aa/hperugu/NASA_EDR_NDVI/GITCO-VIVIO_npp_"+filename+"*")
        lats,lons,Data,gran_lat_0,gran_lon_0,ModeGran = gran_AOT_EDR(prodList,shrink=stride)
        #lats,lons,ndviData,gran_lat_0,gran_lon_0,ModeGran = gran_NDVI(prodList,prodName=ipProd,shrink=stride)
        lat_0 =  gran_lat_0 
        lon_0 =  gran_lon_0 
        csv_file(lats,lons,Data,lat_0,lon_0,ModeGran,ipProd,filename)
        endTime = datetime.now()
        print ("Time taken for a day is :"+str(endTime-strtTime))
        #geoTiff_NDVI(lats,lons,ndviData,lat_0,lon_0,ModeGran)
    
if __name__ == '__main__':
    main()
