#!/usr/bin/python
from netCDF4 import Dataset
import os,sys,pdb
import numpy as np
import subprocess
import gzip

#Read hourly grid level temperature from CALMET *.DAT file
def read_CALMET(grid_expand,DatFile):
    print "Reading CALMET file"+DatFile
    with gzip.open(DatFile,'rb') as inf:
        inf.readline()
        n = 0
        for line in inf:
            if line[0:7] =='       ':
                vals = line.split()
                sthr = int(vals[1] ) -1
                #print "Reading hour %i "%sthr
                inum = 0
                jnum = 0
            else:
                vals = line.split()
                num = len(vals)
                for n in range(0,num,2):
                    temp = (float(vals[n]) + 459.67) * 5/9
                    if inum ==321:
                        inum = 0
                        jnum += 1
                    grid_expand[sthr,0,jnum,inum] = temp
                    inum += 1
    grid_expand[24,:,:,:] = grid_expand[0,:,:,:]
    return grid_expand
    
# Read Hourly County Avergae Temprature from CSV file
def read_CntyAvg(grid_expand,cntyFile):
    with open('Fresno_temp.csv','r') as inf:
        for line in inf.readlines()[1:]:
            hr,month,gai,temp,rhum = line.split(",")
            hr = int(hr)-1
            temp = float(temp)
            if gai == gaiReq:
                cntTemp[hr]= (temp  + 459.67) * 5/9
                #cntTemp[hr]= temp  
        cntTemp[24] = cntTemp[0]

    county = Dataset('cty_surr_321x291.ncf','r')
    for cty in county.variables:
        cnum = cty.replace("c","")
        if cnum == cntyReq:
            for hr in cntTemp:
                countyFrac = np.around(county.variables[cty][:,0,:,:])
                grid_expand[hr] = countyFrac * cntTemp[hr]
                grid_expand[hr][grid_expand[hr]==0] = 258.15

def write_netCDF(Filled_grid,outfile,sdate):
    print "writing NetCDF File"+ outfile
    #Writing Temperature
    [cdate,sdate,ctime]=[2016178,sdate,162100]
    rootgrp = Dataset(outfile, 'w',format='NETCDF3_CLASSIC')
    #Dimension Definitions
    TSTEP = rootgrp.createDimension('TSTEP', None)
    DATE_TIME = rootgrp.createDimension('DATE-TIME', 2)
    LAY = rootgrp.createDimension('LAY', 1)
    VAR = rootgrp.createDimension('VAR', 1) #50
    ROW = rootgrp.createDimension('ROW',291)
    COL = rootgrp.createDimension('COL',321)
    #Variable and Attribute Definitions
    TFLAG=rootgrp.createVariable('TFLAG','i4',('TSTEP','VAR','DATE-TIME',),zlib=True) #zlib=True for Compressed.
    #Attribute Definitions
    TFLAG.units='<YYYYDDD,HHMMSS>'
    TFLAG.long_name='TFLAG           '
    TFLAG.var_desc='Timestep-valid flags:  (1) YYYYDDD or (2) HHMMSS                                '
    #Remaining variables and attribute definitions
    temp= rootgrp.createVariable('TEMP2','f4',('TSTEP','LAY','ROW','COL'),zlib=True)
    temp.long_name='TEMP2           '
    temp.units    ='K               '
    temp.var_desc ='temperature at 2 m                                                              '
    #Global attributes
    rootgrp.IOAPI_VERSION = "$Id: @(#) ioapi library version 3.0 $                                           " ;
    rootgrp.EXEC_ID = "????????????????                                                                " ;
    rootgrp.FTYPE = 1 ;
    rootgrp.CDATE = cdate;#2013137 ; 
    rootgrp.CTIME = ctime;#50126 ;
    rootgrp.WDATE = cdate;#2013137 ;
    rootgrp.WTIME = ctime;#50126 ;
    rootgrp.SDATE = sdate;#2010091 ;
    rootgrp.STIME = 80000 ; 
    rootgrp.TSTEP = 10000 ;
    rootgrp.NTHIK = 1 ;
    rootgrp.NCOLS = 321 ;
    rootgrp.NROWS = 291 ;
    rootgrp.NLAYS = 1 ;
    rootgrp.NVARS = 1 ; 
    rootgrp.GDTYP = 2 ;
    rootgrp.P_ALP = 30. ;
    rootgrp.P_BET = 60. ; 
    rootgrp.P_GAM = -120.5 ;
    rootgrp.XCENT = -120.5 ;
    rootgrp.YCENT = 37. ;
    rootgrp.XORIG = -684000. ; 
    rootgrp.YORIG = -564000. ;
    rootgrp.XCELL = 4000. ;
    rootgrp.YCELL = 4000. ;
    rootgrp.VGTYP = 7 ;
    rootgrp.VGTOP = 10000. ;
    rootgrp.VGLVLS = [1., 0.9958];
    rootgrp.GDNAM = 'METCRO_State_321' ;
    rootgrp.UPNAM = 'M3XTRACT        ' ;
    rootgrp.VAR_LIST= 'TEMP2           ';
    rootgrp.HISTORY= '';
    rootgrp.FILEDESC= '';
    #Writing TFLAG
    time=np.ones((25,1,2),dtype=np.int32)
    for hr in range(0,25):
        if hr > 16:
            nhr = hr -17
            nsdate = sdate +1
        else:
            nhr = hr+7
            nsdate = sdate
        time[hr,:,0]=time[hr,:,0]*nsdate
        time[hr,:,1]=time[hr,:,1]*nhr*10000
     
    rootgrp.variables['TFLAG'][:]=time
    #Writing Temperature
    rootgrp.variables['TEMP2'][:,0,:,:]=Filled_grid
    rootgrp.close()
def main():
    cntTemp = {}
    cntyReq = '10'
    gaiReq = '48'
    grid_expand = np.zeros((25,1,291,321),dtype=float)
    for mm in ['07']:
    #for mm in ['01','07']:
        for dd in range(1,31):
            if mm == '01':
                jday0 = 2012000
            else:
                jday0 = 2012182
            try:
                DatFile = '/aa/hperugu/SMOKE_EMFAC/inputs/temperature/2012-'+mm+'-'+str(dd).zfill(2)+'.dtim.gz'
                Filled_grid = read_CALMET(grid_expand,DatFile)
                jday = jday0 + dd
                outfile = '/aa/hperugu/SMOKE_EMFAC/outputs/METCRO2D_'+str(jday)+'.nc'
                write_netCDF(Filled_grid,outfile,jday)
                subprocess.call(["ncrename", "-h", "-O","-a", "VAR_LIST,VAR-LIST",outfile])
                print "finished writing ",outfile
            except:
                print (DatFile+" not found")
                continue


if __name__ == "__main__":
        main()
