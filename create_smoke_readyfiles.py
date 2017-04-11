#!/bin/python
import os
import pdb
import csv
import operator
from county_nums import county_nums
from datetime import datetime
import glob
import calendar
from copy import deepcopy
##########Description of Program ########################################################################################
'''This Program creates following inputs
1. A MCODES file based on Vehicle codes, process codes and fuel techs
2. Reformatted gspro and gsref files
3. Reformatted EMFAC rates to SMOKE format (mrclist)
4. A MBINV file from EMFAC activity output
5. Reformatted mtpro and mtref files 
Modifications Needed:
1. Relative Humidity should be based on MET4MOVES output
'''
#############Preparing Lookup values#####################################################################################
'''Lookup directories'''
Year = '2012' 
rootDir='/aa/hperugu/SMOKE_EMFAC/'
lookups = rootDir+'lookups/'
inputs =  rootDir+'inputs/'
spcdir = inputs+'speciation'
outputs = rootDir + 'outputs/'

'''Lookup Output files'''
fwkfactor = inputs+'factor.2012.csv'
fhrfactor = inputs+'hourlydist.caltrans.csv'
gsProIn = os.path.join(spcdir, 'gspro.all.010815.csv')
gsRefIn = os.path.join(spcdir,'gsref.25jun2014.2012.d')

'''Lookup files'''
fprocCodes =  os.path.join(lookups,'processid_comp.csv')
fvehCodes =  os.path.join(lookups,'vehcodes.csv')
dsccCodes = os.path.join(lookups,'lookup_newSCC_v6.csv')
fspeedBins = os.path.join(lookups,'speed_bins.csv')
emfac2Emfac = os.path.join(lookups,'Emfac2Emfac.csv')
gai_map = os.path.join(lookups,'gai_map.csv')
hdOperationData = os.path.join(lookups,'hd_operation_days.csv')
ldvOperationData= os.path.join(lookups,'operation_hours_ldv.csv')
HDIdleActivity = os.path.join(lookups,'HD_idle_activity.csv')
LDIdleActivity = os.path.join(lookups,'LD_idle_activity.csv')
SoaktimeFile = os.path.join(lookups,'Soak_Time_Distribution.csv')
HdTimeinCa =os.path.join(lookups,'hd_time_in_ca.csv')
WkDyVmt = os.path.join(lookups,'weekday_vmt_factor.csv')
vcc = os.path.join(lookups,'VCC.csv')

'''Lookup dictionaries'''
catDict = {'1':'CAT','2':'NCAT','3':'DSL'}
pos = {'HC':0,'CO':1,'NOx':2,'TOG':3,'PMEX':4,'PMTW':5,'PMBW':6,'CO2':7,'EVAP':8,'FUEL':9}
POL_NAME = {1: 'HC', 2: 'CO', 3: 'NOx', 4: 'EVAP', 5:'SOx', 6: 'PMEX', 8: 'TOG',10: 'CO2',\
14: 'FUEL', -13: 'PMTW', -14: 'PMBW'}
polnames = POL_NAME.values()
CNTY = {'MONTEREY': 53, 'SONOMA': 97, 'SACRAMENTO': 67, 'SAN BENITO': 69,\
'YOLO': 113, 'SISKIYOU': 93, 'VENTURA': 111, 'CALAVERAS': 9, 'LASSEN': 35, \
'IMPERIAL': 25, 'ALAMEDA': 1, 'SAN MATEO': 81, 'TRINITY': 105, 'SANTA CLARA': 85,\
'KERN': 29, 'NEVADA': 57, 'SAN JOAQUIN': 77, 'MONO': 51, 'SAN DIEGO': 73,\
'SAN LUIS OBISPO': 79, 'EL DORADO': 17, 'MARIN': 41, 'MADERA': 39, 'PLACER': 61,\
'TUOLUMNE': 109, 'LOS ANGELES': 37, 'MODOC': 49, 'ORANGE': 59, 'BUTTE': 7, \
'TULARE': 107, 'SANTA BARBARA': 83, 'MENDOCINO': 45, 'SUTTER': 101, 'SOLANO': 95,\
'HUMBOLDT': 23, 'FRESNO': 19,'MERCED': 47, 'SIERRA': 91, 'DEL NORTE': 15, 'YUBA': 115,\
'SANTA CRUZ': 87, 'AMADOR': 5, 'KINGS': 31, 'TEHAMA': 103,'SAN FRANCISCO': 75,\
'RIVERSIDE': 65, 'NAPA': 55, 'ALPINE': 3, 'MARIPOSA': 43, 'STANISLAUS': 99, 'GLENN': 21, \
'CONTRA COSTA': 13, 'LAKE': 33, 'PLUMAS': 63, 'SHASTA': 89, 'INYO': 27, 'SAN BERNARDINO': 71, 'COLUSA': 11}
assocactivDict = {'VMT':['RUNEX','PMBW','PMTW'],'POPULATION':['PRESTLOSS','MDRESTLOSS','PDIURN','MDDIURN','IDLEX','RUNLOSS'],\
'TRIPS':['STREX','HOTSOAK','RUNLOSS']}
procAssocDict = {'CO':['EXR','EXS','CXR','CXS','CEI','EXT'],'TOG':['EXR','EXS','CXR','CXS','CEI','EXT','EVP','EFV','EFL'],\
'NOX':['EXR','EXS','CXR','CXS','CEI','EXT'],'SOX':['EXR','EXS','CXR','CXS','CEI','EXT'],'PM':['EXR','EXS','CXR','CXS','CEI','EXT']}
###################################################################################################################################

# Merging nested Dictionaries
def merge_dicts(dict1, dict2):
    """ Recursively merges dict2 into dict1 """
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    for k in dict2:
        if k in dict1:
            dict1[k] = merge_dicts(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]
    return dict1

# LookUp Method--- It creates all required global look up dictionaries
def lookupDict(procCodes,vehCodes,cat_dict, dsccCodes,fspeedBins,emfac2Emfac,vcc): 
	""" This method creates all the required dictionaries \n
	ProcessID dictionary, Vehicle code dictionary, dtimSCCC-to-NewSCC \n
	code dictionary and a New SCC code dictionary based on Vehicle code,\n
	Vehicle tech code and emission process """
	args = []
	procDict = {}
	nprocDict = {}
	vehDict = {}
	sccDict = {}
	spdDict = {}
	dsccDict = {}
	emfacDict = {}
	hdOpDict = {}
	ldOpDict = {}
	HDIdActivDict = {}
	LDIdActivDict = {}
	gaiDict = {}
	soakHrdistDict = {}
	soakdistDict = {}
	hdCaPct= {}
	wkdayFact = {}
	vccDict = {}
	dutyDict = {}

	with open(HdTimeinCa,'r') as f:
		for line in f.readlines()[1:]:
			args = line.strip().split(",")
			veh = args[2]
			frac = args[1]
			hdCaPct[veh] = float(frac)

	with open(WkDyVmt,'r') as f:
		for line in f.readlines()[1:]:
			args = line.strip().split(",")
			veh = args[2].upper()
			fuel = args[3].upper()
			frac = args[4]
			wkdayFact[(veh,fuel)] = float(frac)
	
	with open(vcc,'r') as f:
		for line in f.readlines()[1:]:
			args = line.strip().split(",")
			vcc = args[0]
			veh = args[3].upper()
			fuel = args[1].upper()
			duty = args[4].upper()
			vccDict[vcc] = [veh,fuel]
			dutyDict[(veh,fuel)] = duty

	for line in open(procCodes,'r').readlines():
		args = line.strip().split(",")
		proc_num = args[0]
		proc_name = args[1]
		smk_proc = args[5]
		typ = args[4]
		procDict[(proc_num)] = [proc_name,smk_proc,typ]
		nprocDict[(proc_name)] = [proc_num,smk_proc,typ]

	for line in open(gai_map,'rb').readlines():
		args = line.strip().split(',')
		gai_num = args[0]
		county_num = args[1]
		county_name = args[2].upper()
		gaiDict[gai_num] =[county_num,county_name]

	for line in open(vehCodes,'r').readlines():
		args = line.strip().split(",")
		veh_num = args[1]
		vehType = args[0]
		vehDict[veh_num] = vehType

	for line in open(dsccCodes,'r').readlines()[1:]:
		args = line.strip().split(",")
		dtimSCC = args[5]
		NewSCC = args[4]
		if not dsccDict.has_key(dtimSCC):
			dsccDict[dtimSCC] = []
		dsccDict[dtimSCC].append(NewSCC)

	for line in open(fspeedBins,'r').readlines()[1:]:
		vals = line.strip().split(',')
		spdDict[(vals[1],vals[2])] = vals[0]

	for line in open(emfac2Emfac,'r').readlines()[1:]:
		vals = line.split(',')
		emfacDict[vals[0].strip().upper()] = vals[1].strip()

	for line in open(dsccCodes,'r').readlines():
		args = line.split(',')
		veh = args[0].strip()
		fuel = args[1].strip()
		proc = args[2].strip()
		spdBin = args[3].strip()
		fscc = args[4].strip()
		sccDict[(veh,fuel,proc,spdBin)] = fscc

	for line in open(hdOperationData,'r').readlines()[1:]:
		vals= line.strip().split(',')
		hdOpDict[(vals[1].upper(),'DSL')] = float(vals[3])
		hdOpDict[(vals[1].upper(),'GAS')] = 0.0

	for line in open(ldvOperationData,'r').readlines()[1:]:   
		vals = line.strip().split(',')
		ldOpDict[(vals[2].upper(),vals[4])] = float(vals[5])
 
	for line in open(LDIdleActivity, 'r').readlines()[1:]:
		vals = line.strip().split(',')
		year = vals[0]
		if year == Year:continue
		gai = vals[1]
		veh = vals[4].upper()
		fuel = vals[5].upper()
		idle_hr = float(vals[3])
		county = gaiDict[gai][1].upper()
		if not LDIdActivDict.has_key(county):
			LDIdActivDict[county] = {}
		LDIdActivDict[county][(veh,fuel)] = idle_hr

	for line in open(HDIdleActivity, 'r').readlines()[1:]:
		vals = line.strip().split(',')
		year = vals[0]
		if vals[0] <> Year:continue
		gai = vals[1]
		county = gaiDict[gai][1].upper()
		veh = vals[2].strip().upper()
		idle_hr = float(vals[4])
		if not HDIdActivDict.has_key(county):
			HDIdActivDict[county] = {}
		HDIdActivDict[county][(veh,'DSL')] = idle_hr
	TotIdActivDict = merge_dicts(LDIdActivDict,HDIdActivDict)

	for line in open(SoaktimeFile,'r').readlines()[1:]:
		vals = line.strip().split(',')
		soak_time_freq = float(vals[4])
		veh =  vals[5].upper()
		soak_time = int(vals[6])
		hr = int(vals[3])
		if soak_time > 720: 
			soak_time = 720
		fuel = vals[7]
		soak_time = str(soak_time)
		if fuel == 'ELEC':
			continue
		if not soakHrdistDict.has_key((veh,fuel)):
			soakHrdistDict[(veh,fuel)] = {}
			soakdistDict[(veh,fuel)] = {}
		if not soakHrdistDict[(veh,fuel)].has_key(soak_time):
			soakHrdistDict[(veh,fuel)][soak_time] = {}
			soakdistDict[(veh,fuel)][soak_time] = 0.0
		if not soakHrdistDict[(veh,fuel)][soak_time].has_key(hr):
			soakHrdistDict[(veh,fuel)][soak_time][hr] = 0.0
		soakdistDict[(veh,fuel)][soak_time] += soak_time_freq 
		soakHrdistDict[(veh,fuel)][soak_time][hr] += soak_time_freq 
	
	# Actually the soak times have to be normalized for hours
	for veh,fuel in soakHrdistDict.keys():
		for soak_time in soakHrdistDict[(veh,fuel)].keys():
			tot = soakdistDict[(veh,fuel)][soak_time]
			for hr,val in soakHrdistDict[(veh,fuel)][soak_time].items():
				try:
					soakHrdistDict[(veh,fuel)][soak_time][hr] = val/tot
					soakdistDict[(veh,fuel)][soak_time] = tot/100
				except:
					soakHrdistDict[(veh,fuel)][soak_time][hr] = 0.0
	#For Debugging purpose
	for veh,fuel in soakHrdistDict.keys():
		for soak_time in sorted(soakHrdistDict[(veh,fuel)].keys()):
			test = 0.0
			for hr,val in soakHrdistDict[(veh,fuel)][soak_time].items():
				test += val

	return procDict,vehDict,spdDict,dsccDict,sccDict,catDict,emfacDict,nprocDict, hdOpDict,ldOpDict,TotIdActivDict,soakdistDict, soakHrdistDict,hdCaPct,wkdayFact,vccDict,dutyDict



class emfac2smoke(object):
	'''This method intializes all lookup dictionaries'''
	def __init__(self,gspro,gsref,procDict,nprocDict,vehDict,spdDict,dsccDict,sccDict,catDict,emfacDict,hdOpDict,ldOpDict,TotIdActiv,soakdistDict,soakHrdistDict,hdCaPct,wkdayFact,vccDict,dutyDict):
		self.gspro = gspro
		self.gsref = gsref
		self.procDict = procDict
		self.dsccDict = dsccDict
		self.nprocDict = nprocDict
		self.vehDict = vehDict
		self.catDict = catDict
		self.spdDict = spdDict
		self.sccDict = sccDict
		self.emfacDict = emfacDict
		self.hdOpDict  = hdOpDict
		self.ldOpDict  = ldOpDict 
		self.TotIdActiv = TotIdActiv
		self.soakdistDict = soakdistDict
		self.hdCaPct = hdCaPct
		self.wkdayFact = wkdayFact
		self.soakHrdistDict = soakHrdistDict
		self.vccDict = vccDict
		self.dutyDict = dutyDict

	def create_gs(self):
		""" This method should also update FSCC numbers""" 
		gsProInf = open(gsProIn,'r')
		gsProOut = open(self.gspro,'w')
		gsRefInf = open(gsRefIn,'r')
		gsRefOut = open(self.gsref,'w')
		gsProDict = {}
		gsRefDict = {}
		for line in open(gsRefIn,'r').readlines():
			oldSCC,profID,polID = line.strip().split(',')
			if oldSCC in self.dsccDict or oldSCC == '0':
				if oldSCC =='0':
					if not gsRefDict.has_key(oldSCC):
						gsRefDict[oldSCC] = {}
					if not gsRefDict[oldSCC].has_key(profID):
						gsRefDict[oldSCC][profID]=polID 	            
				else:
					try:
						for newSCC in self.dsccDict[oldSCC]:
							if not gsRefDict.has_key(newSCC):
								gsRefDict[newSCC] = {}
							if not gsRefDict[newSCC].has_key(profID):
								gsRefDict[newSCC][profID]=polID    
					except:
						continue
		for scc in sorted(self.sccDict.values()):
			scc_emfac_proc = list([key for key, value in self.sccDict.iteritems() if value == scc][0])[2]
			scc_smk_proc = self.nprocDict[scc_emfac_proc][1]
			#for all_smk_proc in ['BRK','CEI','CXR','CXS','EFL','EFV','EPM','EVP','EXR','EXS','EXT','TIR']:
			for nonHapol in ['CO','NOX','SOX']:
				for all_smk_proc in procAssocDict[nonHapol]:
					if all_smk_proc == scc_smk_proc:
						continue
						newLine = ";".join([scc,nonHapol,all_smk_proc +'__'+nonHapol])+'\n'
					else:
						newLine = ";".join([scc,'0',all_smk_proc +'__'+nonHapol])+'\n'
						#continue
					gsRefOut.write(newLine)
			for Hapol in ['PM','TOG']:
				for all_smk_proc in procAssocDict[Hapol]:
					if all_smk_proc == scc_smk_proc:
						if scc in gsRefDict:
							prof = [key for key,value in gsRefDict[scc].iteritems() if value == Hapol][0]
							newLine = ";".join([scc,prof,all_smk_proc +'__'+Hapol])+'\n'
						else:     
							newLine = ";".join([scc,'0',scc_smk_proc +'__'+Hapol])+'\n'
						gsRefOut.write(newLine)
					else:
						newLine = ";".join([scc,'0',all_smk_proc +'__'+Hapol])+'\n'
						gsRefOut.write(newLine)
		'''We do not need to create GSPRO file every time we update'''
		for line in open(gsProIn,'r').readlines():
			profId,polID,spec,split,div,massfrac = line.strip().split(',')
			if profID in gsRefDict:
				if not gsProDict.has_key((profId,polID,spec)):
					gsProDict[(profId,polID,spec)]=[]
				else:
					gsProDict[(profId,polID,spec)].append([split,div,massfrac])
			for profId,polID,spec in gsProDict:
				for fracs in gsProDict[(profId,polID,spec)]:
					line = +fracs
					newLine =','.join([profId,polID,spec,fracs])+'\n'
					gsProOut.write(newLine)
 		gsProOut.close()
		gsRefOut.close()

	'''This method is used to create fuel month reference file'''
	def create_mfmref(self,fmref):
		self.fmref = fmref
		print "writing mfmref file"
		f = open(fmref,'w')
		for conum in xrange(1,59):
			for month in xrange(1,13):
				if month < 7:
					line= str(6000+conum*2-1)+',1,'+str(month)+'\n'
					print line
				else:
					line= str(6000+conum*2-1)+',7,'+str(month)+'\n'
					print line
				f.write(line)
		f.close()

	'''This method is used prepare a county wide relative humidity dictionary'''	
	def read_rh(self,ftrh):
		self.ftrh = ftrh
		print "reading Trh file"
		rhDict = {}
		avgrhDict = {}
		cntDict = {}
		for line in open(ftrh,'r').readlines()[1:]:
			hr,mon,gai,cyid,cname,temp,rh = line.strip().split(",")
			if not rhDict.has_key(mon):
				rhDict[mon] = {}
				cntDict[mon] = {}
				avgrhDict[mon] = {}
			if not rhDict[mon].has_key(cyid):
				rhDict[mon][cyid] = 0.0
				cntDict[mon][cyid]= 0
				avgrhDict[mon][cyid] = 0.0
			rh = float(rh)
			rhDict[mon][cyid] += rh
			cntDict[mon][cyid] += 1
		for mon in rhDict.keys():
			for cyid in rhDict[mon].keys():
				avgrhDict[mon][cyid] = rhDict[mon][cyid]/cntDict[mon][cyid]
		return avgrhDict

	def create_rates_fromPL(self,month,cyid,rateInput,rateOutput,fixed_Rh,rtype):
		rpdDict ={}
		rpvDict ={}
		self.month = month
		self.rtype = rtype
		self.rateInput = rateInput
		self.rateOutput = rateOutput
		self.cyid = cyid
		self.fixed_Rh = fixed_Rh
		print ("creating %s files for %s month and for %s county"%(rtype,month,cyid)) 
		month = str(list(calendar.month_abbr).index(month))
		f = open(rateInput,'rb')
		year = '2012';dy =5
		tempLst =[0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120]
		#tempLst = [0,68,69,70,72,75,76,77,78,79,80,82,84,88,90,92,94,95,96,97,100]
		spdLst =[]
		for s in xrange(1,17):
			spdLst.append(s)
		rpdout = open(rateOutput,'wb')
		writer = csv.writer(rpdout,delimiter = ',')
		if not rpdDict.has_key(year):
			rpdDict[year] = {}
		if not rpdDict[year].has_key(month):
			rpdDict[year][month] = {}
		if not rpdDict[year][month].has_key(cyid):
			rpdDict[year][month][cyid] = {}
			for t in tempLst:
				if not rpdDict[year][month][cyid].has_key(t):
					rpdDict[year][month][cyid][t]= {}
				for scc in self.sccDict.values():
					prc = list([key for key, value in self.sccDict.iteritems() if value == scc][0])[2]
					smkPrc = self.nprocDict[prc][1]
					if smkPrc in ['EXR','BRK','TIR','CXR']:
						if not rpdDict[year][month][cyid][t].has_key(scc):
							rpdDict[year][month][cyid][t][scc]= {}
						if not rpdDict[year][month][cyid][t][scc].has_key(smkPrc):
							rpdDict[year][month][cyid][t][scc][smkPrc]= {}
							for dummySpd in xrange(1,17):
								if not rpdDict[year][month][cyid][t][scc][smkPrc].has_key(dummySpd):
									rpdDict[year][month][cyid][t][scc][smkPrc][dummySpd] = {}
								if not rpdDict[year][month][cyid][t][scc][smkPrc][dummySpd].has_key(fixed_Rh):
									rpdDict[year][month][cyid][t][scc][smkPrc][dummySpd][fixed_Rh] = {}
								for p in ['HC','CO','NOx','TOG','SOx','PMEX']:
									if not rpdDict[year][month][cyid][t][scc][smkPrc][dummySpd][fixed_Rh].has_key(p):
										rpdDict[year][month][cyid][t][scc][smkPrc][dummySpd][fixed_Rh][p] = 0.0
					else:
						pass 
		rpvout = open(rateOutput,'wb')
		rpwriter = csv.writer(rpvout,delimiter = ',')
		if not rpvDict.has_key(year):
			rpvDict[year] = {}
		if not rpvDict[year].has_key(month):
			rpvDict[year][month] = {}
		if not rpvDict[year][month].has_key(cyid):
				rpvDict[year][month][cyid] = {}
		for t in tempLst:
			if not rpvDict[year][month][cyid].has_key(t):
				rpvDict[year][month][cyid][t] = {}
			for dy in [2,5]:
				if not rpvDict[year][month][cyid][t].has_key(dy):
					rpvDict[year][month][cyid][t][dy] = {}
				for scc in self.sccDict.values():
					prc = list([key for key, value in self.sccDict.iteritems() if value == scc][0])[2]
					smkPrc = self.nprocDict[prc][1]
					if smkPrc in ['EXS','EXT','CXS','CEI','EFL','EVP','EFV']:
						if not rpvDict[year][month][cyid][t][dy].has_key(scc):
							rpvDict[year][month][cyid][t][dy][scc] = {}
						if not rpvDict[year][month][cyid][t][dy][scc].has_key(smkPrc):
							rpvDict[year][month][cyid][t][dy][scc][smkPrc] = {}
						for hr in xrange(1,25):
							if not rpvDict[year][month][cyid][t][dy][scc][smkPrc].has_key(hr):
								rpvDict[year][month][cyid][t][dy][scc][smkPrc][hr] = {}
							for p in ['HC','CO','NOx','TOG','SOx','PMEX']:
								if not rpvDict[year][month][cyid][t][dy][scc][smkPrc][hr].has_key(p):
									rpvDict[year][month][cyid][t][dy][scc][smkPrc][hr][p] = 0.0
		reader = csv.reader(f)
		headers = reader.next()
		for row in reader:
			""" create a dictionary of variables and values"""
			val = dict(zip (headers,row))

			try:
				'''cal_year,Area,month,veh_category_name,Temperature,Rhum,\
				process_id,speed_time,cat_id,pol_id,ER'''
				yearID = val['cal_year']
				monthID = val['month']
				fips = 6000+CNTY[val['Area'].split("(")[0].strip().upper()]
				old_emfac_veh = val['veh_category_name'].upper()
				ttmp = val['Temperature']
				fuel = self.catDict[val['cat_id']]
				procName = self.procDict[val['process_id']][0]
				smkProcName = self.procDict[val['process_id']][1]
				Rhum = val['Rhum']
				polName = POL_NAME[int(val['pol_id'])]
				if  procName == 'RUNEX':
					avgSpdBin = int(self.spdDict[(str(int(val['speed_time'])-5),val['speed_time'])])
				else:
					avgSpdBin = 0
				ems = float(val['ER'])
			except:
				pdb.set_trace()
				'''calendar_year,season_month,sub_area,vehicle_class,fuel,\
				temperature,relative_humidity,process,speed_time,pollutant,emission_rate'''
				yearID = val['calendar_year']
				monthID = val['season_month']
				fips = 6000+CNTY[val['sub_area'].split("(")[0].strip().upper()]
				old_emfac_veh = val['vehicle_class'].upper()
				fuel = self.catDict[val['fuel']]
				procName = self.procDict[val['process']][0]
				smkProcName = self.procDict[val['process']][1]
				ttmp = val['temperature']
				Rhum = val['relative_humidity']
				if  procName == 'RUNEX':
					avgSpdBin = int(self.spdDict[(str(int(val['speed_time'])-5),val['speed_time'])])
				else:
					avgSpdBin = 0
				polName = val['pollutant']
				ems = float(val['emission_rate'])
			if fips != cyid:
				continue
			if fuel not in ['CAT','NCAT','DSL']:
				continue
			if Rhum not in [fixed_Rh,'None']:
				continue
			if procName not in ['RUNEX','PMBW','PMTW']:
				if procName =='STREX':
					relHum = fixed_Rh
					sccSmoke = self.sccDict[(old_emfac_veh,fuel.upper(),procName,str(val['speed_time']))]
				else:
					relHum = fixed_Rh
					sccSmoke = self.sccDict[(old_emfac_veh,fuel.upper(),procName,str(avgSpdBin))]
			else:
				try:
					ems = ems/int(val['speed_time'])
				except:
					continue
				if procName in ['PMBW','PMTW']:
					relHum = fixed_Rh
				else:
					relHum = Rhum
				'''To facilitate discrepancy in ERP files'''
				sccSmoke = self.sccDict[(old_emfac_veh,fuel.upper(),procName,str(avgSpdBin))]

			if avgSpdBin > 16:
				continue 
			if ttmp =='None':
				temp = tempLst
			else:
				temp = int(ttmp)
				if temp not in tempLst:
					continue
			if procName =='RUNLOSS':
				avgSpdBin = spdLst
			if polName in ['PM2_5','ROG','CH4','PM10','CO2']:
				continue
			flDict = {'CAT':'GAS','NCAT':'GAS','DSL':'DSL'}
			if procName in ['RUNEX','PMBW','PMTW','RUNLOSS']:
				if procName == 'RUNEX' :
					for spd in xrange(1,17):
						rpdDict[yearID][monthID][fips][temp][sccSmoke][smkProcName][spd][relHum][polName] = ems

				elif procName == 'RUNLOSS':
					for spd in avgSpdBin:
						rpdDict[yearID][monthID][fips][temp][sccSmoke][smkProcName][spd][relHum][polName] = ems
				elif procName in ['PMBW','PMTW']:
					spd = int(self.spdDict[(str(int(val['speed_time'])-5),val['speed_time'])])
					if spd ==1:
						for tt in temp:
							for Nspd in xrange(1,17):
								if self.dutyDict[(old_emfac_veh,flDict[fuel])] == 'HEAVY DUTY':
									if old_emfac_veh == 'T7 SWCV':
										rpdDict[yearID][monthID][fips][tt][sccSmoke][smkProcName][Nspd][relHum][polName] = ems * 1.089
									elif old_emfac_veh == 'UBUS':
										rpdDict[yearID][monthID][fips][tt][sccSmoke][smkProcName][Nspd][relHum][polName] = 0.012
									else:
										rpdDict[yearID][monthID][fips][tt][sccSmoke][smkProcName][Nspd][relHum][polName] = ems
								else:
									if old_emfac_veh == 'UBUS' and smkProcName == 'TIR':
										rpdDict[yearID][monthID][fips][tt][sccSmoke][smkProcName][Nspd][relHum][polName] = 0.012
									elif old_emfac_veh == 'UBUS' and smkProcName == 'BRK' :
										if fuel == 'DSL':
											rpdDict[yearID][monthID][fips][tt][sccSmoke][smkProcName][Nspd][relHum][polName] = 0.859
										else:
											rpdDict[yearID][monthID][fips][tt][sccSmoke][smkProcName][Nspd][relHum][polName] = 0.133
									else:
										rpdDict[yearID][monthID][fips][tt][sccSmoke][smkProcName][Nspd][relHum][polName] = ems * 2 

					else:
						continue
				else:
					continue
			elif procName=='IDLEX':
				for dayID in [2,5]:
					for tt in temp:
						for hrID in xrange(1,25):
							rpvDict[yearID][monthID][fips][tt][dayID][sccSmoke][smkProcName][hrID][polName] = ems

			elif procName=='HOTSOAK' or procName=='STREX':
				if procName=='STREX':
					for dayID in [2,5]:
						for hrID in xrange(1,25):
							#frac = self.soakHrdistDict[(old_emfac_veh,fuel.upper())][val['speed_time']][hrID]
							rpvDict[yearID][monthID][fips][temp][dayID][sccSmoke][smkProcName][hrID][polName] = ems 
				else:
					for dayID in [2,5]:
						for hrID in xrange(1,25):
							rpvDict[yearID][monthID][fips][temp][dayID][sccSmoke][smkProcName][hrID][polName] = ems

			elif procName in ['PRESTLOSS','MDRESTLOSS','PDIURN','MDDIURN']:
				for dayID in [2,5]:
					for hrID in xrange(1,25):
						rpvDict[yearID][monthID][fips][temp][dayID][sccSmoke][smkProcName][hrID][polName] += ems
			else:
				continue
		f.close()
		if rtype == 'RPD':
			'''Writing of RPD Emission Rates'''
			'''One more loop needed to calculate temperature bins'''
			rpwriter.writerow(['NUM_TEMP_BIN 25'])
			rpwriter.writerow(['MOVESScenarioID','yearID','monthID','FIPS','SCCsmoke','smokeProcID','avgSpeedBinID','temperature','relHumidity','THC','CO','NOX','TOG','SOX','PM'])
			for yearID in rpdDict:
				for monthID in rpdDict[yearID]:
					for fips in rpdDict[yearID][monthID]:
						for temp in sorted(rpdDict[yearID][monthID][fips]):
							for sccSmoke in sorted(rpdDict[yearID][monthID][fips][temp]):
								for smkProcName in sorted(rpdDict[yearID][monthID][fips][temp][sccSmoke]):
									for avgSpdBin in sorted(rpdDict[yearID][monthID][fips][temp][sccSmoke][smkProcName]):
										for relHum in sorted(rpdDict[yearID][monthID][fips][temp][sccSmoke][smkProcName][avgSpdBin]):
												values =[0.0,0.0,0.0,0.0,0.0,0.0]
												pos={'HC':0,'CO':1,'NOx':2,'TOG':3,'SOx':4,'PMEX':5}
												for pol,ems in rpdDict[yearID][monthID][fips][temp][sccSmoke][smkProcName][avgSpdBin][relHum].items():
													if pol not in ['CO2','EVAP','FUEL']:
														values[pos[pol]] = ems
												line = ['RD_060'+str((int(cyid)*2)-1)+'_2012_6_T30_110',yearID,monthID,fips,sccSmoke,smkProcName,avgSpdBin,temp,relHum]+values
												rpwriter.writerow(line)
		rpdout.close()
		if rtype == 'RPV':
			'''Writing of RPD Emission Rates'''
			'''One more loop needed to calculate temperature bins'''
			rpwriter.writerow(['NUM_TEMP_BIN 25'])
			rpwriter.writerow(['MOVESScenarioID','yearID','monthID','dayID','hourID','FIPS','SCCsmoke','smokeProcID','temperature','THC','CO','NOX','TOG','SOX','PM'])
			for yearID in rpvDict:
				for monthID in rpvDict[yearID]:
					for fips in sorted(rpvDict[yearID][monthID]):
						for temp in sorted(rpvDict[yearID][monthID][fips]):
							for dayID in sorted(rpvDict[yearID][monthID][fips][temp]):
								for sccSmoke in sorted(rpvDict[yearID][monthID][fips][temp][dayID]):
									for smkProcName in sorted(rpvDict[yearID][monthID][fips][temp][dayID][sccSmoke]):
										for hr in sorted(rpvDict[yearID][monthID][fips][temp][dayID][sccSmoke][smkProcName]):
												values =[0.0,0.0,0.0,0.0,0.0,0.0]
												pos={'HC':0,'CO':1,'NOx':2,'TOG':3,'SOx':4,'PMEX':5}
												for pol,ems in rpvDict[yearID][monthID][fips][temp][dayID][sccSmoke][smkProcName][hr].items():
													if pol not in ['CO2','EVAP','FUEL']:
														try:
															values[pos[pol]] = ems
														except:
															values[pos[pol]] = ems
												"""Only one Relative Humidity is needed this should be read from MET4MOVES output in future"""
												line = ['RV_060'+str((int(cyid)*2)-1)+'_2012_6_T30_110',yearID,monthID,dayID,hr,fips,sccSmoke,smkProcName,temp]+values
												rpwriter.writerow(line)
		rpvout.close()

	def frac_mbinv(self,activfile):
		'''1. RUNEX process has to be seperated and VMT fractions are generated sperately
		2. Calculating SPEED distributions and applying on top of them'''
		activFracDict = {}
		self.activfile = activfile
		'''The DSL trips are missing from activity inputs, so, it may cause some descrepancies in start and hot soak emissions'''
		f = open(activfile,'rb')
		reader = csv.reader(f)
		headers = reader.next()
		try:
			for row in reader:
				''' create a dictionary of variables and values'''
				val = dict(zip (headers,row))
				'''cal_year,Area,veh_category_name,cat_id,activity_process,Frac'''
				year = val['cal_year']
				cnty = val['Area'].strip()
				vehType = val['veh_category_name']
				activity = val['activity_process'].upper()
				if activity == 'TRIP':activity = 'TRIPS'
				fuel = self.catDict[val['cat_id']]
				Frac = float(val['Frac'])
				if not activFracDict.has_key(activity):activFracDict[activity] = {}
				for process in assocactivDict[activity]:
					if not activFracDict[activity].has_key((vehType,fuel,process)):
						activFracDict[activity][(vehType,fuel,process)] = 0.0
					activFracDict[activity][(vehType,fuel,process)] += Frac 
		except ValueError:
			print "Not correct activity fractions values"""
			SystemExit
		for activity in ['VMT','TRIPS']:
			chk_tot={}
			for vtype,fuel,process in activFracDict[activity]:
				if not chk_tot.has_key(process):
					chk_tot[process] = {}
				if not chk_tot[process].has_key(vtype):
					chk_tot[process][vtype] = 0.0
				chk_tot[process][vtype] += activFracDict[activity][(vtype,fuel,process)]
				'''Print check fraction totals '''
		return  activFracDict
	'''This method is used to create the speed fractions for Running Exhaust Emissions
		if VMT is not supplied by speed'''
	def frac_speed(self,emisInput,cntyName):
		spdFracDict = {}
		self.emisInput = emisInput
		self.cntyName = cntyName 
		fuelbysccTotal = {}
		fuelTotal = {}
		self.emisInput = emisInput
		'''The DSL trips are missing from activity inputs, so, it may cause 
		some descrepancies in start and hot soak emissions'''
		f = open(emisInput,'rb')
		reader = csv.reader(f)
		headers = reader.next()

		for vtype in self.emfacDict.keys():
			for fuel in ['CAT','NCAT','DSL']:
					if vtype =='MCY' and fuel=='DSL':continue
					if not fuelTotal.has_key(vtype):
						fuelTotal[vtype] = {}
						fuelbysccTotal[vtype] = {}
					if not fuelbysccTotal[vtype].has_key(fuel):
						fuelTotal[vtype][fuel] = 0.0
						fuelbysccTotal[vtype][fuel] = {}
					for allspd in xrange(1,17):
						allspd = str(allspd)
						try:nsccSmoke = self.sccDict[(vtype,fuel,'RUNEX',allspd)]
						except: continue
						if not fuelbysccTotal[vtype][fuel].has_key(nsccSmoke):
							fuelbysccTotal[vtype][fuel][allspd] = 0.0
		try:
			for row in reader:
				''' create a dictionary of variables and values'''
				val = dict(zip (headers,row))
				'''calendar_year,season_month,sub_area,vehicle_class,fuel,speed,process,cat_ncat,pollutant,emission'''
				year = val['calendar_year']
				cnty = val['sub_area'].split("(")[0].strip().upper()
				if cnty == cntyName:
					#vehType = self.emfacDict[val['vehicle_class'].upper()]
					vehType = val['vehicle_class'].upper()
					#process = val['process']
					process = 'RUNEX'
					#polName = val['pollutant']
					fuel = val['cat_ncat'].upper()
					#if polName =='CO' and process =='RUNEX':
					speed = int(val['speed'])
					spdbin = self.spdDict[(str(speed-5),str(speed))]
					if int(spdbin) >13 :spdbin ='13'
					sccSmoke = self.sccDict[(vehType,fuel,process,spdbin)]
					qnty = float(val['vmt'])
					fuelbysccTotal[vehType][fuel][spdbin] += qnty
					fuelTotal[vehType][fuel] += qnty
		except ValueError:
			print "Not correct fuel vales for emission calculation"""
			SystemExit
		chk_tot = {}
		for vtype in fuelbysccTotal:
			for fuel in fuelbysccTotal[vtype]:
				for spd in sorted(fuelbysccTotal[vtype][fuel]):
					try:
						spdFracDict[(vtype,fuel,spd)] = fuelbysccTotal[vtype][fuel][spd]/fuelTotal[vtype][fuel]
					except:
						spdFracDict[(vtype,fuel,spd)] = 0.0
		'''To check speed fractions are correct or not'''
		for vtype,fuel,spd in spdFracDict:
			if not chk_tot.has_key(vtype):
				chk_tot[vtype] = {}
			if not chk_tot[vtype].has_key(fuel):
				chk_tot[vtype][fuel]= 0.0
			chk_tot[vtype][fuel] += spdFracDict[(vtype,fuel,spd)]
		'''renormalize fractions for better accuracy'''
		for vtype,fdic in chk_tot.items():
			for fuel,val in fdic.items():
				if round(val) != 1.0:
					print "processing speed fractions"
		return  spdFracDict

	def read_activity(self,activInput,cntyName):
		self.activInput = activInput
		self.cntyName = cntyName
		factiv = open(activInput, 'rb')
		reader = csv.reader(factiv)
		headers = reader.next()
		activtot = {}
		tot = 0.0
		try:
			for row in reader:
				"""calendar_year,sub_area,vehicle_class,fuel,speed,cat_ncat,vmt/trips"""
				val = dict(zip(headers,row))
				county = (val['sub_area'].strip().split("(")[0]).strip().upper()
				if county != cntyName:
					continue
				fuel = val['cat_ncat'].upper()
				if fuel not in ['CAT','NCAT','DSL']:
					continue
				vehType = val['vehicle_class'].upper()
				if 'vmt' in activInput:
					activity = float(val['vmt']) * 366.0
					"""To make daily activity to yearly"""
					if not activtot.has_key((vehType,fuel)):
						activtot[(vehType,fuel)] = 0.0
					tot += activity/365
				elif 'trips' in activInput:
					activity = float(val['trips']) 
					if not activtot.has_key((vehType,fuel)):
						activtot[(vehType,fuel)] = 0.0
				else:
					activity = float(val['population'])
					if not activtot.has_key((vehType,fuel)):
						activtot[(vehType,fuel)] = 0.0
				activtot[(vehType,fuel)] += activity
					
		except ValueError:
			print "Activity file reading error.. check the format or heading!!"""
			SystemExit

		factiv.close()

		return activtot

	def idle_activity(self,cnty):
		self.cnty = cnty
		fIdle = open(inputs+'/emission_rates/erp/jan/activity_idle_hours.csv','rb')
		reader = csv.reader(fIdle)
		headers = reader.next()
		idletot = {}
		try:
			for row in reader:
				"""calendar_year,sub_area,vehicle_class,fuel,speed,cat_ncat,vmt/trips"""
				val = dict(zip(headers,row))
				activity = float(val['Idle_Hours'])
				vehType,fuel = self.vccDict[val['VCC']][0][0]
				if not idletot.has_key((vehType,fuel)):
					idletot[(vehType,fuel)] = 0.0
				idletot[(vehType,fuel)] += activity
		except ValueError:
			print "Idle hours file reading error.. check the format or heading!!"""
			SystemExit
		fIdle.close()
		return idletot

	def write_activity(self,activTot,spdFrac,mbActiv,flag,header,cnty):
		self.activTot  = activTot
		self.mbActiv = mbActiv
		self.flag = flag
		self.spdFrac = spdFrac
		self.cnty = cnty
		self.header = header
		ndict = {'CAT':'GAS','NCAT':'GAS','DSL':'DSL'}

		if os.path.exists(mbActiv):
			fmbActiv = open(mbActiv,'a')
			writer = csv.writer(fmbActiv,delimiter = ',')
		else:
			fmbActiv = open(mbActiv,'w')
			writer = csv.writer(fmbActiv,delimiter = ',')
			fmbActiv.write(header+'\n')

		if flag =='vmt':
			for veh,fuel,proc,spd in self.sccDict.keys():
				'''PM related SCCs are calculated in seperate loop'''
				if proc in ['PMBW','PMTW']:
					sccSmoke = self.sccDict[(veh,fuel,proc,spd)]
					try:
						splitActiv = activTot[(veh,fuel)]
					except:
						splitActiv = 0.0
				elif proc == 'RUNEX':
					sccSmoke = self.sccDict[(veh,fuel,proc,str(spd))]
					try:
						splitActiv = activTot[(veh,fuel)]*spdFrac[(veh,fuel,str(spd))]
					except:
						splitActiv = 0.0
				else:
					splitActiv = 0.0
					continue
				if splitActiv <> 0.0:
					line = ['US',str(CNTY[cnty.upper()]+6000).rjust(5,'0'),'','','',str(sccSmoke),'','MILES',flag.upper(),splitActiv,2012,'','']
					line.extend(map(lambda x : 0.0,[splitActiv for x in xrange(12)]))
					writer.writerow(line)

		if flag =='speed':
			for veh in set(self.emfacDict.keys()):
				for fuel in ['CAT','NCAT','DSL']:
					if veh == 'MCY' and fuel == 'DSL':
						continue
					for spdbin in xrange(1,17):
						try:
							sccSmoke = self.sccDict[(veh,fuel,'RUNEX',str(spdbin))]
						except:
							continue
						spd = list([key for key, value in self.spdDict.iteritems() if value == str(spdbin)][0])[0]
						avgspd = int(spd)+2.5
						line = ['US',str(CNTY[cnty.upper()]+6000).rjust(5,'0'),'','','',str(sccSmoke),'','MPH',flag.upper(),str(avgspd),2012,'','']
						line.extend(map(lambda x : x,[avgspd for x in xrange(12)]))
						line.extend(['Prepared from Emfac'])
						writer.writerow(line)

		if flag =='trips':
			soak_dist = 0.0
			for veh,fuel,proc,spd in sorted(self.sccDict.keys()):
				if proc == 'HOTSOAK' and fuel <> 'DSL' :
					sccSmoke = self.sccDict[(veh,fuel,proc,spd)]
					try:
						splitActiv = activTot[(veh,fuel)] * 1/24
						#print veh, fuel,proc,spd,splitActiv
					except:
						splitActiv = 0.0
				elif proc == 'STREX' and fuel <> 'DSL':
					#for soak_time in [5,10,20,30,40,50,60,120,180,240,300,360,420,480,540,600,660,720]:
					soak_time = spd
					sccSmoke = self.sccDict[(veh,fuel,proc,soak_time)]
					try:
						if veh <> 'SBUS':
							# To mimic  what population based emission process doing 
							splitActiv = activTot[(veh,fuel)] * self.soakdistDict[(veh,'GAS')][soak_time] *1/24 
						elif veh == 'SBUS':
							splitActiv = activTot[(veh,fuel)] * self.soakdistDict[(veh,'GAS')][soak_time] *1/24 *2.5
					except:
						splitActiv = 0.0
				else:
					splitActiv = 0.0
					continue
				if splitActiv <> 0.0:
					line = ['US',str(CNTY[cnty.upper()]+6000).rjust(5,'0'),'','','',str(sccSmoke),'','',"VPOP",splitActiv,2012,'','']
					line.extend(map(lambda x:0,[splitActiv for x in xrange(12)]))
					line.extend(['Prepared from Emfac'])
					writer.writerow(line)

		if flag == 'population' :
			#idletot = self.idle_activity(cnty)
			cnt1 = 0
			for veh,fuel,proc,spd in self.sccDict.keys():
				veh07= self.emfacDict[veh.upper()]
				if proc == 'RUNLOSS':
					continue
				sccSmoke = self.sccDict[(veh,fuel,proc,spd)]
				''' since there is nor direct correspondence between retsloss in EMFAC to MOVES types
				we artifically adjusting activity'''
				if proc in ['PRESTLOSS','MDRESTLOSS','PDIURN','MDDIURN']:
					if proc =='PRESTLOSS' and fuel <> 'DSL':
						try:
							splitActiv = activTot[(veh,fuel)]
							cnt1 += splitActiv 
						except:
							continue
					else:
						splitActiv = 0.0
				elif proc =='IDLEX':
					try:
						"""  idle hours = Average HD idle hour * population * hd_percent in ca"""
						try:
							#splitActiv = activTot[(veh,fuel)] * self.TotIdActiv[cnty.upper()][(veh,ndict[fuel])] *1/366 * self.hdCaPct[veh]
							splitActiv = activTot[(veh,fuel)] 
						except:
							#splitActiv = activTot[(veh,fuel)] * self.TotIdActiv[cnty.upper()][(veh,ndict[fuel])] *1/366 
							splitActiv = activTot[(veh,fuel)] 
					except:
						continue
				else:
					splitActiv = 0.0
	
				if splitActiv <> 0.0:
					line = ['US',str(CNTY[cnty.upper()]+6000).rjust(5,'0'),'','','',str(sccSmoke),'','',"VPOP",splitActiv,2012,'','']
					line.extend(map(lambda x : 0,[splitActiv for x in xrange(12)]))
					line.extend(['Prepared from Emfac'])
					writer.writerow(line) 

		if flag == 'veh_run_hour_ld':
			for veh,fuel,proc,spd in self.sccDict.keys():
				if proc == 'RUNLOSS':
					sccSmoke = self.sccDict[(veh,fuel,proc,spd)]
					#veh07= self.emfacDict[veh.upper()]
					#if veh07 not in ['HHDT','MHDT','OBUS','SBUS']:
					#	"""LD Vehicle running hours = OperatingHour * starts(trips)"""
					try:
						splitActiv = activTot[(veh,fuel)] * self.ldOpDict[(veh,ndict[fuel])] *1/self.wkdayFact[(veh,ndict[fuel])]*366
					except:
						splitActiv = 0.0
				else:
					splitActiv = 0.0
					continue
				if splitActiv <> 0.0:
					line = ['US',str(CNTY[cnty.upper()]+6000).rjust(5,'0'),'','','',str(sccSmoke),'','',"VMT",splitActiv,2012,'','']
					line.extend(map(lambda x : 0,[splitActiv for x in xrange(12)]))
					line.extend(['Prepared from Emfac'])
					writer.writerow(line)

		if flag == 'veh_run_hour_hd':
			for veh,fuel,proc,spd in self.sccDict.keys():                    
				if proc == 'RUNLOSS':
					sccSmoke = self.sccDict[(veh,fuel,proc,spd)]
					#veh_2007 = self.emfacDict[veh.upper()]
					#if veh_2007 in ['HHDT','MHDT','OBUS','SBUS']:
					#	"""HD Vehicle running hours = OperatingHour * population, since operating hours are by days """
					try:
						try:
							splitActiv = activTot[(veh,fuel)] * self.hdOpDict[(veh,ndict[fuel])] * self.hdCaPct[(veh,ndict[fuel])]*self.wkdayFact[(veh,ndict[fuel])]
						except:
							splitActiv = activTot[(veh,fuel)] * self.hdOpDict[(veh,ndict[fuel])] 
					except:
						continue
				else:
					splitActiv = 0.0
				if splitActiv <> 0.0:
					line = ['US',str(CNTY[cnty.upper()]+6000).rjust(5,'0'),'','','',str(sccSmoke),'','',"VMT",splitActiv,2012,'','']
					line.extend(map(lambda x : 0,[splitActiv for x in xrange(12)]))
					line.extend(['Prepared from Emfac'])
					writer.writerow(line) 
		fmbActiv.close()

	def create_mbinv(self,activIn,activOut,spdFrac,activType,header,cnty):
		""" This method applies fractions to the total VMT obtained from frac_mbinv method"""
		""" Also creates Speed mbinv file"""
		self.activIn = activIn 
		self.activOut = activOut
		self.spdFrac = spdFrac
		self.cnty = cnty
		activDict = self.read_activity(activIn,cnty)
		self.header = header
		self.activType = activType
		print "Creating %s related mbinv file "%activType
		self.write_activity(activDict,spdFrac,activOut,activType,header,cnty)
        
	def create_temporal(self,fwkfactor,fhrfactor,flkupscc,fmtref,fmprof):
		'''This method used SMOKE ready MTPRO file using CALVAD fractions'''
		self.lkupscc = flkupscc
		self.fmtref = fmtref
		self.fmprof = fmprof
		self.fwkfactor = fwkfactor
		self.fhrfactor = fhrfactor
		#lkupscc = open (flkupscc,"r")
		mref = open (fmtref,"w")
		mpro = open (fmprof,"a")
		"""SCC month code  week code diurnal code"""
		code_dict ={}
		scc_dict={}
		hrfact_dict = {}
		wkfact_dict = {}
		wkfactor = open(fwkfactor, 'rb')
		reader = csv.reader(wkfactor)
		headers = reader.next()
		for row in reader:
			val = dict(zip(headers,row))
			fips = CNTY[val['CNTY'].upper()]
			day = val['DAY']
			if day == '8':
				continue
			if day == '1': 
				day = '7'
			else:
				day = str(int(day)-1)
			for vtypes in ['LD','LM','HH']:
				if not wkfact_dict.has_key(fips):
					wkfact_dict[fips] = {}
				if not wkfact_dict[fips].has_key(vtypes):
					wkfact_dict[fips][vtypes] = {}
				wkfact_dict[fips][vtypes][day]= round(float(val[vtypes])*100)
				try:
					wkfact_dict[fips][vtypes]['3'] = wkfact_dict[fips][vtypes]['2']
				except:
					continue
				try:
					wkfact_dict[fips][vtypes]['4'] = wkfact_dict[fips][vtypes]['2']
				except:
					continue
		hrfactor = open(fhrfactor, 'rb')
		#To read District Look Up for Caltrans factors
		dstr = open('/aa/hperugu/SMOKE_EMFAC/inputs/cfnd.csv','rb')
		dstRead = csv.reader(dstr)
		dstHead = dstRead.next()
		DstrDict = {}
		for line in dstRead:
			val = dict(zip(dstHead,line))
			dist = val['DISTRICT']
			fips = val['FIPS']
			if not DstrDict.has_key(dist):
				DstrDict[dist] = []
			DstrDict[dist].append(fips)
		reader2 = csv.reader(hrfactor)
		headers2 = reader2.next()
		for row in reader2:
			val = dict(zip(headers2,row))
			#fips = CNTY[val['CNTY'].upper()]
			dist = val['DSTR']
			day = val['DAY']
			if day not in ['1','3']:
				continue
			hr = int(val['HR'])
			#For Calvad data first loop has to be removed
			for fips in DstrDict[dist]:
				fips = int(fips)
				for vtypes in ['LD','LM','HH']:
					if not hrfact_dict.has_key(fips):
						hrfact_dict[fips] = {}
					if not hrfact_dict[fips].has_key(vtypes):
						hrfact_dict[fips][vtypes] = {}
					if not hrfact_dict[fips][vtypes].has_key(day):
						hrfact_dict[fips][vtypes][day] = {}
					hrfact_dict[fips][vtypes][day][hr] = round(float(val[vtypes]))
		emfac2caltr = {'LDA':'LD','LDT1':'LD','LDT2':'LD','MDV':'LM','LHDT1':'LM','LHDT2':'LM','MHDT':'HH','OBUS':'LM','UBUS':'LM','MCY':'LD','SBUS':'LM','MH':'HH','HHDT':'HH'}
		emfachrFact_dict = {}
		reader3 = csv.reader(open('/aa/hperugu/SMOKE_EMFAC/inputs/hourly_dist.emfac.csv','rb'))
		headers3 = reader3.next()
		for fips in range(1,115,2):
			for row in reader3:
				val = dict(zip(headers3,row))
				veh = val['Vehicle'].upper()
				fuel = val['Fuel'].upper()
				frac = float(val['VMT_frac']) * 10
				hr = val['Hour']
				for day in ['1','3']:
					if not emfachrFact_dict.has_key(fips):
						emfachrFact_dict[fips] = {}
					if not emfachrFact_dict[fips].has_key((veh,fuel)):
						emfachrFact_dict[fips][(veh,fuel)] = {}
					if not emfachrFact_dict[fips][(veh,fuel)].has_key(day):
						emfachrFact_dict[fips][(veh,fuel)][day] = {}
					emfachrFact_dict[fips][(veh,fuel)][day][hr] = round(frac)

		wkcnt = 0 ; wcode_dict = {}
		for fips in wkfact_dict.keys():
			hrcnt =0; hrcode_dict = {}
			with open (flkupscc) as lkupscc:
				for line in lkupscc:
					args=line.strip().split(",")
					fscc = args[4]
					veh = args[0]
					if args[1] in ['CAT','NCAT']:
						fuel = 'GAS'
					else:
						fuel = 'DSL'
					veh_2007 = self.emfacDict[veh.upper()]
					vtypes = emfac2caltr[veh_2007]
					if not (veh,fuel) in hrcode_dict.keys():
						hrcnt += 1
						hrcode = 3500+hrcnt
						hrcode_dict[(veh,fuel)] = hrcode
					if not (fips,vtypes) in wcode_dict.keys(): 
						wkcnt += 1
						wcode = 3000+wkcnt
						wcode_dict[(fips,vtypes)] = wcode
					line = fscc.ljust(10,' ')+','+'9100'+','+str(wcode)+','+str(hrcode)+',0,'+str(fips+6000).zfill(6)+',,0,,'+fscc.ljust(10,' ')+'\n'
					mref.write(line)

		mpro.write("/MONTHLY/\n")
		mpro.write(" 9100 100 100 100 100 100 100 100 100 100 100 100 100 1200\n")
		mpro.write("/END/\n")
		mpro.write("/WEEKLY/\n")
		for fips in wkfact_dict.keys():
			for vtypes in wkfact_dict[fips].keys():
				wcode = wcode_dict[(fips,vtypes)]
				fact = []
				tot = 0
				for day in sorted(wkfact_dict[fips][vtypes].keys()):
					#val = wkfact_dict[fips][vtypes][day]
					val = 100
					fact.append(int(val))
					tot += int(val)
				line = str(wcode).rjust(5,' ')+''.join([str(x).rjust(4,' ') for x in fact])+str(tot).rjust(6,' ')+'\n'
				mpro.write(line)
		mpro.write("/END/\n") 
		mpro.write("/DIURNAL WEEKDAY/\n")

		for fips in emfachrFact_dict.keys():
			for veh in self.emfacDict.keys():
				for fuel in ['GAS','DSL']:
					try:
						hrcode = hrcode_dict[(veh,fuel)]
					except:
						continue
					try:
						for day in emfachrFact_dict[fips][(veh,fuel)].keys():
							if day == '3':
								fact =[]
								tot = 0
								for hr in sorted(emfachrFact_dict[fips][(veh,fuel)][day].keys()):
									#val = emfachrFact_dict[fips][(veh,fuel)][day][hr]
									val = 100
									fact.append(int(val))
									tot += int(val)
					except:
						fact =[]
						tot = 0
						for hr in range(24):
							val = 100
							fact.append(int(val))
							tot += int(val)
					line = str(hrcode).rjust(5,' ')+''.join([str(x).rjust(4,' ') for x in fact])+str(tot).rjust(5,' ')+'\n'
					mpro.write(line)
		mpro.write("/END/\n")
		mpro.write("/DIURNAL WEEKEND/\n")
		for fips in emfachrFact_dict.keys():
			for veh in self.emfacDict.keys():
				for fuel in ['GAS','DSL']:
					try:
						hrcode = hrcode_dict[(veh,fuel)]
					except:
						continue
					try:
						for day in emfachrFact_dict[fips][(veh,fuel)].keys():
							if day == '3':
								fact =[]
								tot = 0
								for hr in sorted(emfachrFact_dict[fips][(veh,fuel)][day].keys()):
									val = 100
									#val = emfachrFact_dict[fips][(veh,fuel)][day][hr]
									fact.append(int(val))
									tot += int(val)
					except:
						fact =[]
						tot = 0
						for hr in range(24):
							val = 100
							fact.append(int(val))
							tot += int(val)
					line = str(hrcode).rjust(5,' ')+''.join([str(x).rjust(4,' ') for x in fact])+str(tot).rjust(5,' ')+'\n'
					mpro.write(line)
		mpro.write("/END/\n")
		mref.close()
		mpro.close()

	def create_mcodes(self,fproc_codes,fveh_codes,fscc_codes,fmcodes,foutput):
		self.fproc_codes = fproc_codes
		self.fveh_codes = fveh_codes
		self.fscc_codes = fscc_codes
		self.fmcodes = fmcodes
		self.foutput = foutput
		proc_codes_file = open(fproc_codes, 'r')
		finput = open(fscc_codes, 'r')
		veh_codes_file = open(fveh_codes, 'r')
		mcodes = open(fmcodes, 'w')
		output = open(foutput, 'w')
		args=[];veh_dict={}
		proc_dict={}
		code_dict ={}
		scc_dict={}
		for line in proc_codes_file.readlines():
			args=line.strip().split(",")
			proc_dict[(args[1])]=[args[0],args[5]]
		for line in veh_codes_file.readlines():
			args=line.strip().split(",")
			veh_dict[(args[0])]=args[1]
		j =0
		for line in finput.readlines():
			args=line.strip().split(",")
			nveh = args[4][2:6]
			j += 1
			nvehCode = args[1][0:4]+str(j).rjust(2,'0')
			if not code_dict.has_key((args[1])):
				code_dict[(args[1])]=[]
				i = 0
			else:
				i += 1
			code_dict[(args[1])].append([args[4],i,nveh,nvehCode])
		mcodes.write("/VEHICLE TYPES/\n")
		for veh in code_dict:
			for scc in code_dict[veh]:
				scc_dict[scc[0]]=[veh,scc[0][-3:]]
		for fscc,veh in scc_dict.items():
			j +=1
			mcodes.write(veh[0][0:3].ljust(4,'0')+str(j).rjust(3,'0')+' '+fscc[2:6]+' Y\n')

		for veh in code_dict.values():
			for h in xrange(len(veh)):
				output.write(veh[h][3].ljust(6)+' '+veh[h][2].rjust(4,'0')+' Y\n')
		mcodes.write("/ROAD CLASSES/\n")
		#for proc,nums in proc_dict.items():
		#    output.write (nums[1].rjust(3,'0')+' 01 Y\n')
		mcodes.write (" 1 01 Y\n")
		mcodes.write ("/SCC/\n")
		i=1
		output.write('8, "'+'(I003,1X,A006,1X,A002,1X,A001,1X,A004,1X,A010,1X,A005,1X,A002)'+'"\n'+
		'SMOKE Source ID\n'+
		'Cntry/St/Co FIPS\n'+
		'Process Type code\n'+
		'Link ID\n'+
		'Vehicle Type code\n'+
		'SCC\n'+
		'Vehicle Type Name\n'+
		'Source type code\n')
		for fscc,veh in scc_dict.items():
			mcodes.write (veh[1]+' '+veh[0].ljust(5)+' '+fscc+'\n')
			output.write(str(i).rjust(3)+' 006037 '+str(int(fscc[-3:])).rjust(2)+'  '+str(int(fscc[2:6])).rjust(4)+' '+fscc+' '+veh[0].rjust(5)+' 00\n')
			i +=1
		proc_codes_file.close()
		finput.close()
		veh_codes_file.close()
		mcodes.close()
		output.close()

def main():

	emisInput = inputs+'/activity/Deafault_State_activity_Jan_EMFAC11_catNcat_vmt.csv'
	mcodes = outputs+'/mcodes_emfac.txt'
	src = outputs+'/rateperdistance_noRFLsrc.txt'
	tempoRef = outputs+'/mref.emfac.ca.txt'
	tempoProf = outputs+'/mpro.emfac.ca.txt'
	fulmonProf = outputs+'/mfmref.emfac_st_4k.txt'
	gspro = gsProIn.split('.')
	gsref = gsRefIn.split('.')
	gspro.insert(1,'emfac')
	gsref.insert(1,'emfac')
	fgspr = '.'.join(gspro)
	fgsre = '.'.join(gsref)
	proc,veh,spd,dscc,scc,cat,emfac,nproc,hdOp,ldOp,totIdHr,soakdist,soakhr,hdact,wkfact,vccDict,dutyDict = lookupDict(fprocCodes,fvehCodes,catDict,dsccCodes,fspeedBins,emfac2Emfac,vcc)
	cntyFiles = emfac2smoke(fgspr,fgsre,proc,nproc,veh,spd,dscc,scc,cat,emfac,hdOp,ldOp,totIdHr,soakdist,soakhr,hdact,wkfact,vccDict,dutyDict)
	#cntyFiles.create_mfmref(fulmonProf)
	#cntyFiles.create_gs()
	#cntyFiles.create_temporal(fwkfactor,fhrfactor,dsccCodes,tempoRef,tempoProf)
	#cntyFiles.create_mcodes(fprocCodes,fvehCodes,dsccCodes,mcodes,src)
	SC_CNTY = {'LOS ANGELES':6037,'ORANGE':6059,'RIVERSIDE':6065, 'SAN BERNARDINO':6071} 
	[os.remove(x) for x in glob.glob("../outputs/mbinv.*")]
	#for conum,cnty in {'10':'Fresno'}.items():
	for conum,cnty in county_nums.items():
		start = datetime.now()
		#for activity in ["vmt","trips","population","veh_run_hour_ld","veh_run_hour_hd","speed"]:
		for activity in ["vmt","veh_run_hour_ld","veh_run_hour_hd","speed"]:
			cnty = cnty.upper()
			speedFrac = cntyFiles.frac_speed(emisInput,cnty)
			fips = 6000+int(conum)*2-1
			#print "Creating MBINV files for %s for activity %s"%(cnty,activity)
			activInput = inputs+'/activity/Deafault_State_activity_Jan_EMFAC11_catNcat_xxx.csv'
			mbInv = outputs+'/mbinv.xxx.emfac_st_4k.txt'
			if activity=="speed" or activity=="vmt" :
				mbActIn = activInput.replace("xxx","vmt")
			elif activity == "veh_run_hour_ld":
				mbActIn = activInput.replace("xxx","trips")
			elif activity == "veh_run_hour_hd" :
				mbActIn = activInput.replace("xxx","population")
			else:
				mbActIn = activInput.replace("xxx",activity)
			header = '#FORMAT=FF10_ACTIVITY\n'+'#COUNTRY  US\n'+'#YEAR     2012\n'+ '# units of ANN_PARM_VALUE are in total miles per year if it is VMT\n'+\
			'# COUNTRY_CD,REGION_CD,TRIBAL_CODE,CENSUS_TRACT_CD,SHAPE_ID,SCC,ACT_PARM_TYPE_CD,ACT_PARM_UOFMSR,'+\
			'ACTIVITY_TYPE,ANN_PARM_VALUE,CALC_YEAR,DATE_UPDATED,DATA_SET_ID,JAN_VALUE,FEB_VALUE,MAR_VALUE,APR_VALUE,MAY_VALUE,'+\
			'JUN_VALUE,JUL_VALUE,AUG_VALUE,SEP_VALUE,OCT_VALUE,NOV_VALUE,DEC_VALUE,COMMENT' 

			if activity=="trips":
				mbOut = mbInv.replace("xxx","TRIPS")
			elif activity=="population":
				mbOut = mbInv.replace("xxx","VPOP")
			elif activity=="speed":
				mbOut = mbInv.replace("xxx","SPEED")
			else:
				mbOut = mbInv.replace("xxx","VMT")
			cntyFiles.create_mbinv(mbActIn,mbOut,speedFrac,activity,header,cnty)
		#pdb.set_trace()
		rhDict = cntyFiles.read_rh(inputs+'TempRh.csv')
		for month in ['Jan','Jul']:
		#for month in ['Jul']:
			mo = str(list(calendar.month_abbr).index(month))
			conum = str(conum)
			fixed_Rh = str(int(rhDict[mo][conum]))
			cntyin= inputs+'emission_rates/erp/'+month.lower()+'/'+str(conum).zfill(2)+'_erp.csv'
			#cntyin= inputs+'emission_rates/PL_State_wide_jan_emfac11_emissionrates.csv'
			countyrpdOut = outputs+'rateperdistance_0'+str(fips)+'_'+month+'.txt'
			countyrpvOut = outputs+'ratepervehicle_0'+str(fips)+'_'+month+'.txt'
			#cntyFiles.create_rates_fromPL(month,fips,cntyin,countyrpdOut,fixed_Rh,'RPD')
			#cntyFiles.create_rates_fromPL(month,fips,cntyin,countyrpvOut,fixed_Rh,'RPV')
			print  datetime.now() -start 

if __name__ == "__main__":
    main()

