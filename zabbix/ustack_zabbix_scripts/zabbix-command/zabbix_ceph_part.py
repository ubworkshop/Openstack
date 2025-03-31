#!/usr/bin/env python
# -*- coding:utf-8 -*-
#by wuxiaoliu
import json
import sys
import commands

ceph_mon_cmd = 'ceph quorum_status --format json-pretty 2>/dev/null'
ceph_pg_cmd = 'ceph -s --format json-pretty 2>/dev/null'
ceph_df_cmd = 'ceph df detail --format json-pretty 2>/dev/null'
ceph_pool_cmd = 'ceph osd pool stats --format json-pretty 2>/dev/null'
ceph_mon_down_num = 'ceph -s --format json-pretty 2>/dev/null'


def ceph_data(cmd):
        return_code, output = commands.getstatusoutput(cmd)
        if return_code == 0:
            try:
                data = json.loads(output)
                return data
            except:
                print 0
                sys.exit()


def xhelp():
    print "usage: %s mon <leader|epoch|outside|down_num> "% sys.argv[0]
    print "       %s pg <num_pgs|active+clean|active+undersized+degraded|active+remapped|active+undersized+degraded+remapped> "% sys.argv[0]
    print "       %s pool <openstack-00|sata-00|gnocchi> <pool_id|write|read|ops> "% sys.argv[0]
    print "       %s df <openstack-00|sata-00|gnocchi> <bytes_used|max_avail> "% sys.argv[0]
    print "       %s osd </var/lib/ceph/osd/ceph-X> <op|op_r|op_w|op_rw|op_in_bytes|op_w_in_bytes|op_rw_in_bytes|op_out_bytes|op_r_out_bytes|op_rw_out_bytes|op_laavg|op_r_laavg|op_w_laavg|op_rw_laavg|op_lasum|op_r_lasum|op_w_lasum|op_rw_lasum> "% sys.argv[0]


def select_mon_status(p,ceph_data):
    if p == 'leader':
        return ceph_data.get("quorum_leader_name") or 0
    elif p == 'epoch':
        return ceph_data.get("election_epoch") or 0
    elif p == 'outside':
        return ceph_data.get("outside_quorum") or 0
    else:
        return 'parameter no found'
        xhelp()


def mon_down_num(ceph_data):
    data = ceph_data['health']['summary']
    for i in data:
     s = 'mons down'
     j = i['summary']
     if j.find(s) > 0:
         f = i['summary']
         h = f.split(' ')[0]
         return h
         return 0
    return 0


def select_pg_status(p,ceph_data):
    xmap = {'active+clean','active+undersized+degraded','active+remapped','active+undersized+degraded+remapped'}
    if p == 'num_pgs':
        return ceph_data['pgmap']['num_pgs']
    elif p in xmap:
        for v in ceph_data['pgmap']['pgs_by_state']:
            if p == v['state_name']:
                return v['count']
            else:
                return 0
    else:
        return 0


def select_df_status(p,k,ceph_data):
    data = ceph_data['pools']
    for i in data:
        if p in i['name']:
            if k == 'bytes_used':
                return i['stats']['bytes_used']
            elif k == 'max_avail':
                return i['stats']['max_avail']
            else:
                return 0
            return 0
    else:
        return 'pool no found !'


def select_pool_status(p,k,ceph_data):
    for v in ceph_data:
        if p in v['pool_name']: # Determine existence value can use [] , no sure value use get or 0
            if k == 'pool_id':
                return v['pool_id']
            elif k == 'write':
                return v['client_io_rate'].get('write_bytes_sec') or 0
            elif k == 'read':
                return v['client_io_rate'].get('read_bytes_sec') or 0
            elif k == 'ops':
                return v['client_io_rate'].get('op_per_sec') or 0
            else:
                return 'parameter no found'
                xhelp()
            return 0
    else:
       return 'pool no found'


def select_osd_status(p,ceph_data):
   osd = ceph_data.get('osd')
   if p == 'op':
       return osd.get('op') or 0 # Osd section all value is accumulated value,need calculate
   elif p == 'op_r':
       return osd.get('op_r') or 0
   elif p == 'op_w':
       return osd.get('op_w') or 0
   elif p == 'op_rw':
       return osd.get('op_rw') or 0
   elif p == 'op_in_bytes':
       return osd.get('op_in_bytes') or 0
   elif p == 'op_w_in_bytes':
       return osd.get('op_w_in_bytes') or 0
   elif p == 'op_rw_in_bytes':
       return osd.get('op_rw_in_bytes') or 0
   elif p == 'op_out_bytes':
       return osd.get('op_out_bytes') or 0
   elif p == 'op_r_out_bytes':
       return osd.get('op_r_out_bytes') or 0
   elif p == 'op_rw_out_bytes':
       return osd.get('op_rw_out_bytes') or 0
   elif p == 'op_laavg':
       return osd.get('op_latency').get('avgcount') or 0
   elif p == 'op_r_laavg':
       return osd.get('op_r_latency').get('avgcount') or 0
   elif p == 'op_w_laavg':
       return osd.get('op_w_latency').get('avgcount') or 0
   elif p == 'op_rw_laavg':
       return osd.get('op_rw_latency').get('avgcount') or 0
   elif p == 'op_lasum':
       return osd.get('op_latency').get('sum') or 0 # This output is float num
   elif p == 'op_r_lasum':
       return osd.get('op_r_latency').get('sum') or 0
   elif p == 'op_w_lasum':
       return osd.get('op_w_latency').get('sum') or 0
   elif p == 'op_rw_lasum':
       return osd.get('op_rw_latency').get('sum') or 0
   else:
       return 'parameter no found'
       xhelp()
# op = op_r + op_w + op_rw
# op_in_bytes = op_w_in_bytes + op_rw_in_bytes
# op_out_bytes = op_r_out_bytes + op_rw_out_bytes
# op_latency.avgcount = op_r_latency.avgcount + op_w_latency.avgcount + op_rw_latency.avgcount
# op_latency.sum = op_r_latency.sum + op_w_latency.sum + op_rw_latency.sum


if __name__ == '__main__':
    if len(sys.argv) == 3: # two parameter
        part = sys.argv[1]
        parts = sys.argv[2]
        if part == 'mon':
            if parts == 'down_num':
                ceph_data = ceph_data(ceph_mon_down_num)
                if ceph_data:
                    print mon_down_num(ceph_data)
                else:
                    print 0
            else:
                ceph_data = ceph_data(ceph_mon_cmd)
                if ceph_data:
                    print select_mon_status(sys.argv[2],ceph_data)
                else:
                    print 0
        elif part == 'pg':
            ceph_data = ceph_data(ceph_pg_cmd)
            if ceph_data:
                print select_pg_status(sys.argv[2],ceph_data)
            else:
                print 0
        elif part == 'pool':
            print 'Error ! You need input three parameter !'
            xhelp()
        else:
            print 'Error ! You first parameter input Error !'
            xhelp()
    elif len(sys.argv) == 4: # three parameter
        part = sys.argv[1]
        if part == 'pool':
            ceph_data = ceph_data(ceph_pool_cmd)
            if ceph_data:
                print select_pool_status(sys.argv[2],sys.argv[3],ceph_data)
            else:
                print 0 # 0 mean excuting shell error
        elif part == 'df':
            ceph_data = ceph_data(ceph_df_cmd)
            if ceph_data:
                print select_df_status(sys.argv[2],sys.argv[3],ceph_data)
            else:
                print 0
        elif part == 'osd':
            p = sys.argv[2]
            pp = (p.split('-'))
            ppp = pp[1]
            ceph_osd_cmd = 'ceph daemon osd.'+ppp+' perf dump'
            ceph_data = ceph_data(ceph_osd_cmd)
            if ceph_data:
                print select_osd_status(sys.argv[3],ceph_data)
            else:
                print 0
        else:
            print 'Error ! You first parameter input Error !'
            xhelp()
    else:
        print "Error ! You input parameter nums Error !"
        xhelp()
