#!/usr/bin/python
from __future__ import print_function
import numpy as np
import matplotlib.mlab as mlab
import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import matplotlib.font_manager as font_manager
import matplotlib.cm as cm
import sys
sys.path.append('.')
from cfnd import *

def summary_nparray_eic(datafile):
	#datafile = '/aa/hperugu/test/scripts/summaries/Summary.csv'
	print('loading', datafile)
	r = mlab.csv2rec(datafile, converterd={3: lambda x: datetime.datetime.strptime(x, '%y%j')})
	r.sort()

	summaryfuncs = (
		('jday', lambda x: [thisdate.day for thisdate in x], 'weekday'),
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
	print('summary by jdays')
	ry = mlab.rec_groupby(rsum, ('weekday','cy','poll','eic'), stats)
        return ry
	#Get eic numbers from the file
	#Define 5 EIClists
def find_scale_max(ry,Cfnd,polst):
	eic=[]
	scale={}
	# Read All counties day by to decide scale
	for cnum,fid,cname,dnum in Cfnd:
	    for pol in polst:
		Sc_arr=ry[ (ry.cy==cnum) & (ry.poll==pol)]
	#Sort rec array
		Sc_arr.sort(order='rsum')
	# for generating scale min,max values
		for index,x  in np.ndenumerate(Sc_arr):
		    if x.eic not in eic:
			eic.append(x.eic)
		    try:
			scale[pol,x.eic].append(x.rsum) 
		    except KeyError:
			scale[pol,x.eic] = [x.rsum]
	scaleMax={}
	for keys, values in scale.items():
	    if not scaleMax.has_key(keys):
		scaleMax[keys]=max(values)
	    else:
	       scaleMax[keys].append(max(values))
	return scaleMax,eic
	#Loop through all counties
def plotall_pol_eic(ry,scaleMax,eic,polst):
        print (ry,scaleMax,eic,polst)
	for cnum,fid,cname,dnum in Cfnd:
	    rc=ry[(ry.cy==cnum)]
	    ncname=cname.replace(" ","_")
	    # to define color list
	    colormap = plt.cm.gist_ncar
	    plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, len(eic))]) 
	    #loop for each pollutant
	    for pol in polst:
		pol_arr=rc[(rc.poll==pol)]
		pol_arr.sort(order='rsum')
		l=1
	    # loop over each eic code in eic_list and extract a plot array
		fig = plt.figure()
		for w in sorted (scaleMax,key=scaleMax.get, reverse=False):
		    if pol in w[0]:
			each=w[1];ymax=scaleMax[w]
			if l in [1,2,3,10,11,12]:
				k = 311
			elif l in [4,5,6,13,14,15]:
				k = 312
			else:
				k = 313
			#Get the data for eic   
			jarr=pol_arr[(pol_arr.eic==each)]
			# Get the Y scale parameters
			#create subplot and activate it ???
			plt.subplot(k)
			if l%3==1 :
			    labels=[]
			    lines = []
			labels.append(r'%s' %each)
			line0,=plt.plot(jarr.weekday,jarr.rsum,linestyle='-')
			lines.append(line0)
			plt.grid()
			plt.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
			if l%3==0:
				plt.ylim(0,ymax)
				plt.legend(lines,labels,loc='upper right')
			# Now add the legend with some customizations.
			if l==9 or l==18:
				fig.suptitle(pol,fontsize=20,fontweight='bold')
				plt.xlabel("Julian Day")
				fig.autofmt_xdate()
				plt.ylabel("Emission in TPD")
				fig.savefig('/aa/hperugu/test/scripts/plots/%s_%s_%i.png'%(ncname,pol,l/9))        
				print ("......%s county's %s plot no:%i  is completed"%(cname,pol,l/9))
			if l == 9:
				fig = plt.figure()
			l+=1

