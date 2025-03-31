#!/usr/bin/env python    
# - coding:utf - 8 -*-
#2017.07.03-haoxiaoci
import re,sys
import string
#filter the unexpected instance UUID
with open('/var/log/nova/nova-compute.log') as f:
    UUIDlist=[]
    for line in f:
        parseInstanceUUID = re.search(r'\[instance:(.*?)\]', line)
        parseKeyword = re.search('During _sync_instance_power_state(.*?)\.',line)
        if parseInstanceUUID is None or parseKeyword is None:
            continue
        #print parseInstanceUUID
        #print parseKeyword
        uuid = parseInstanceUUID.group(1) 
        UUIDlist.append(uuid)
#Remove the duplicate UUID

for x in UUIDlist:
    while UUIDlist.count(x)>1:
        del UUIDlist[UUIDlist.index(x)]

json = "{\n" + "\t" + '"data":[' + "\n"
for j in UUIDlist:
    if j !=UUIDlist[-1]:
        json=json +  "\t\t" + "{" + "\n" + "\t\t\t" + '"{#INSTANCE_UUID}":"' + str(j) + "\"\n\t\t\t},\n"
    else:
        json=json +  "\t\t" + "{" + "\n" + "\t\t\t" + '"{#INSTANCE_UUID}":"' + str(j) + "\"\n\t\t}\n\t]\n}"
print json

