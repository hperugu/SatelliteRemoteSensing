import numpy as np
import sys
import os
import pdb

def scc_total(filenames,n):
#input file format:meds
#output file format:standard qa report 
##AGTYPE,YEAR,MM,JDAY,DOW,BASIN,CYID,EICSUM,POL,UNIT,EMS
  #dowf={2:5/7.,5:1/7.,6:1/7.} #0=mon, 1= tue, 2=wed... 5=sat, 6=sun   only wed, sat, sun for now
  ems_dict={};bas_cty_scc_lst={};h_pos={}
  headcnt=0
  fin=open(filenames[0],'r')
  infname=os.path.basename(filenames[0])
  name_parts=infname.split('.')
  yyyy=name_parts[datepos][0:4]
  fmt='%Y%j' #format of time YYYYjjj  year and julian date
  dowk_mm_dict={}
  ems={};fcnt=0
  for file in filenames:
        ems_dict={}
        fin=os.popen('zcat -f %s' % file,'r')  #fin=open(file,'r')
        medsfile=os.path.basename(file)
        date=os.path.basename(file).split('.')[datepos]
        [jday,mm,dowk]=finddowk.get_dates(medsfile,byear)
        for line in fin.readlines():  # for line in fin.readlines()[headcnt:]: #skips linesopen(file,'r')
                hre=line[65:67].strip()
                i=line[i:j].strip()
                j=line[i:j].strip()
                cyid=line[56:58].strip()
                basin="NA"
                try: ems['CO']=float(line[78:88])
                except ValueError: ems['CO']=0.0
                try: ems['NOX']=float(line[88:98])
                except ValueError: ems['NOX']=0.0
                try: ems['SOX']=float(line[98:108])
                except ValueError: ems['SOX']=0.0
                try: ems['TOG']=float(line[108:118])
                except ValueError: ems['TOG']=0.0
                try: ems['PM']=float(line[118:128])
                except ValueError: ems['PM']=0.0
                try: ems['NH3']=float(line[128:138])
                except ValueError: ems['NH3']=0.0
                except: ems_dict[(cyid,i,j,pol,hre)]=ems[pol]#*dowf[dayofwk]
        [jday,mm,dowk]=finddowk.get_dates(medsfile,byear)
        fcnt+=1
        fin.close()
  return ems_dict,outfname
ncols=321;nrows=291
def load_hourly_ij(infile):
        grid_dict={}
        pol_lst=['CO','NOX','SOX','TOG','PM']
        try:
                fin=os.popen("zcat -f "+infile,'r') # fin=open(infile,'r')
        except:
                sys.stderr.write("\n*\nERROR: Could not open file '"+infile+"'\n*\n")
                sys.exit()
        for p in pol_lst:
                grid_dict[p]={}
                for h in range(0,23):
                    grid_dict[p][h]=np.zeros(shape=(nrows,ncols)) #python defines a matrix as rows,cols
        print grid_dict 
        ems=np.array([])
        data=fin.readlines()
        #header=data[0].rstrip('\r\n').split(',') #extracting header
        i=0;heading_lst={}
        #for heading in header:
        #   heading_lst[heading]=i
        #   i+=1
        #if sc4k==True:
        #        [shiftrow,shiftcol]=[3,150]
        #else:
        #        [shiftrow,shiftcol]=[0,0]
        for line in data:
	     hr=line[63:64].strip()
             i=line[36:38].strip()
             j=line[39:41].strip()
             #cyid=line[56:58].strip()
             basin="NA"
             CO_ems=float(line[78:88])
             NOX_ems=float(line[88:98])
             SOX_ems=float(line[98:108])
             TOG=float(line[108:118])
             PM=float(line[118:128])
             #NH3=float(line[128:138])
             try:
                 for p in pol_lst:
			try:
                            grid_dict[p][hr][i][j]+=p
                        except:
			    pdb.set_trace()
             except:
                 print i,j
        fin.close()
        return grid_dict
if __name__ == "__main__":
	output=load_hourly_ij("/share/aether/DataStorage/2012_SIP/Emis/MotorVehMeds/by2012/my2012/st_4k.mv.v0047..2012.201202d01..e14..meds.gz")
        print output

