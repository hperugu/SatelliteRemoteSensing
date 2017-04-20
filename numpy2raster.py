import numpy as np
from osgeo import gdal
from osgeo import gdal_array
from osgeo import osr
import matplotlib.pylab as plt
import numpy.ma as ma
import h5py
import glob
import pdb

NoData_value = -9999
files = glob.glob('/aa/hperugu/NASA_SRSD/EDR_2015/GAERO*.h5')
domllx,domlly = [31.756,-124.02]
domurx,domury = [42.127,-116.76]
for file in files:
  timeBFile = file.split("_")[4]+'QF1'
  orbit = file.split("_")[5]
  try:f = h5py.File(file,'r')
  except: continue
  # My image array  
  array = np.array(f['All_Data']['VIIRS-Aeros-EDR_All']['AerosolOpticalDepth_at_550nm'])
  lat = np.array(f['All_Data']['VIIRS-Aeros-EDR-GEO_All']['Latitude'])
  lon = np.array(f['All_Data']['VIIRS-Aeros-EDR-GEO_All']['Longitude'])
  factor = np.array(f['All_Data']['VIIRS-Aeros-EDR_All']['AerosolOpticalDepthFactors'])
  qf1 = np.array(f['All_Data']['VIIRS-Aeros-EDR_All']['QF1_VIIRSAEROEDR'])
  qf_array = (qf1 > 16).astype(int)
  qf_mask = np.ma.masked_equal(qf_array,0)
  aot = array*factor[0] + factor[1]
  aot_mask = np.ma.masked_where(np.ma.getmask(qf_mask), aot)
  llx,urx = lat[0][0],lat[-1][-1]
  lly,ury = lon[0][0],lon[-1][-1]
  print ("llx: "+str(llx) +", urx: "+ str(urx)+", lly: "+ str(lly)+", ury: "+ str(ury))
  print "processing "+ timeBFile+"  "+orbit
  if  not (( llx> domllx) and (domurx <urx) and  ( abs(domlly) > abs(lly) ) and( abs(ury) > abs(domury)) ):
    print f
    continue
  # For each pixel's latitude and longitude.
  xmin,ymin,xmax,ymax = [lon.min(),lat.min(),lon.max(),lat.max()]
  nrows,ncols = np.shape(array)
  xres = (xmax-xmin)/float(ncols)
  yres = (ymax-ymin)/float(nrows)
  geotransform=(xmin,xres,0,ymax,0, -yres)   
  # That's (top left x, w-e pixel resolution, rotation (0 if North is up), 
  # top left y, rotation (0 if North is up), n-s pixel resolution)
  output_raster = gdal.GetDriverByName('GTiff').Create(timeBFile+'.tif',ncols, nrows, 1 ,gdal.GDT_Float32)  # Open the file
  output_raster.SetGeoTransform(geotransform)  # Specify its coordinates
  output_raster.GetRasterBand(1).WriteArray( aot ) 
  band = output_raster.GetRasterBand(1)
  band.SetNoDataValue(NoData_value)
  band.FlushCache() 
  srs = osr.SpatialReference() 
  srs.ImportFromEPSG(4326)                     # This one specifies WGS84 lat long.
  output_raster.SetProjection( srs.ExportToWkt() )   # Exports the coordinate system                                                   # to the file
  output_raster = None   # Writes my array to the raster
  f.close()
