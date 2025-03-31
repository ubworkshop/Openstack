#!/usr/bin/env python
# wuxiaoliu
import sys
import json

def get_proc_name():
    s = sys.argv[1].split(',')
    result = {"data": []}
    for p in s:
        result["data"].append({"{#PROCNAME}": p})
    return json.dumps(result)


if __name__ == '__main__':
    try:
        print get_proc_name()
    except:
        print 0
