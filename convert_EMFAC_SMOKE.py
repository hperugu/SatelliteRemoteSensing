
import pdb
input =open ("/aa/hperugu/from_jstilley/19_emission_rates_20150422101853.csv","r")
output=open ("/aa/hperugu/from_jstilley/EMFAC_SMOKE_2012_LA_RPD.csv","w")
proc_codes_file = open ("/aa/hperugu/from_jstilley/processid_comp.csv","r")
veh_codes_file = open ("/aa/hperugu/from_jstilley/vehcodes.csv","r")
scc_codes_file = open ("/aa/hperugu/from_jstilley/lookup_table.csv","r")
speed_bins_file = open ("/aa/hperugu/from_jstilley/speed_bins.csv","r")

cat_dict = {'CAT':'1','NCAT':'2','DSL':'3'}
proc_dict = {}
args=[]
rpd_dict={}
rpd_ndict={}
scc_dict={}
#pos={'CO':1,'NOX':2,'TOG':29,'FUEL':32,'PMEX':33}
pos={'CO':1,'NOX':2,'TOG':9}
POL_NAME = {1: 'HC', 2: 'CO', 3: 'NOX', 4: 'EVAP', 6: 'PMEX', 8: 'TOG', 10: 'CO2', 14: 'FUEL', -13: 'PMTW', -14: 'PMBW'}
speed_dict={}

for line in proc_codes_file.readlines():
    args=line.strip().split(",")
    proc_num=args[0];proc_name=args[1];smk_proc=args[5];type=args[4]
    proc_dict[(proc_num)]=[proc_name,smk_proc,type]

for line in scc_codes_file.readlines()[1:]:
    vals = line.strip().split(",")
    veh_name,tech_name,proc_name,fscc=vals[1:]
    tech_num = cat_dict[tech_name]
    for key,values in proc_dict.items():
        if values[0] == proc_name:
            proc_num = key
    scc_dict[(veh_name,tech_num,proc_num)]=fscc

for line in speed_bins_file.readlines()[1:]:
    vals = line.strip().split(',')
    speed_dict[(vals[1],vals[2])] = vals[0]

for line in input.readlines()[1:]:
    '''MOVESScenarioID,yearID,monthID,FIPS,SCCsmoke,smokeProcID,avgSpeedBinID,temperature,relHumidity'''
    args=line.strip().split(",")
    veh_name,temp,Rh,proc_num,spd,tech_num,pol_num,emis_rate=args[3:]
    if proc_num == '7' or proc_num =='8':
        proc_num = '9'
    if proc_num == '10' or proc_num =='11':
        proc_num = '12'
    tscc = scc_dict[veh_name,tech_num,proc_num]
    smk_proc = proc_dict[proc_num][1]
    pol_name=POL_NAME[int(pol_num)]
    type = proc_dict[proc_num][2]
    if type =='RPD' and spd <> 'NULL':
        for spd_rng,binid in speed_dict.items():
            if float(spd_rng[0])<= float(spd) < float(spd_rng[1]): 
                break
        spdBinid = binid
        if not rpd_dict.has_key((tscc,smk_proc,spdBinid,temp,Rh)):
            rpd_dict[(tscc,smk_proc,spdBinid,temp,Rh)]={}
        else:
            rpd_dict[(tscc,smk_proc,spdBinid,temp,Rh)][pol_name]=emis_rate
    else:
        continue

input.close()
proc_codes_file.close() 
scc_codes_file.close()
temp=[]
for n in range(17):
    temp.append("0")

for scc,pol in  rpd_dict.items():
    ntemp=list(temp)
    for pol,fac in rpd_dict[scc].items():
        if pol in pos.keys():
            ntemp[pos[pol]]=fac
        rpd_ndict[scc] =ntemp

for all,rate in rpd_ndict.items():
    frnt=['RD_06037_2012_1_T20_65','2012','6','6037']
    print (",".join([str(x) for x in frnt])+','+",".join([str(x) for x in all])+','+",".join([str(x) for x in rate]))
    oline = ",".join([str(x) for x in frnt])+','+",".join([str(x) for x in all])+','+",".join([str(x) for x in rate])+"\n"
    output.write(oline)
output.close()

