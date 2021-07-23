# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 01:34:55 2021

@author: wb580236
"""

import pdb
from pyhdf.SD import SD, SDC
import pprint
import numpy as np

 

#### File paths
file_name = "C:\\Users\\wb580236\\OneDrive - WBG\\Documents\\Python Scripts\\MCD19A2.A2021137.h18v08.006.2021139045000.hdf"
lat_lon_file = ""
##### Get h and v numbers from file name
h = file_name.split('\\')[6].split('.')[2][1:3]
v = file_name.split('\\')[6].split('.')[2][5:7]
##### Get origin Lat/Lon  from the lat lon file
f = open(lat_lon_file,'r')
for line in f.readlines():
    if line[0:2] == h:
        i = int(v) *3 
        lat_0 = line[i+1:i+4]
        lon_0 = 0
        
file = SD(file_name, SDC.READ)
print (file.info())
pdb.set_trace()
#### To create numpy array of lat/lon values
lat_lon = np.linspace(lat_0,lat_0+1.2,1200)
datasets_dic = file.datasets()

#### Unwrap the data
for idx,sds in enumerate(datasets_dic.keys()):
    print (idx,sds)
sds_obj = file.select('Optical_Depth_055')
data = sds_obj.get()
for key, value in sds_obj.attributes().items():
    print( key, value )
    if key == 'add_offset':
        add_offset = value  
    if key == 'scale_factor':
        scale_factor = value

###### Get data values from the dataset

print( 'add_offset', add_offset, type(add_offset) )
print( 'scale_factor', scale_factor, type(scale_factor) )
data = (data - add_offset) * scale_factor
print( data )

#### Merge Lat lon and data

 
pdb.set_trace()