import pdb
proc_codes_file = open ("/bb/hperugu/SMOKE_EMFAC/lookups/processid_comp.csv","r")
veh_codes_file = open ("/bb/hperugu/SMOKE_EMFAC/lookups/vehcodes.csv","r")
input = open ("/bb/hperugu/SMOKE_EMFAC/lookups/lookup_dtimSCC_newSCC_v1.csv","r")
mcodes = open ("/bb/hperugu/SMOKE_EMFAC/outputs/mcodes_emfac.txt","w")
output = open ("/bb/hperugu/SMOKE_EMFAC/outputs/rateperdistance_noRFLsrc.txt","w")
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
for line in input.readlines()[1:]:
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
for veh in code_dict.keys():
    for scc in code_dict[veh]:
        scc_dict[scc[0]]=[veh,scc[0][-3:]]
for fscc,veh in scc_dict.items():
    j +=1
    output.write(veh[0][0:3].ljust(4,'0')+str(j).rjust(3,'0')+' '+fscc[2:6]+' Y\n')

for veh in code_dict.values():
    for h in range(len(veh)):
       # output.write(veh[h][3].ljust(6)+' '+veh[h][2].rjust(4,'0')+' Y\n')
       print h
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
    print fscc[-3:],fscc[2:6],veh[0].rjust(5)
    i +=1
mcodes.close()
