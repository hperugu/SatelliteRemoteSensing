proc_codes_file = open ("/bb/hperugu/SMOKE_EMFAC/lookups/processid_comp.csv","r")
veh_codes_file = open ("/bb/hperugu/SMOKE_EMFAC/lookups/vehcodes.csv","r")
input = open ("/bb/hperugu/SMOKE_EMFAC/lookups/lookup_dtimSCC_newSCC_v1.csv","r")
mref = open ("/bb/hperugu/SMOKE_EMFAC/outputs/mref.emfac.ca.txt","w")
mpro = open ("/bb/hperugu/SMOKE_EMFAC/outputs/mref.emfac.ca.txt","w")
"""SCC month code  week code diurnal code"""
code_dict ={}
scc_dict={}
week_code = {'LD':3001,'LM':3002,'HH':3003}
diu_code = {'LD':3101,'LM':3102,'HH':3103}
emfac2caltr = {'LDA':'LD','LDT1':'LD','LDT2':'LD','MDV':'LM','LHDT1':'LM','LHDT2':'LM',\
'MHDT':'HH','OBUS':'LM','UBUS':'LM','MCY':'LD','SBUS':'LM','MH':'HH','HHDT':'HH'}

for line in input.readlines()[1:]:
    args=line.strip().split(",")
    fscc = args[4]; veh = args[1]
    code_dict[fscc] = veh
    
for scc,veh in code_dict.items():
	print scc, "9001",week_code[emfac2caltr[veh]],diu_code[emfac2caltr[veh]]       
	mref.write(scc.ljust(10,' ')+' '+'9001'+' '+str(week_code[emfac2caltr[veh]])+' '+str(diu_code[emfac2caltr[veh]])+'\n')
        
