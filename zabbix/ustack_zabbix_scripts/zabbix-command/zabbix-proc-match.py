#!/usr/bin/env python
# wuxiaoliu
import sys
import json
import commands

#template_role_api
#openstack-aodh-notifier,openstack-aodh-listener,openstack-aodh-evaluator,openstack-ceilometer-notification,openstack-ceilometer-collector,openstack-ceilometer-api,openstack-cinder-api,openstack-cinder-scheduler,openstack-glance-api,openstack-glance-regist,httpd,ustack-kiki-api,ustack-kiki-mq-consumer,kunkka,neutron-vpn-agent,neutron-openvswitch-agent,neutron-metadata-agent,neutron-dhcp-agent,openstack-nova-api,openstack-nova-conductor

#template_role_compute
#openstack-ceilometer-compute,neutron-vts-agent,libvirtd,openstack-nova-compute,openvswitch-nonetwork,neutron-openvswitch-agent

#template_role_ceph_rgw
#ceph-radosgw

#template_role_gnocchi
#gnocchi

#template_role_l4
#haproxy

#template_role_memcached
#memcached

#template_role_rabbitmq
#rabbitmq-server

#template_role_zabbix-server
#zabbix-server

#template_system_ssh
#sshd

#template_system_rsyslog
#rsyslog

#template_system_crontab
#crond

system_cmd = 'cd /usr/lib/systemd/system/ && ls *.service | grep -v @'
need_proc = 'openstack-aodh-notifier.service,openstack-aodh-listener.service,openstack-aodh-evaluator.service,openstack-ceilometer-notification.service,openstack-ceilometer-collector.service,openstack-ceilometer-api.service,openstack-ceilometer-compute.service,ceph-radosgw.service,openstack-cinder-api.service,openstack-cinder-scheduler.service,openstack-glance-api.service,openstack-glance-regist.service,gnocchi.service,haproxy.service,httpd.service,ustack-kiki-api.service,ustack-kiki-mq-consumer.service,kunkka.service,memcached.service,neutron-vpn-agent.service,neutron-openvswitch-agent.service,neutron-metadata-agent.service,neutron-dhcp-agent.service,openstack-nova-api.service,neutron-vts-agent.service,libvirtd.service,openstack-nova-compute.service,openvswitch-nonetwork.service,neutron-openvswitch-agent.service,openstack-nova-conductor.service,openstack-nova-novncproxy.service,openstack-nova-scheduler.service,rabbitmq-server.service,zabbix-server.service,sshd.service,rsyslog.service,crond.service'

def cmd_data(cmd):
        return_code, output = commands.getstatusoutput(cmd)
        a = output.split('\n')
        b = need_proc.split(',')
        tmp = [val for val in a if val in b]
        result = {"data": []}
        for p in tmp:
            result["data"].append({"{#PROCNAME}": p[:-8]})
        return json.dumps(result)


if __name__ == '__main__':
    try:
        print cmd_data(system_cmd)
    except:
        print 0
