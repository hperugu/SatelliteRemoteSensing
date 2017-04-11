#latest update 6/26/12
#how to run:
#e.g:  python addvmt.py lnk.sacog.7.9.csv    # lnk totals for hour 9 for sacog county 7
# python addvmt.py lnk.*7*.csv    # lnk totals for county 7 all hours
#      python addvmt.py taz.sacog.7.9.csv #taz totals for hour 9 sacog county 7
# python addvmt.py lnk.*7*.csv    # taz totals for county 7 all hours

import sys
import pg
import datetime
import pdb
import numpy as np
import os
import pylab as p
#import edate
from decimal import * #Decimal
import operator
from glob import iglob
import shutil

outprefix="dtim_sums"
#inpath="./"
if len(sys.argv)< 2:
	sys.stderr.write("Please specify file(s) to process.\n")
	sys.exit()
path=os.getcwd()
a=1
cty=-1
dd=-1
nscc=-1
filenames=[]
file_name='NA'
#save_as=-1
scc_lst={}
#pdb.set_trace()
#PROCESSING INPUT OPTIONS
while(a<len(sys.argv)):
	if(sys.argv[a]=='-taz'): a+=1; type='taz'  # optional -not needed
	elif(sys.argv[a]=='-lnk'): a+=1; type='lnk'# optional -not needed
	else: filenames.append(sys.argv[a])
        a+=1
ems_lst={}
#pdb.set_trace()
#if (file_name=='NA'): #it means no file name was given. using different naming convention
#varspath=path.split('.')
#if (len(varspath)==5):   #checking for name convention eg: lnk.fresno.19.2.csvt
#    type=varspath[0]
#    cog=varspath[1]
#    cfips=varspath[2]
#    hh=str(varspath[3]).rjust(2,'0') #apending a 0 to hours less than 10
#pdb.set_trace()
type=filenames[0].split('.')[0]
cog=filenames[0].split('.')[1]
#pdb.set_trace()
cfip=filenames[0].split('.')[2]
print "The following files:"
for file in filenames:
#       print file
        os.system("ls -l '"+file+"'")
print "File count:"
print len(filenames)
print
sumfname="cfips_"+cfip+"_"+type+".sum"
catfname="cfips_"+cfip+"_"+type
print "Will be cated together as:",outprefix+"/"+catfname #cfips_"+cfip+"_"+type
#pdb.set_trace()
try: os.makedirs(outprefix)
except: pass
catedfile = open(outprefix+"/"+catfname, 'wb')

for filename in filenames:
    shutil.copyfileobj(open(filename, 'rb'), catedfile)
catedfile.close()

#os.system("cat filenames > "+outprefix+"/"+cog)
#pdb.set_trace()
#d1= np.genfromtxt(file_name, delimiter=',')
d= np.loadtxt(open(outprefix+"/"+catfname,"rb"),delimiter=",",skiprows=0)
sum_vmt=0
#labels=['LDA_gas', 'LDT1_gas', 'LDT2_gas','MDV_gas','LHD1_gas','LHD2_gas','T6TS_gas','T7IS_gas',
#        'OBUS_gas','UBUS_gas','MCY_gas','SBUS_gas','MH_gas',
#        'LDA_dis', 'LDT1_dis', 'LDT2_dis','MDV_dis','LHD1_dis','LHD2_dis','T6TS_dis','T7IS_dis',
#        'OBUS_dis','UBUS_dis','MCY_dis','SBUS_dis','MH_dis']
#tot_vtype={}
#for i in range(0,26):
#    vtypei=sum(d[:,6]*d[:,8+i])
#    sum_vmt=sum_vmt+vtypei
#    print labels[i],"=",vtypei
#sum(d1[:,6]*d1[:,7])
#pdb.set_trace()
#print "total vmt:",sum_vmt
v_gas={'LDA_gas':1,'LDT1_gas':2,'LDT2_gas':3,'MDV_gas':4,'LHD1_gas':5,
           'LHD2_gas':6,'T6TS_gas':7,'T7IS_gas':8,'OBUS_gas':9,'UBUS_gas':10,
           'MCY_gas':11,'SBUS_gas':12,'MH_gas':13}
v_dis={'LDA_dis':1,'LDT1_dis':2,'LDT2_dis':3,'MDV_dis':4,'LHD1_dis':5,
           'LHD2_dis':6,'T6TS_dis':7,'T7IS_dis':8,'OBUS_dis':9,'UBUS_dis':10,
           'MCY_dis':11,'SBUS_dis':12,'MH_dis':13}
#veh={'LDA_gas':1,'LDT1_gas':2,'LDT2_gas':3,'MDV_gas':4,'LHD1_gas':5,
#     'LHD2_gas':6,'T6TS_gas':7,'T7IS_gas':8,'OBUS_gas':9,'UBUS_gas':10,
#     'MCY_gas':11,'SBUS_gas':12,'MH_gas':13,
#     'LDA_dis':14,'LDT1_dis':15,'LDT2_dis':16,'MDV_dis':17,'LHD1_dis':18,
#     'LHD2_dis':19,'T6TS_dis':20,'T7IS_dis':21,'OBUS_dis':22,'UBUS_dis':23,
#     'MCY_dis':24,'SBUS_dis':25,'MH_dis':26}

sum_dis=0
sum_gas=0
vgas={}
vdis={}
#tot_gas=sum(d[:,6]*sum(d[:,7:20]))
#tot_dis=sum(sum(d[:,21:35]))

#pdb.set_trace()
if type=='lnk': 
 for key in sorted(v_gas):
#for key in sorted(v_gas.iteritems(), key=operator.itemgetter(1)):
#    key=key[0]
    vtypei=sum(d[:,6]*d[:,7+v_gas[key]])
    vgas[key]=vtypei
   
    #print key,"=",vtypei#, "| frac=",vtypei/tot_gas
    sum_gas=sum_gas+vtypei
#print "total_gas = ",sum_gas
 for key in sorted(v_dis):
#for key in sorted(v_dis.iteritems(), key=operator.itemgetter(1)):
#    key=key[0]
    vtypei=sum(d[:,6]*d[:,20+v_dis[key]])
    vdis[key]=vtypei
    sum_dis=sum_dis+vtypei
    #print key,"=",vtypei#, "| frac=",vtypei/tot_dis
elif type=='taz':
 for key in sorted(v_gas):
 #   pdb.set_trace()
    vtypei=sum(d[:,2]*d[:,5+v_gas[key]])
    vgas[key]=vtypei

    #print key,"=",vtypei#, "| frac=",vtypei/tot_gas
    sum_gas=sum_gas+vtypei
#print "total_gas = ",sum_gas
 for key in sorted(v_dis):
    vtypei=sum(d[:,2]*d[:,43+v_dis[key]])
    vdis[key]=vtypei
    sum_dis=sum_dis+vtypei
else:
 sys.exit("Error!. What type of file? -lnk  -taz")


sum_tot=sum_dis+sum_gas
fout=open(outprefix+"/"+sumfname,'w')
for key in vgas:
#   print key,"=",vgas[key]," | frac=",vgas[key]/sum_gas
   fout.write(str(key)+","+str(vgas[key])+","+str(vgas[key]/sum_gas)+"\n")
for key in vdis:
#   print key,"=",vdis[key]," | frac=",vdis[key]/sum_dis
   fout.write(str(key)+","+str(vdis[key])+","+str(vdis[key]/sum_dis)+"\n")

#print "total_gas = ",sum_gas
fout.write("total_gas ,"+str(sum_gas)+",\n")
#print "total_dis = ", sum_dis
fout.write("total_dis ,"+str(sum_dis)+",\n")
#print "total_gas+dis =", sum_gas+sum_dis
fout.write("total_gas+dis,"+str(sum_gas+sum_dis)+",\n")
#pdb.set_trace()
