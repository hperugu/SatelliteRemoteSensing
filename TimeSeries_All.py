#!/usr/bin/python
import matplotlib.pyplot as plti
import pdb
from datetime import datetime as dt
import matplotlib.dates as mdates
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter,DateLocator
from pylab import *
from tsplotot import *
from tsploteic import *
from cfnd import *
# Options for first argument
# H -- Hourly Plotting, requires only one more argument
# M -- Daily plotting, requires only one more argument
# D -- Day of Week plotting, requires only one more argument
# TH -- Temperature and PollutantHourly plotting requires two more arguments
# TD -- Temeperature and Pollutnat Day of Week plotting, requires two more arguments
# TM -- Temeperature and Pollutant Daily plotting, requires two more arguments
# B -- batch mode , requires no argument

years    = mdates.YearLocator()   # every year
months   = mdates.MonthLocator()  # every month
yearsFmt = mdates.DateFormatter('%Y')
dates    = mdates.DateLocator()
def importTemp_data(filepath):
    print filepath
        # Read lines , skip first row
    with open (filepath,"r") as f:
      #columns=f.readlines()[0]
       lines=f.readlines()
  # need little massaging here to convert the time etc
    dTime=[]; Date=[]; Temp=[]
    for line in lines:
	line=line.strip()
	dTime.append(line.split(",")[0])
    Temp.append(line.split(",")[1])
    fTemp=[float(x) for x in Temp]
    for n in dTime:
	Date.append(mdates.date2num(dt.strptime(n, '%m/%d/%Y %H:%M')))
    return Date,fTemp
# Import standard qarpt.hourly
def importqarpt(qarpt,y):
       # Read lines , skip first row
    with open (qarpt,"r") as f:
	#columns=f.readlines()[0]
	lines=f.readlines()
        # need little massaging here to convert the time etc
        Jday_Hour=[]; fmtDate=[]; Pol=[]
        for line in lines:
            line=line.strip()
            Jday_Hour.append(line.split(",")[3]+" "+line.split(",")[5]+":00")
            Pol.append(float(line.split(",")[11]))
        for n in Jday_Hour:
	    fmtDate.append(mdates.date2num(dt.strptime(n, '%Y%j %H:%M')))
        qa_dict=dict(zip(fmtDate,Pol))
	if y==1:
	    return qa_dict
	else:	    
	    return fmtDate,Pol

# The plotting program
def plotdata(x,y,output,xname,xfmt):
    fig, ax1 = plt.subplots()
    ax1.plot_date(x,y,'-')
    plt.title( 'Temperature - Hourly for %s' %output )
    plt.xlabel( xname )
    plt.ylabel( "Temperature" )
    ax1.fmt_xdata = DateFormatter(xfmt)
    fig.autofmt_xdate()
    plt.savefig( '%s.png' % output )
    plt.show()
# Plot two lines

def plotdata2(x,y1,y2,output):
    fig, ax1 = plt.subplots()
    l1=plt.plot_date(x,y1)
    l2=plt.plot_date(x,y2)
    setp(l1, linestyle='--')  
    setp(l2,linestyle='--')     # set both to dashed
    setp(l1, linewidth=2, color='r')  # line1 is thick and red
    setp(l2, linewidth=1, color='g')  # line2 is thicker and green
    plt.title( 'Temperature - Hourly for %s' %output )
    plt.xlabel( "Dates" )
    plt.ylabel( "Temperature" )
    ax1.fmt_xdata = DateFormatter('%M-%d')
    fig.autofmt_xdate()
    plt.savefig( '%s.png' % output )
    plt.show()

#Sorting the Data
def grab_Data(x1,y1,qa_dict):
    sort_data=[]
    for each in x1:
	sort_data.append(qa_dict.get(each))
    return sort_data
#Seconday Axis Plotting

def plotdata_second(x,y,s,output,xname,xfmt):
    fig, ax1 = plt.subplots()
    ax1.plot_date(x,y,'b-',label='Temp')
    plt.title( 'Temperature-TOG  Hourly Plot for %s County'%output )
    plt.xlabel( xname )
    plt.ylabel( "Temperature" )
    #ax1.fmt_xdata = DateFormatter('%M-%D')
    #plt.gcf().axes[0].xaxis.set_major_formatter('%M-%D')
    #ax1.xaxis.set_major_formatter('%m-%d')
    fig.autofmt_xdate()
    #Secondary Axis
    ax2 = ax1.twinx()
    ax2.plot_date(x, s, 'r-',label='TOG')
    handles, labels = ax2.get_legend_handles_labels()
    # reverse the order
    ax2.legend(handles[::-1], labels[::-1])
    ax2.set_ylabel('TOG', color='r',size='large')
    #ax2.set_ylim(0,4)
    plt.savefig( '%s_TOG.png' % output )
    plt.show()

if __name__ == '__main__':
    from sys import argv
    from tsplotot import *
    from tsploteic import *
    polst=['CO','NOX','SOX','PM','TOG']
    opt= argv[1];filepath=argv[2];output=argv[3]
    if opt=='H':
	print " Creating Timeseries for Pollutant Hourly Totals"
	filepath= argv[2]
	output= argv[3]
	x,y=importqarpt(filepath,0)
	pdb.set_trace()
	plotdata(x,y,output,"Dates",'%M-%d')
    elif opt=='D':
	print " Creating Timeseries for Pollutant Day-of-Week Totals"
	filepath= argv[2]
        output= argv[3]
    elif opt=='M':
	print " Creating Timeseries for Pollutant Daily Totals "
	filepath= argv[2]
        output= argv[3]
    elif opt=='TD':
	print " Creating Timeseries for Pollutant & Temperature Day-of-Week Totals"
        sec_data= argv[4]
    elif opt=='TM':
	print "Creating Timeseries for Pollutant & Temperature Daily Totals"
    elif opt=='TTH':
	print "Creating Timeseries for Two Different Temperatures"
	filepath=argv[2];output= argv[3];line2_data =argv[4]
	x,y1=importTemp_data(filepath)
        x2,y2=importTemp_data(line2_data)
        plotdata2(x,y1,y2,output)
    elif opt=='TH':
	print "Creating Timeseries for Pollutant & Temperature for Hourly Totals"
	filepath=argv[2];output=argv[3];sec_data=argv[4] 
	x,y1=importTemp_data(filepath)
        sec_dict=importqarpt(sec_data,1)
        sData=grab_Data(x,y1,sec_dict)
        plotdata_second(x,y1,sData,output,"Dates", '%Y-%M-%D')

    elif opt=='BTD':
        print " Creating Timeseries for Pollutant Daily Totals in Batch Mode"
        qa_arr_tot=summary_nparray_total(filepath,1)
        maxScale,eiclst=find_scale_max(qa_arr_eic,Cfnd,polst)
        plotall_pol_total(qa_arr_tot,eiclst,polst)
    elif opt=='BED':
	print " Creating Timeseries for EIC Daily Totals in Batch Mode "
	qa_arr_eic=summary_nparray_eic(filepath,1)
	maxScale,eiclst=find_scale_max(qa_arr_eic,Cfnd,polst)
	plotall_pol_eic(qa_arr_eic,maxScale,eiclst,polst)
    elif opt=='BTM':
	print " Creating Timeseries for Pollutant Daily Totals in Batch Mode"
	qa_arr_tot=summary_nparray_total(filepath,0)
	maxScale,eiclst=find_scale_max(qa_arr_eic,Cfnd,polst)
	plotall_pol_total(qa_arr_tot,eiclst,polst)
    elif opt=='BEM':
	print " Creating Timeseries for EIC Daily Totals in Batch Mode "
	qa_arr_eic=summary_nparray_eic(filepath,0)
        maxScale,eiclst=find_scale_max(qa_arr_eic,Cfnd,polst)
	plotall_pol_eic(qa_arr_eic,maxScale,eiclst,polst)
    else:
	print "Options are not specified"
    

