
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

import viirs_aerosol_products_mod as viirsVI
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

    LOG.debug("Creating viirsAeroObj...")
    reload(viirsAero)
    viirsAeroObj = viirsAero.viirsAero()
    LOG.debug("done")

    # Determine the correct fillValue
    trimObj = ViirsTrimTable()
    eps = 1.e-6

    # Build up the swath...
    for grans in np.arange(len(aotList)):

        LOG.debug("\nIngesting granule {} ...".format(grans))
        retList = viirsAeroObj.ingest(aotList[grans],'aot',shrink,'linear')

        try :
            latArr  = np.vstack((latArr,viirsAeroObj.Lat[:,:]))
            lonArr  = np.vstack((lonArr,viirsAeroObj.Lon[:,:]))
            ModeGran = viirsAeroObj.ModeGran
            LOG.debug("subsequent geo arrays...")
        except NameError :
            latArr  = viirsAeroObj.Lat[:,:]
            lonArr  = viirsAeroObj.Lon[:,:]
            ModeGran = viirsAeroObj.ModeGran
            LOG.debug("first geo arrays...")

        try :
            aotArr  = np.vstack((aotArr ,viirsAeroObj.ViirsAProdSDS[:,:]))
            retArr  = np.vstack((retArr ,viirsAeroObj.ViirsAProdRet[:,:]))
            qualArr = np.vstack((qualArr,viirsAeroObj.ViirsCMquality[:,:]))
            #lsmArr  = np.vstack((lsmArr ,viirsAeroObj.LandSeaMask[:,:]))
            LOG.debug("subsequent aot arrays...")
        except NameError :
            aotArr  = viirsAeroObj.ViirsAProdSDS[:,:]
            retArr  = viirsAeroObj.ViirsAProdRet[:,:]
            qualArr = viirsAeroObj.ViirsCMquality[:,:]
            #lsmArr  = viirsAeroObj.LandSeaMask[:,:]
            LOG.debug("first aot arrays...")

        LOG.debug("Intermediate aotArr.shape = {}".format(str(aotArr.shape)))
        LOG.debug("Intermediate retArr.shape = {}".format(str(retArr.shape)))
        LOG.debug("Intermediate qualArr.shape = {}".format(str(qualArr.shape)))
        #LOG.debug("Intermediate lsmArr.shape = {}".format(str(lsmArr.shape)))

    lat_0 = latArr[np.shape(latArr)[0]/2,np.shape(latArr)[1]/2]
    lon_0 = lonArr[np.shape(lonArr)[0]/2,np.shape(lonArr)[1]/2]

    LOG.debug("lat_0,lon_0 = ",lat_0,lon_0)

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
                LOG.debug("Dataset was neither int not float... a worry")
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
            LOG.debug(">> error: Mask Error, probably mismatched geolocation and product array sizes, aborting...")
            sys.exit(1)

    except Exception, err :
        LOG.debug(">> error: {}...".format(str(err)))
        sys.exit(1)

    LOG.debug("gran_AOT ModeGran = ",ModeGran)

    return lats,lons,data,lat_0,lon_0,ModeGran
    
def geoTiff_AOT(gridLat,gridLon,gridData,lat_0,lon_0,ModeGran):
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
    ipProd = 'AOT'
    stride = 1.0
    prodList = granuleFiles("/aa/hperugu/NASA_SRSD/EDR_test_split/GITCO-VIVIO_npp*")
    lats,lons,ndviData,gran_lat_0,gran_lon_0,ModeGran = gran_NDVI(prodList,prodName=ipProd,shrink=stride)
    lat_0 =  gran_lat_0
    lon_0 =  gran_lon_0
    geoTiff_NDVI(lats,lons,ndviData,ModeGran,lat_0,lon_0)

if __name__ == '__main__':
    main()
