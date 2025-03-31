#!/usr/bin/env python
#
#Written by Xuchangbao

import sys
import json
import subprocess

args = 'ceph osd pool get openstack-00 crush_ruleset'
crush_ruleset = subprocess.Popen(
    args,
    shell = True,
    stdout = subprocess.PIPE).communicate()[0].split()[1]

args = 'ceph osd crush dump'
osd_crush_dump = subprocess.Popen(args,
    shell = True,
    stdout = subprocess.PIPE).communicate()[0]

for i in json.loads(osd_crush_dump)['rules']:
    if int(i['ruleset']) == int(crush_ruleset):
        ssd_pool=i['steps'][0]['item_name']

args = 'ceph osd df tree -f json'
pool_df = subprocess.Popen(args,
        shell = True,
        stdout = subprocess.PIPE).communicate()[0]

pool_df_dict = json.loads(pool_df)

pools_df = {}
for i in pool_df_dict['nodes']:
    if i['name'] == 'sata01' and i['type'] == 'failure-domain':
        pools_df['sata_utilization'] = i['utilization']
        pools_df['sata_kb_avail'] = i['kb_avail']
        pools_df['sata_kb_used'] = i['kb_used']
        pools_df['sata_kb'] = i['kb']
    elif i['name'] == ssd_pool and i['type'] == 'failure-domain':
        pools_df['ssd_utilization'] = i['utilization']
        pools_df['ssd_kb_avail'] = i['kb_avail']
        pools_df['ssd_kb_used'] = i['kb_used']
        pools_df['ssd_kb'] = i['kb']

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print """usage: %s { sata_utilization| sata_kb_avail | sata_kb_used | sata_kb
                         ssd_utilization | ssd_kb_avail  | ssd_kb_used  | ssd_kb  }
        """ % sys.argv[0]
        sys.exit(-1)

    if sys.argv[1] == 'sata_utilization' or sys.argv[1] == 'ssd_utilization':
        print  "%.2f" % pools_df[sys.argv[1]]
    else:
        print  pools_df[sys.argv[1]]
