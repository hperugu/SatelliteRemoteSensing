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

import viirs_vi_products as viirsVI
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

def granuleFiles(totalGlob):
    '''
    Returns sorted lists of the geolocation and product files.
    '''
    prodDir = path.dirname(path.abspath(path.expanduser(totalGlob)))
    prodGlob = path.basename(path.abspath(path.expanduser(totalGlob)))

    geoPrefix = "GITCO"
    prodPrefix = "VIVIO"

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

        # Unscale the NDVI dataset
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

def geoTiff_NDVI(gridLat,gridLon,gridData,lat_0,lon_0,ModeGran):
    '''
    Plots the VIIRS Normalised Vegetation Index as raster
    '''
    tempfile= 'd20171024'
    xmin,ymin,xmax,ymax = [gridLon.min(),gridLat.min(),gridLon.max(),gridLat.max()]
    nrows,ncols = np.shape(gridData)
    xres = (xmax-xmin)/float(ncols)
    yres = (ymax-ymin)/float(nrows)
    geotransform = (xmin,xres,0,ymax,0, -yres)
    # That's (top left x, w-e pixel resolution, rotation (0 if North is up),top left y, rotation (0 if North is up), n-s pixel resolution)
    output_raster = gdal.GetDriverByName('GTiff').Create(tempfile+'.tif',ncols, nrows, 1 ,gdal.GDT_Float32)  # Open the file
           for fillType in trimObj.sdrTypeFill.keys() :
            if ndviFillMasks[fillType] is not None :
                fillMask = fillMask * ma.array(np.zeros(ndviArr.shape,dtype=np.bool),\
                    mask=ndviFillMasks[fillType])

        # Unscale the NDVI dataset
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

def geoTiff_NDVI(gridLat,gridLon,gridData,lat_0,lon_0,ModeGran):
    '''
    Plots the VIIRS Normalised Vegetation Index as raster
    '''
    tempfile= 'd20171024'
    xmin,ymin,xmax,ymax = [gridLon.min(),gridLat.min(),gridLon.max(),gridLat.max()]
    nrows,ncols = np.shape(gridData)
    xres = (xmax-xmin)/float(ncols)
    yres = (ymax-ymin)/float(nrows)
    geotransform = (xmin,xres,0,ymax,0, -yres)
    # That's (top left x, w-e pixel resolution, rotation (0 if North is up),top left y, rotation (0 if North is up), n-s pixel resolution)
    output_raster = gdal.GetDriverByName('GTiff').Create(tempfile+'.tif',ncols, nrows, 1 ,gdal.GDT_Float32)  # Open the file
        output_raster.GetRasterBand(1).WriteArray( gridData )
    band = output_raster.GetRasterBand(1)
    band.FlushCache()
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)                           # This one specifies WGS84 lat long.
    output_raster.SetProjection( srs.ExportToWkt() )   # Exports the coordinate system to the file
    #output_raster = None   # Writes my array to the raster

def main():
    ipProd = 'NDVI'
    stride = 1.0
    prodList = granuleFiles("/aa/hperugu/NASA_SRSD/EDR_test_split/GITCO-VIVIO_npp*")
    lats,lons,ndviData,gran_lat_0,gran_lon_0,ModeGran = gran_NDVI(prodList,prodName=ipProd,shrink=stride)
    lat_0 =  gran_lat_0
    lon_0 =  gran_lon_0
    geoTiff_NDVI(lats,lons,ndviData,ModeGran,lat_0,lon_0)

if __name__ == '__main__':
    main()




