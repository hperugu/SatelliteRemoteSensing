#!/usr/bin/python
from __future__ import print_function
import numpy as np
import matplotlib.mlab as mlab
import datetime
import pdb
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
import matplotlib.dates as mdates
import matplotlib.font_manager as font_manager
import matplotlib.cm as cm
import sys
sys.path.append('.')
from cfnd import *
def summary_nparray_total(datafile,y):
	#datafile = 'summaries/Summary_julwk1_DOW.csv'
	print('loading', datafile)
	r = mlab.csv2rec(datafile, converterd={3: lambda x: datetime.datetime.strptime(x, '%Y%j').date()})
	r.sort()
	# Here some how introduce map function for lambda
	if y==1:
		summaryfuncs = (
                	('jday',lambda x:[thisdate.weekday() for thisdate in x], 'weekday'),
			('cyid', lambda x: x, 'cy'),
			('eicsum', lambda x: x,'eic'),
			('pol', lambda x:x, 'poll'),
 			('ems', lambda x:x, 'emis'),
        		)
	else:
		 summaryfuncs = (
                        ('jday',lambda x:x, 'weekday'),
                        ('cyid', lambda x: x, 'cy'),
                        ('eicsum', lambda x: x,'eic'),
                        ('pol', lambda x:x, 'poll'),
                        ('ems', lambda x:x, 'emis'),
                        )

	rsum = mlab.rec_summarize(r,summaryfuncs)
	stats = (
	    ('emis', np.sum, 'rsum' ),
	    ('emis' , len , 'rcount'),
	    )
	print('summary by total')
	ry = mlab.rec_groupby(rsum, ('weekday','cy','poll','eic'), stats)
        return ry
#Get eic numbers from the file
def plotall_pol_total(ry,eic,polst):
        #Loop through all counties
	for cnum,fid,cname,dnum in Cfnd:
	    rc=ry[(ry.cy==cnum)]
	    ncname=cname.replace(" ","_")
	    # to define color list
	    colormap = plt.cm.gist_ncar
	    plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, len(eic))]) 
	    #loop for each pollutant
	    fig=plt.figure();l=1
	    for pol in polst:
		pol_arr=rc[(rc.poll==pol)]
		# loop over each eic code in eic_list and extract a plot array
		#if pol=='CO' or pol=='SOX':         
		#    plt.subplot(311)
		#elif pol=='NOX' or pol=='PM':
		#    plt.subplot(312)
		#else:
		#    plt.subplot(313)
		plt.plot(pol_arr.weekday,pol_arr.rsum,linestyle='-')
		plt.grid()
		plt.title(pol,fontsize=20,fontweight='bold')
		plt.xlabel("Date")
 		#fig.autofmt_xdate()
		#plt.gca().xaxis.set_major_formatter( DateFormatter('%m-%d') )
		#plt.fmt_xdata = DateFormatter('%m-%d')
		plt.ylabel("Emission in TPD")
		fig.savefig('/aa/hperugu/test/scripts/plots/plots_dow/%s_%i.png'%(ncname,l))        
		print ("......%s county's  plot no:%i  is completed"%(cname,l))
		#if l == 3:
		fig = plt.figure()
		l+=1
def convert_nparr_dict(ry,eic):
        dow=[];ems=[]
	for record in ry:
        	dow.append(record.weekday)
		ems.append(record.rsum)
	samp_dict=dict(zip(dow, ems))
        print (samp_dict)
        
	
if __name__ == '__main__':
        from sys import argv
        filepath= argv[1]
        #polst=['CO','NOX','SOX','PM','TOG']
        qa_arr=summary_nparray_total(filepath)
        #plotall_pol_total(qa_arr,polst)
        convert_nparr_dict(qa_arr, 'TOG')
        

