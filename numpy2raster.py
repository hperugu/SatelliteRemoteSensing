import numpy as np
from osgeo import gdal
from osgeo import gdal_array
from osgeo import osr
import matplotlib.pylab as plt
import h5py
import os

files = os.listdir("GAERO_VAOOO*")
for file in files:
  timeBFile = file.split("_")[3]
  f = h5py.File(file,'r')

  # My image array  
  array = np.array(f['All_Data']['VIIRS-Aeros-EDR_All']['AerosolOpticalDepth_at_550nm'])
  lat = np.array(f['All_Data']['VIIRS-Aeros-EDR-GEO_All']['Longitude'])
  lon = np.array(f['All_Data']['VIIRS-Aeros-EDR-GEO_All']['Longitude'])
  # For each pixel I know it's latitude and longitude.

  xmin,ymin,xmax,ymax = [lon.min(),lat.min(),lon.max(),lat.max()]
  nrows,ncols = np.shape(array)
  xres = (xmax-xmin)/float(ncols)
  yres = (ymax-ymin)/float(nrows)
  geotransform=(xmin,xres,0,ymax,0, -yres)   
  # That's (top left x, w-e pixel resolution, rotation (0 if North is up), 
  #         top left y, rotation (0 if North is up), n-s pixel resolution)
  # I don't know why rotation is in twice???

  output_raster = gdal.GetDriverByName('GTiff').Create(timeBFile+'.tif',ncols, nrows, 1 ,gdal.GDT_Float32)  # Open the file
  output_raster.SetGeoTransform(geotransform)  # Specify its coordinates
  srs = osr.SpatialReference() 
  srs.ImportFromEPSG(4326)                     # This one specifies WGS84 lat long.
  output_raster.SetProjection( srs.ExportToWkt() )   # Exports the coordinate system                                                   # to the file
  output_raster.GetRasterBand(1).WriteArray(array)   # Writes my array to the raster
  f.close()
