#!/bin/bash
source /root/openrc
tap=`echo $1 | cut -d - -f 1 | sed "s/tap//g"`
shared_net=$(neutron net-list --shared | grep shared | awk '{print $2}')
tap_net=$(neutron port-show nic-$tap | grep network_id | awk '{print $4}')
if [[ $shared_net == $tap_net ]]
then
    echo 1
else
    echo 0 
fi
