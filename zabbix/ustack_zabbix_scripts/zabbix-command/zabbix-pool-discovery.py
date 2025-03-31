#!/usr/bin/env python
import sys
import json
import commands


def get_pool_name():
    return_code,cmd_result = commands.getstatusoutput('timeout 10 ceph osd pool ls -f json 2>/dev/null')
    if return_code != 0:
        return
    result = {"data": []}
    pools = json.loads(cmd_result)
    for pool in pools:
        if not pool.startswith("."):
            result["data"].append({"{#POOL_NAME}": pool})
    return json.dumps(result)


if __name__ == '__main__':
    print get_pool_name()
