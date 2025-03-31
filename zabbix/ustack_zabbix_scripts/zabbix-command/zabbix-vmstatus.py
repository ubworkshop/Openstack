#!/usr/bin/env python
# wuxiaoliu
import sys
from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client

def vmshow(u):
    auth = v3.Password(auth_url='http://lb.0.nxin.ustack.in:35357/v3',
                       username='admin',
                       password='5d196c5193bea137463b61a6',
                       project_name='openstack',
                       user_domain_id='default',
                       project_domain_id='default')
    sess = session.Session(auth=auth)
    nova = client.Client("2.1", session=sess)
    reload(sys)
    sys.setdefaultencoding("utf8")
    r = nova.servers.get(u)
    print r.status + '_' + r.name

if __name__ == '__main__':
    if len(sys.argv) == 2: # one parameter
        i = sys.argv[1]
        vmshow(i)
    else:
        print 'usage: %s  UUID' % sys.argv[0]
