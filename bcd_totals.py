#!/usr/bin/python

import gzip
import sys
from itertools import chain
from collections import defaultdict
d = defaultdict(int)
#python bcd_totals.py  /aa/djohnson/gei/mv/calnex/2010/2010/[0-9][0-9]/[0-9][0-9]/emfac/Los_Angeles.bcd.gz
def read_bcd(cname):
    #t2kg = 2000./2.205
    t2kg = 1.0
    fin = gzip.open(cname,"r")
    bcd = {}
    names_str = "calyr startmyr endmyr airbasin county starts" +\
      " population vmt_1000 vehtype vehtech pollutant process" +\
      " emissions basis"
    types_str = "i i i s s f" + " f f s s s s" +  " f s"
    names_arr = names_str.split()
    types_arr = types_str.split()
    for line in fin:
        line = line.rstrip()
        if line.find("CALYR") > -1: # skip header lines
            continue
        fields = {}
        args = line.split(',')
        for i in range(len(names_arr)):
            name = names_arr[i]
            type = types_arr[i]
            if type == 'i':
                fields[name] = int(args[i])
            elif type == 'f':
                fields[name] = float(args[i])
            else:
                fields[name] = args[i].strip()
        hr = 24
        if fields['basis'].find('Hr') > -1:
            hr = int(fields['basis'][2:])
        emis = fields['emissions']*t2kg
        #if emis == 0.:
        #     continue
        if fields['process'].find("Total") > -1:
             continue
        pol = fields['pollutant']
        vtype = fields['vehtype']
        vtech = fields['vehtech']
        proc = fields['process']
        if not bcd.has_key(pol):
            bcd[pol] = {}
        if not bcd[pol].has_key(vtype):
            bcd[pol][vtype] = {}
        if not bcd[pol][vtype].has_key(vtech):
            bcd[pol][vtype][vtech] = {}
        if not bcd[pol][vtype][vtech].has_key(proc):
            bcd[pol][vtype][vtech][proc] = [0.]*25
        bcd[pol][vtype][vtech][proc][hr] = emis
            
    fin.close()
    return(bcd)

def sum_bcd(bcd):
    pol_qnty={}
        
    for pol in sorted(bcd.keys()):
       psum=0
       plist=[]
       for vtype in sorted(bcd[pol].keys()):
          for vtech in sorted(bcd[pol][vtype].keys()):
             for proc in sorted(bcd[pol][vtype][vtech].keys()):
                 for hr in range(0,23):
                    emis =bcd[pol][vtype][vtech][proc][hr] 
                    plist.append(emis)
       for i in plist:
          psum += i 
       if not pol_qnty.has_key(pol):
          pol_qnty[pol]={}
       pol_qnty[pol]=psum
    #print (pol_qnty)
    return(pol_qnty)
if __name__ == "__main__":
    a=1
    filenames=[]
#PROCESSING INPUT OPTIONS
    while(a<len(sys.argv)):
        if(sys.argv[a]=='-out'): a+=1; outname=sys.argv[a] #following meds naming convention
        else: filenames.append(sys.argv[a])
        a+=1
    yr_ems={}
    out= open(outname,"w")
    for file in filenames:
        date= file.split('/')[-4]+"/"+file.split('/')[-3]+"/"+file.split('/')[-5]
        #date = file[51:57]+file[46:50]
        rbcd = read_bcd(file)
        pol_ems=sum_bcd(rbcd)
        print("Processing %s file"%date)
        if not yr_ems.has_key(date):
            yr_ems[date]={}
        for pol,psum in pol_ems.items():
            if not yr_ems[date].has_key(pol):
                yr_ems[date][pol]=psum    
                #if pol=='TOG':
                out.write("%s,%s,%s\n"%(date,pol,psum))
                #else:
                    # continue    
           
    out.close()


