
import os
datadir = os.getenv('DATA')
#sharedir = "/usr/local/share"


cfndfile = open("%s/cfnd.csv" % (datadir), "r")
lines = cfndfile.readlines()
cfndfile.close()

Cfnd = []
for line in lines[1:]:
    [cid,fid,name,dist] = line.strip().split(',')
    if fid == '':
        fid = -1
    if dist == '':
        dist = -1
    Cfnd.append([int(cid),int(fid),name.strip(),int(dist)])
#return Cfnd
