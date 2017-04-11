import os
from time import strptime, strftime #importing library for date/time calculation
import pdb

def get_dates(medsfile,byear):
 cdate_vars=strftime("%a, %j %b %Y %H:%M:%S").split(); #Reading the current date and time
 cdate=int(str(cdate_vars[3])+str(cdate_vars[1])); #converting date to Julian: YYYYddd
 tvars=cdate_vars[4].split(':');  #reading the variables from current time
 ctime=int(int(tvars[0])*3600.+int(tvars[1])*60.+int(tvars[2]))  #converting current time to HHMMSS
 name_parts=os.path.basename(medsfile).split('.') 
 if '.rpt' in medsfile: 
	sdate=os.path.basename(medsfile).split('.')[-2]
 elif 'med' in medsfile:
	if len(name_parts)<9:
	  sdate=os.path.basename(medsfile).split('.')[1]
	else:
	  sdate=name_parts[5]
 sdate=str(byear)+sdate[4:]
 
 if sdate[6:9]=='d50': #average file
        sdate=int(str(sdate[0:3])+'001') #fixing sdate as YYYY001 meds is 13d50
 if sdate[6]=='d': #format like 203205d01
	YYYY=int(sdate[0:4])
	MM=sdate[4:6]
	dd=sdate[7:9]
	fmt='%Y%m%d'
	jday=str(strptime(str(YYYY)+MM+dd,fmt)[7]).rjust(3,'0')
	sdate=int(str(YYYY)+jday)
 elif sdate[6:9] in ['wdy','sat','sun','wde']:
        YYYY=int(sdate[0:4])
        MM=int(sdate[4:6])
        dow=sdate[6:9]
        dd=1
        fmt='%Y%m%d'
        if dow=='wdy': #currently wdy is a Wednesday=2 ;  Mon=0 ... Sun=6
                while not strptime(str(YYYY)+str(MM)+str(dd),fmt)[6] == 2:dd+=1 #day of week is wednesday
        if dow=='wde': #currently wdy is a Saturday=5 ;  Mon=0 ... Sun=6
                while not strptime(str(YYYY)+str(MM)+str(dd),fmt)[6] == 5:dd+=1 #day of week is wde or saturday
        if dow=='sat': #currently wdy is a Saturday=2 ;  Mon=0 ... Sun=6
                while not strptime(str(YYYY)+str(MM)+str(dd),fmt)[6] == 5:dd+=1 #day of week is saturday
        if dow=='sun': #currently wdy is a Sunday=2 ;  Mon=0 ... Sun=6
                while not strptime(str(YYYY)+str(MM)+str(dd),fmt)[6] == 6:dd+=1 #day of week is sunday
        jday=str(strptime(str(YYYY)+str(MM)+str(dd),fmt)[7]).rjust(3,'0') #julian day position
        sdate=int(str(YYYY)+jday)
 else:
        try: sdate=int(sdate)  #int(medsfile.split('.')[1]) #Reading file date.  It expects YYYYddd
        except ValueError: sdate=2010001 #june wdy: 06-02-2010  temporary, fix this 

 #print "cdate",cdate
 #print "ctime",ctime
 #print "sdate",sdate
 fmt='%Y%j'
 date=str(sdate)
 dowk=strptime(date[0:4]+date[4:7],fmt)[6]
 mm=strptime(date[0:4]+date[4:7],fmt)[1]
 
# print [sdate,mm,dowk]
 return [sdate,mm,dowk]
