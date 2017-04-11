import pdb
input =open ("/bb/hperugu/SMOKE_EMFAC/lookups/lookup_table.csv","r")
output=open ("/bb/hperugu/SMOKE_EMFAC/outputs/mcodes_emfac_fakescc.txt","w")
args=[];code_dict={}
lookup={}
for line in input.readlines()[1:]:
    args=line.strip().split(",")
    lookup[args[0]]= args[3]
    if not code_dict.has_key((args[1])):
        code_dict[(args[1])]=[]
        i = 0
    else:
        i += 1
        code_dict[(args[1])].append([args[3],i])
print code_dict
print lookup
