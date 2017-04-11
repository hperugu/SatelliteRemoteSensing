import pdb 
#mbinv_spd = open ("/aa/hperugu/from_jstilley/mbinv.SPEED.LA_4k.May2015.txt","r")
#mbinv_vmt = open ("/aa/hperugu/from_jstilley/mbinv.VMT.LA_4k.May2015.txt","r")
mbinv_emis = open ("/aa/hperugu/from_jstilley/Default_LosAngelesMD_LosAngelesSC_2012_Annual_emission_20150427154203.csv","r")
mbinv_vmt = open ("/aa/hperugu/from_jstilley/Default_LosAngelesMD_LosAngelesSC_2012_Annual_vmt_20150427154203.csv","r")
input = open ("/aa/hperugu/from_jstilley/lookup_table.csv","r")
emfac_lu = open("/aa/hperugu/from_jstilley/Emfac2Emfac.csv","r")
mbinv_spd_out = open ("/aa/hperugu/from_jstilley/mbinv.SPEED.LA_4k.May2015.new.txt","w")
mbinv_vmt_out = open ("/aa/hperugu/from_jstilley/mbinv.VMT.LA_4k.May2015.new.txt","w")
gsref_in = open ("/aa/hperugu/from_jstilley/gsref.25jun2014.2012.d","r")
gsref_out = open ("/aa/hperugu/from_jstilley/gsref.25jun2014.2012.new.d","w")
code_dict = {}
emfaic_dict = {}
vmt_dict = {}
for line in input.readlines()[1:]:
    args=line.strip().split(",")
    code_dict[(args[0])]=args[4]
for line in gsref_in.readlines():
    nargs = line.strip().split(",")
    if nargs[0] in code_dict.keys():
        nargs[0]= code_dict[nargs[0]]
        nLine = ",".join(nargs)+"\n"
    else:
        nLine = ",".join(nargs)+"\n"
    gsref_out.write(nLine)
'''create a EmfAc 2013 to Emfac 2007 Lookup Table'''
for line in emfac_lu.readlines()[1:]:
    emfac13,emfac7 = line.strip().split(',')
    emfac_dict[emfac13]=emfac[7] 

'''Read the VMT file first'''
for line in mbinv_vmt.readlines()[1:]:
    yr,cnty,em13,fl,spd,tech,vmt=line.strip().split(",")
    em7 = emfac_dict[em13]
    vmt_dict[(em7,tech)] += float(vmt)
'''Apply TOG emission based fractions to get SCC based VMT distribution'''

mbinv_spd_out.write('#FORMAT=FF10_ACTIVITY\n'+
'#COUNTRY US\n'+
'#YEAR 2012\n'+
'# COUNTRY_CD,REGION_CD,TRIBAL_CODE,CENSUS_TRACT_CD,SHAPE_ID,SCC,ACT_PARM_TYPE_CD,ACT_PARM_UOFMSR,ACTIVITY_TYPE,ANN_PARM_VALUE,CALC_YEAR,DATE_UPDATED,DATA_SET_ID,JAN_VALUE,FEB_VALUE,MAR_VALUE,APR_VALUE,MAY_VALUE,JUN_VALUE,JUL_VALUE,AUG_VALUE,SEP_VALUE,OCT_VALUE,NOV_VALUE,DEC_VALUE,COMMENT')
for line in mbinv_spd.readlines()[5:]:
    nargs = line.strip().split(",")
    try:
        nargs[5] = code_dict[str(int(nargs[5]))]
        nLine = ",".join(nargs)+"\n"
        mbinv_spd_out.write(nLine)
    except:
        print "SCC %s is not available"%str(int(nargs[5]))
mbinv_vmt_out.write('#FORMAT=FF10_ACTIVITY\n'+
'#COUNTRY  US\n'+
'#YEAR     2012\n'+
'# units of ANN_PARM_VALUE are in total miles per year\n'+
'# COUNTRY_CD,REGION_CD,TRIBAL_CODE,CENSUS_TRACT_CD,SHAPE_ID,SCC,ACT_PARM_TYPE_CD,ACT_PARM_UOFMSR,ACTIVITY_TYPE,ANN_PARM_VALUE,CALC_YEAR,DATE_UPDATED,DATA_SET_ID,JAN_VALUE,FEB_VALUE,MAR_VALUE,APR_VALUE,MAY_VALUE,JUN_VALUE,JUL_VALUE,AUG_VALUE,SEP_VALUE,OCT_VALUE,NOV_VALUE,DEC_VALUE,COMMENT\n')

for line in mbinv_vmt.readlines()[5:]:
    nargs = line.strip().split(",")
    try:
        nargs[5] = code_dict[str(int(nargs[5]))]
        nLine = ",".join(nargs)+"\n"
        mbinv_vmt_out.write(nLine)
    except:
        print "SCC %s is not available"%str(int(nargs[5]))
mbinv_spd.close() 
mbinv_vmt.close() 
input.close() 
mbinv_spd_out.close()
mbinv_vmt_out.close() 
gsref_in.close() 
gsref_out.close() 

