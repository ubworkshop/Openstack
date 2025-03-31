#!/usr/bin/env python
#
#Written by Xuchangbao

import sys
import json
import subprocess

def cmd(args):
    cmd_result = subprocess.Popen(
        args,
        shell = True,
        stdout = subprocess.PIPE).communicate()[0]
    return cmd_result

def get_failure_domain_name(pool) :
    args = 'ceph osd pool get %s crush_ruleset 2>/dev/null' % pool
    crush_ruleset = cmd(args).split()[1]

    args = 'ceph osd crush dump 2>/dev/null'
    osd_crush_dump = cmd(args)

    for i in json.loads(osd_crush_dump)['rules']:
        if int(i['ruleset']) == int(crush_ruleset):
            return i['steps'][0]['item_name']

def get_pool_size(pool):
    args = 'ceph osd pool get %s size -f json 2>/dev/null' % pool
    size = json.loads(cmd(args))["size"]
    return size

def get_osds_df(failure_domain_name):
    args = 'ceph osd df tree -f json 2>/dev/null'
    osd_df = cmd(args)
    osd_df_dict = json.loads(osd_df)
        
    
    failure_domain_df = {}
    for i in osd_df_dict['nodes']:
        if i['name'] == failure_domain_name and i['type'] == 'failure-domain':
            failure_domain_df['utilization'] = i['utilization']
            failure_domain_df['kb_avail'] = i['kb_avail']
            failure_domain_df['kb_used'] = i['kb_used']
            failure_domain_df['kb'] = i['kb']
    return failure_domain_df

def get_ceph_df(pool):
    #Old version 0.80.91
    args = 'ceph df -f json 2>/dev/null'
    ceph_df = cmd(args)
    ceph_df_dict = json.loads(ceph_df)

    pool_df={}
    for i in ceph_df_dict['pools']:
        if i['name'] == pool:
            stats=i['stats']
            pool_df['kb_used'] = stats['kb_used']
            pool_df['kb_avail'] = stats['max_avail'] / 1024
            pool_df['kb'] =pool_df['kb_used'] + pool_df['kb_avail']
            pool_df['utilization'] = pool_df['kb_used'] * 100.0 / pool_df['kb']
    return pool_df


def get_capacity(pool):
    if cmd('rpm -q ceph').count('0.80.91') < 1 :
        domain_name=get_failure_domain_name(pool)
        capacity=get_osds_df(domain_name)
    else:
        capacity=get_ceph_df(pool)
    return capacity

def main():
    xhelp="usage: %s <sata|ssd> <utilization|kb_avail|kb_used|kb_total|kb_avail_real|kb_total_real>" % sys.argv[0]

    if len(sys.argv) != 3:
        print xhelp
        sys.exit(-1)

    xmap={
        'ssd': 'openstack-00',
        'sata': 'sata-00',
        'type': ['utilization', 'kb_avail', 'kb_used', 'kb_total', 'kb_total_real', 'kb_avail_real']
        }


    if sys.argv[2] in xmap['type'] and sys.argv[1] in xmap.keys():
	pool=xmap[sys.argv[1]]
        capacity=get_capacity(pool)

        if sys.argv[2] == 'utilization':
            print  "%.2f" % capacity[sys.argv[2]]
        elif sys.argv[2] == 'kb_total':
            print capacity['kb']
        elif sys.argv[2] == "kb_total_real":
            size=get_pool_size(pool)
            print capacity['kb'] / size
        elif sys.argv[2] == "kb_avail_real":
            size=get_pool_size(pool)
            print capacity['kb_avail'] / size
        else:
            print capacity[sys.argv[2]]
    else:
        print xhelp

if __name__ == '__main__':
    main()
