#!/usr/bin/env python
# -*- coding:utf-8 -*-
#by wuxiaoliu
from __future__ import division
import json
import sys
import commands

ceph_osd_tree_cmd = 'ceph osd tree -f json 2>/dev/null'
ceph_osd_df_cmd = 'ceph osd df -f json-pretty 2>/dev/null'

def write_value(data,osd_num):
    try:
        f = open("/dev/shm/zbxosd--"+osd_num, 'w')
        f.write(str(data))
        f.close()
    except:
        return 0


def read_value_json(osd_num):
    try:
        f = open("/dev/shm/zbxosd--"+osd_num, 'r')
        r = f.read()
        data = json.loads(r)
        return data
    except:
        return 0


def osd_number():
    p = sys.argv[1]
    pp = (p.split('-'))
    ppp = pp[1]
    return ppp


def ceph_osd_cmd(osd_number):
    cmd = 'sudo ceph daemon osd.'+osd_number+' perf dump 2>/dev/null'
    return_code, output = commands.getstatusoutput(cmd)
    if return_code == 0:
        return output


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
    print 'usage: %s ceph-X latency <op_latency|r_latency|w_latency|rw_latency>'% sys.argv[0]
    print '       %s        pg <numpg|numpg_primary|numpg_replica|numpg_stray|pgclean|pgwork|pgdirty>'% sys.argv[0]
    print '       %s        hit hitpercent'% sys.argv[0]
    print '       %s        filestore <journal_latency|apply_latency>'% sys.argv[0]
    print '       %s        status alive'% sys.argv[0]
    print '       %s        use <deviation|kb_all|kb_used|kb_avail|utilization>'% sys.argv[0]


def subtraction(new,old):
    try:
        cha = new - old
        if cha < 0 :
            return 0
        else:
            return cha
    except:
        return 0


def division(lasum,laavg):
    try:
        late = lasum/laavg
        if late < 0 :
            return 0
        else:
            return late
    except:
        return 0


def select_latency(p,newjson,oldjson):
    newosd = newjson.get('osd')
    oldosd = oldjson.get('osd')
    if p == 'op_latency':
        new_lasum = newosd.get('op_latency').get('sum') or 0
        old_lasum = oldosd.get('op_latency').get('sum') or 0
        sum_cha = subtraction(new_lasum,old_lasum)
        new_laavg = newosd.get('op_latency').get('avgcount') or 0
        old_laavg = oldosd.get('op_latency').get('avgcount') or 0
        avg_cha = subtraction(new_laavg,old_laavg)
        late = division(sum_cha,avg_cha)
        return late
    elif p == 'r_latency':
        new_lasum = newosd.get('op_r_latency').get('sum') or 0
        old_lasum = oldosd.get('op_r_latency').get('sum') or 0
        sum_cha = subtraction(new_lasum,old_lasum)
        new_laavg = newosd.get('op_r_latency').get('avgcount') or 0
        old_laavg = oldosd.get('op_r_latency').get('avgcount') or 0
        avg_cha = subtraction(new_laavg,old_laavg)
        late = division(sum_cha,avg_cha)
        return late
    elif p == 'w_latency':
        new_lasum = newosd.get('op_w_latency').get('sum') or 0
        old_lasum = oldosd.get('op_w_latency').get('sum') or 0
        sum_cha = subtraction(new_lasum,old_lasum)
        new_laavg = newosd.get('op_w_latency').get('avgcount') or 0
        old_laavg = oldosd.get('op_w_latency').get('avgcount') or 0
        avg_cha = subtraction(new_laavg,old_laavg)
        late = division(sum_cha,avg_cha)
        return late
    elif p == 'rw_latency':
        new_lasum = newosd.get('op_rw_latency').get('sum') or 0
        old_lasum = oldosd.get('op_rw_latency').get('sum') or 0
        sum_cha = subtraction(new_lasum,old_lasum)
        new_laavg = newosd.get('op_rw_latency').get('avgcount') or 0
        old_laavg = oldosd.get('op_rw_latency').get('avgcount') or 0
        avg_cha = subtraction(new_laavg,old_laavg)
        late = division(sum_cha,avg_cha)
        return late
    else:
        return 'parameter no found'
        xhelp()


# op = op_r + op_w + op_rw
# op_in_bytes = op_w_in_bytes + op_rw_in_bytes
# op_out_bytes = op_r_out_bytes + op_rw_out_bytes
# op_latency.avgcount = op_r_latency.avgcount + op_w_latency.avgcount + op_rw_latency.avgcount
# op_latency.sum = op_r_latency.sum + op_w_latency.sum + op_rw_latency.sum


def select_pg(p,data,osd_num):
    clean_cmd = 'ceph pg ls-by-osd '+osd_num+' -f json-pretty 2>/dev/null | grep active+clean | wc -l'
    work_cmd = 'ceph pg ls-by-osd '+osd_num+' -f json-pretty 2>/dev/null | grep active+ | wc -l'
    if p == 'numpg':
        return data.get('osd').get('numpg') or 0
    elif p == 'numpg_primary':
        return data.get('osd').get('numpg_primary') or 0
    elif p == 'numpg_replica':
        return data.get('osd').get('numpg_replica') or 0
    elif p == 'numpg_stray':
        return data.get('osd').get('numpg_stray') or 0
    elif p == 'pgclean':
        return_code, out = commands.getstatusoutput(clean_cmd)
        if return_code == 0:
            return out
    elif p == 'pgwork':
        return_code, out = commands.getstatusoutput(work_cmd)
        if return_code == 0:
            return out
    elif p == 'pgdirty':
        cleanout = commands.getstatusoutput(clean_cmd)
        workout = commands.getstatusoutput(work_cmd)
        dirtyout = subtraction(int(workout[0]),int(cleanout[0]))
        return dirtyout
    else:
        return 'pg parameter no found !'
        xhelp()


def select_hit(p,data):
    if p == 'hitpercent':
        hit = data.get('osd').get('object_ctx_cache_hit') or 0
        total = data.get('osd').get('object_ctx_cache_total') or 0
        hitper = division(hit,total)
        return 100*hitper
    else:
        return 'hit parameter no found'
        xhelp()


def select_filestore(p,data):
    store = data.get('filestore')
    if p == 'journal_latency':
       jsum = store.get('journal_latency').get('sum') or 0
       javg = store.get('journal_latency').get('avgcount') or 0
       jlate = division(jsum,javg)
       return jlate
    elif p == 'apply_latency':
       asum = store.get('apply_latency').get('sum') or 0
       aavg = store.get('apply_latency').get('avgcount') or 0
       alate = division(asum,aavg)
       return alate
    else:
        return 'filestore parameter no found !'
        xhelp()


def select_status(p,osd_num):
    cmd_data = ceph_data(ceph_osd_tree_cmd)
    name = 'osd.'+osd_num
    if p == 'alive':
        data = cmd_data['nodes']
        for v in data:
            if name == v['name']:
                t = v['status']
                if t == 'up':
                    return 1
                elif t == 'down':
                    return 0
                else:
                    return 'status is null !'
                return 0
    else:
        return 'status parameter no found !'
        xhelp()


def select_use(p,osd_num):
    cmd_data = ceph_data(ceph_osd_df_cmd)
    name = 'osd.'+osd_num
    data = cmd_data['nodes']
    for v in data:
        if name == v['name']:
            if p == 'deviation':
                return v['var']
            elif p == 'kb_all':
                return v['kb']
            elif p == 'kb_used':
                return v['kb_used']
            elif p == 'kb_avail':
                return v['kb_avail']
            elif p == 'utilization':
                return v['utilization']
            else:
                return 'use parameter no found !'
                xhelp()
    #bo sure no Null value
    return 0


if __name__ == '__main__':
    if len(sys.argv) == 4: # three parameter
        osd_nums = osd_number()
        cmd_data = ceph_osd_cmd(osd_nums)
        if cmd_data:
            newjson = json.loads(cmd_data)
            oldjson = read_value_json(osd_nums)
            p = sys.argv[2]
            if oldjson == 0:
                write_value(cmd_data,osd_nums)
                print 0
            else:
                if p == 'pg':
                    print select_pg(sys.argv[3],newjson,osd_nums)
                elif p == 'hit':
                    print select_hit(sys.argv[3],newjson)
                elif p == 'filestore':
                    print select_filestore(sys.argv[3],newjson)
                elif p == 'status':
                    print select_status(sys.argv[3],osd_nums)
                elif p == 'use':
                    print select_use(sys.argv[3],osd_nums)
                else:
                    print select_latency(sys.argv[3],newjson,oldjson)
                    write_value(cmd_data,osd_nums)
        else:
            print 0
            sys.exit()
    else:
        print "Error ! You input parameter nums Error !"
        xhelp()
