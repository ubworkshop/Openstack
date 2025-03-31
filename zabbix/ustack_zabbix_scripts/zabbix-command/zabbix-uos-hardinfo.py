#! /usr/bin/env python

"""Usage:
    uos_hardinfo [<vendor>] [<chassis>]

Options:
    -h --help  		Show the screen.
    --version	        Show version.
    vendor	        Specify vendor. Example: dell, hp, huawei, inspur, etc.
    chassis	        Example: cpu, mem, fans, power, harddisk, temp.
"""

import argparse
import ConfigParser
import os
import sys
import re
import itertools
from subprocess import Popen, PIPE
#from docopt import docopt

try:
    import json
except:
    import simplejson as json

class Dell(object):
    def __init__(self):
	pass

    def cpu(self):
	cpu_monitor = {}
	command = "/opt/dell/srvadmin/bin/omreport chassis processors | grep -e '^Index' -e '^Status'"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	cpu_mon_list = filter(None, re.split("''|\ * |: |\n", res))
	cpu_monitor['Details'] = ''
	for i in range(0, len(cpu_mon_list), 2):
	    if cpu_mon_list[i] == 'Index':
		cpu_index = 'Index ' + cpu_mon_list[i+1]
		cpu_status = cpu_mon_list[i+3]
	        cpu_monitor[cpu_index] = cpu_status
	for k,v in cpu_monitor.items():
	    if v != 'Ok' and k != 'Details':
		cpu_monitor['Status'] = 'Error'
		cpu_monitor['Details'] = cpu_monitor['Details'] + "Error CPU:" + k + ' '
	if 'Status' not in cpu_monitor.keys():
	    cpu_monitor['Status'] = 'Ok'
	    cpu_monitor['Details'] = 'Ok'
	return cpu_monitor

    def mem(self):
	mem_monitor = {}
	command1 = "/opt/dell/srvadmin/bin/omreport chassis memory | grep '^Connector Name' | awk -F':' '{print $2}' | xargs"
	command2 = "/opt/dell/srvadmin/bin/omreport chassis memory | grep '^Status' | awk -F':' '{print $2}' | xargs"
	process1 = Popen(command1, shell=True, stdout=PIPE, stderr=PIPE)
	process2 = Popen(command2, shell=True, stdout=PIPE, stderr=PIPE)
	(res1, stderr1) = process1.communicate()
	(res2, stderr2) = process2.communicate()
	mem_conn_list = res1.split()
	mem_stat_list = res2.split()
	mem_monitor = dict(itertools.izip(mem_conn_list, mem_stat_list))
	mem_monitor['Details'] = ''
	for k,v in mem_monitor.items():
	    if v != 'Ok' and v != 'Unknown' and k != 'Details':
		mem_monitor['Status'] = 'Error'
		mem_monitor['Details'] = mem_monitor['Details'] + "Error Memory:" + k + ' '
	if 'Status' not in mem_monitor.keys():
	    mem_monitor['Status'] = 'Ok'
	    mem_monitor['Details'] = 'Ok'
	return mem_monitor

    def temp(self):
	temp_monitor = {}
	command = "/opt/dell/srvadmin/bin/omreport chassis temps | grep -e '^Index' -e '^Status'"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	temp_mon_list = filter(None, re.split("''|\ * |: |\n", res))
	temp_monitor['Details'] = ''
	for i in range(0, len(temp_mon_list), 2):
	    if temp_mon_list[i] == 'Index':
		temp_index = 'Index ' + temp_mon_list[i+1]
		temp_status = temp_mon_list[i+3]
	        temp_monitor[temp_index] = temp_status
	for k,v in temp_monitor.items():
	    if v != 'Ok' and k != 'Details':
		temp_monitor['Status'] = 'Error'
		temp_monitor['Details'] = temp_monitor['Details'] + "Error TEMP:" + k + ' '
	if 'Status' not in temp_monitor.keys():
	    temp_monitor['Status'] = 'Ok'
	    temp_monitor['Details'] = 'Ok'
	return temp_monitor

    def harddisk(self):
	disk_monitor = {}
	command1 = "/opt/dell/srvadmin/bin/omreport storage pdisk controller=0 | grep '^ID' | cut -d':'  -f2,3,4 | xargs"
	command2 = "/opt/dell/srvadmin/bin/omreport storage pdisk controller=0 | grep '^Status' | awk -F':' '{print $2}' | xargs"
	#command3 = "/opt/dell/srvadmin/bin/omreport storage pdisk controller=0 | grep '^State' | awk -F':' '{print $2}' | xargs"
	process1 = Popen(command1, shell=True, stdout=PIPE, stderr=PIPE)
	process2 = Popen(command2, shell=True, stdout=PIPE, stderr=PIPE)
	(res1, stderr1) = process1.communicate()
	(res2, stderr2) = process2.communicate()
	disk_id_list = res1.split()
	disk_stat_list = res2.split()
	disk_monitor = dict(itertools.izip(disk_id_list, disk_stat_list))
	disk_monitor['Details'] = ''
	for k,v in disk_monitor.items():
	    if v != 'Ok' and v != 'Non-Critical' and k != 'Details':
		disk_monitor['Status'] = 'Error'
		disk_monitor['Details'] = disk_monitor['Details'] + "Error Disk:" + k + ' '

	common = DiskCommon()
	megacli = common.megacli()
	lsscsi = common.lsscsi()
	if megacli['Status'] != 'Ok':
	    disk_monitor['Status'] = megacli['Status']
	    disk_monitor['Details'] = disk_monitor['Details'] + megacli['Status']
	if lsscsi['Status'] != 'Ok':
	    disk_monitor['Status'] = lsscsi['Status']
	    disk_monitor['Details'] = disk_monitor['Details'] + lsscsi['Status']

	if 'Status' not in disk_monitor.keys():
	    disk_monitor['Status'] = 'Ok'
	    disk_monitor['Details'] = 'Ok'
	return disk_monitor

    def fans(self):
	fan_monitor = {}
	command = "/opt/dell/srvadmin/bin/omreport chassis fans | grep -e '^Index' -e '^Status'"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	fan_mon_list = filter(None, re.split("''|\ * |: |\n", res))
	fan_monitor['Details'] = ''
	for i in range(0, len(fan_mon_list), 2):
	    if fan_mon_list[i] == 'Index':
		fan_index = 'Index ' + fan_mon_list[i+1]
		fan_status = fan_mon_list[i+3]
	        fan_monitor[fan_index] = fan_status
	for k,v in fan_monitor.items():
	    if v != 'Ok' and k != 'Details':
		fan_monitor['Status'] = 'Error'
		fan_monitor['Details'] = fan_monitor['Details'] + "Error FAN:" + k + ' '
	if 'Status' not in fan_monitor.keys():
	    fan_monitor['Status'] = 'Ok'
	    fan_monitor['Details'] = 'Ok'
	return fan_monitor

    def power(self):
	power_monitor = {}
	command = "/opt/dell/srvadmin/bin/omreport chassis pwrsupplies | grep -e '^Index' -e '^Status'"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	power_mon_list = filter(None, re.split("''|\ * |: |\n", res))
	power_monitor['Details'] = ''
	for i in range(0, len(power_mon_list), 2):
	    if power_mon_list[i] == 'Index':
		power_index = 'Index ' + power_mon_list[i+1]
		power_status = power_mon_list[i+3]
	        power_monitor[power_index] = power_status
	for k,v in power_monitor.items():
	    if v != 'Ok' and k != 'Details':
		power_monitor['Status'] = 'Error'
		power_monitor['Details'] = power_monitor['Details'] + "Error PS:" + k + ' '
	if 'Status' not in power_monitor.keys():
	    power_monitor['Status'] = 'Ok'
	    power_monitor['Details'] = 'Ok'
	return power_monitor

class HP(object):
    def __init__(self):
	pass

    def cpu(self):
	cpu_monitor = {}
	command = "hpasmcli -s 'show server' | grep -e 'Processor' -e 'Status' | grep -vi 'total' | cut -d ':' -f2 | xargs"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	cpu_mon_list = res.split()
	cpu_monitor['Details'] = ''
	for i in range(0, len(cpu_mon_list), 2):
	    cpu_index = cpu_mon_list[i]
	    cpu_status = cpu_mon_list[i+1]
	    cpu_monitor[cpu_index] = cpu_status
	for k,v in cpu_monitor.items():
	    if v != 'Ok' and k != 'Details':
		cpu_monitor['Status'] = 'Error'
		cpu_monitor['Details'] = cpu_monitor['Details'] + "Error CPU:" + k + ' '
	if 'Status' not in cpu_monitor.keys():
	    cpu_monitor['Status'] = 'Ok'
	    cpu_monitor['Details'] = 'Ok'
	return cpu_monitor

    def mem(self):
	mem_monitor = {}
	command = "hpasmcli -s 'show dimm' | grep -e 'Processor' -e 'Module' -e 'Status' | cut -d':' -f2 | xargs"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr1) = process.communicate()
	mem_conn_list = res.split()
	mem_monitor['Details'] = ''
	for i in range(0, len(mem_conn_list), 3):
	    mem_index = mem_conn_list[i] + '_' + mem_conn_list[i+1]
	    mem_status = mem_conn_list[i+2]
	    mem_monitor[mem_index] = mem_status
	for k,v in mem_monitor.items():
	    if v != 'Ok' and k != 'Details':
		mem_monitor['Status'] = 'Error'
		mem_monitor['Details'] = mem_monitor['Details'] + "Error Memory:" + k + ' '
	if 'Status' not in mem_monitor.keys():
	    mem_monitor['Status'] = 'Ok'
	    mem_monitor['Details'] = 'Ok'
	return mem_monitor

    def temp(self):
	pass

    def harddisk(self):
	disk_monitor = {}
	command = "hpssacli ctrl slot=3 pd all show detail | grep -e 'physicaldrive' -e 'Status' | grep -v 'Authentication' | awk '{print $2}' | xargs"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	disk_mon_list = res.split()
	disk_monitor['Details'] = ''
	for i in range(0, len(disk_mon_list), 2):
	    disk_index = disk_mon_list[i]
	    disk_status = disk_mon_list[i+1]
	    disk_monitor[disk_index] = disk_status
	for k,v in disk_monitor.items():
	    if v != 'OK' and v != 'Non-Critical' and k != 'Details':
		disk_monitor['Status'] = 'Error'
		disk_monitor['Details'] = disk_monitor['Details'] + "Error Disk:" + k + ' '

	common = DiskCommon()
	lsscsi = common.lsscsi()
	if lsscsi['Status'] != 'Ok':
	    disk_monitor['Status'] = lsscsi['Status']
	    disk_monitor['Details'] = disk_monitor['Details'] + lsscsi['Status']

	if 'Status' not in disk_monitor.keys():
	    disk_monitor['Status'] = 'Ok'
	    disk_monitor['Details'] = 'Ok'
	return disk_monitor

    def fans(self):
	fan_monitor = {}
	command = "hpasmcli -s 'show fans' | grep SYSTEM | awk '{print $1,$4}' | xargs"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	fan_mon_list = res.split()
	fan_monitor['Details'] = ''
	for i in range(0, len(fan_mon_list), 2):
	    fan_index = fan_mon_list[i]
	    fan_status = fan_mon_list[i+1]
	    fan_monitor[fan_index] = fan_status
	for k,v in fan_monitor.items():
	    if v != 'NORMAL' and k != 'Details':
		fan_monitor['Status'] = 'Error'
		fan_monitor['Details'] = fan_monitor['Details'] + "Error FAN:" + k + ' '
	if 'Status' not in fan_monitor.keys():
	    fan_monitor['Status'] = 'Ok'
	    fan_monitor['Details'] = 'Ok'
	return fan_monitor
    def power(self):
	power_monitor = {}
	command = "hpasmcli -s 'show powersupply'|grep -e 'Power supply' -e 'Condition'"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	power_mon_list = filter(None, re.split("\t|: |\n| #", res))
	power_monitor['Details'] = ''
	for i in range(0, len(power_mon_list), 2):
	    if power_mon_list[i] == 'Power supply':
		power_index = 'Index ' + power_mon_list[i+1]
		power_status = power_mon_list[i+3]
	        power_monitor[power_index] = power_status
	for k,v in power_monitor.items():
	    if v != 'Ok' and k != 'Details':
		power_monitor['Status'] = 'Error'
		power_monitor['Details'] = power_monitor['Details'] + "Error PS:" + k + ' '
	if 'Status' not in power_monitor.keys():
	    power_monitor['Status'] = 'Ok'
	    power_monitor['Details'] = 'Ok'
	return power_monitor

class Inspur(object):
    def __init__(self):
	pass

    def cpu(self):
        cpu_monitor = {}
        command = "ipmitool sdr|grep 'CPU[0-9]_Status' | awk -F '|' '{print $3}'|xargs "
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        cpu_monitor['Details'] = ''
        cpu_status = res.split()[0]
        cpu_monitor['CPU Status'] = cpu_status
        for k,v in cpu_monitor.items():
            if v != 'ok' and k != 'Details':
                cpu_monitor['Status'] = 'Error'
                cpu_monitor['Details'] = cpu_monitor['Details'] + "Error cpu:" + k + ' '

        if 'Status' not in cpu_monitor.keys():
            cpu_monitor['Status'] = 'Ok'
            cpu_monitor['Details'] = 'Ok'
        return cpu_monitor

    def mem(self):
        mem_monitor = {}
        command = "ipmitool sdr|grep 'MEM' | awk -F '|' '{print $3}' |xargs"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        mem_monitor['Details'] = ''
        mem_status = res.split()[0]
        mem_monitor['Memory Status'] = mem_status
        for k,v in mem_monitor.items():
            if v != 'ok' and k != 'Details':
                mem_monitor['Status'] = 'Error'
                mem_monitor['Details'] = mem_monitor['Details'] + "Error memory:" + k + ' '

        if 'Status' not in mem_monitor.keys():
            mem_monitor['Status'] = 'Ok'
            mem_monitor['Details'] = 'Ok'
        return mem_monitor

    def temp(self):
	pass

    def harddisk(self):
        disk_monitor = {}

        common = DiskCommon()
        megacli = common.megacli()
        lsscsi = common.lsscsi()
        if megacli['Status'] != 'Ok':
            disk_monitor['Status'] = megacli['Status']
            disk_monitor['Details'] = disk_monitor['Details'] + megacli['Status']
        if lsscsi['Status'] != 'Ok':
            disk_monitor['Status'] = lsscsi['Status']
            disk_monitor['Details'] = disk_monitor['Details'] + lsscsi['Status']

        if 'Status' not in disk_monitor.keys():
            disk_monitor['Status'] = 'Ok'
            disk_monitor['Details'] = 'Ok'
        return disk_monitor

    def fans(self):
        fan_monitor = {}
        command = "ipmitool sdr | grep 'FAN_SYS' | awk -F'|' '{print $1, $3}' | xargs"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        fan_mon_list = res.split()
        fan_monitor['Details'] = ''
        for i in range(0, len(fan_mon_list), 2):
            fan_index = fan_mon_list[i]
            fan_status = fan_mon_list[i+1]
            fan_monitor[fan_index] = fan_status
        for k,v in fan_monitor.items():
            if v != 'ok' and k != 'Details':
                fan_monitor['Status'] = 'Error'
                fan_monitor['Details'] = fan_monitor['Details'] + "Error FAN:" + k + ' '
        if 'Status' not in fan_monitor.keys():
            fan_monitor['Status'] = 'Ok'
            fan_monitor['Details'] = 'Ok'
        return fan_monitor

    def power(self):
        power_monitor = {}
        command = "ipmitool sdr | grep '^Power' | awk -F '|' '{print $1, $3}' | xargs"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
	power_mon_list = res.split()
        power_monitor['Details'] = ''
        for i in range(0, len(power_mon_list), 2):
	    if re.match("Power[0-9]_Status", power_mon_list[i]) != None:
                power_index = power_mon_list[i]
                power_status = power_mon_list[i+1]
                power_monitor[power_index] = power_status
        for k,v in power_monitor.items():
            if v != 'ok' and v != 'nc' and k != 'Details':
                power_monitor['Status'] = 'Error'
                power_monitor['Details'] = power_monitor['Details'] + "Error PS:" + k + ' '
        if 'Status' not in power_monitor.keys():
            power_monitor['Status'] = 'Ok'
            power_monitor['Details'] = 'Ok'
        return power_monitor

class Huawei(object):
    def __init__(self):
	pass

    def cpu(self):
        cpu_monitor = {}
        command = "ipmitool sdr | grep CPU | grep 'Status' |  awk -F'|' '{print $1, $3}' | xargs"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        cpu_monitor['Details'] = ''
        cpu_mon_list = res.split()
        for i in range(0, len(cpu_mon_list), 3):
            if re.match("CPU[0-9]", cpu_mon_list[i]):
                cpu_index = cpu_mon_list[i] + cpu_mon_list[i+1]
                cpu_status = cpu_mon_list[i+2]
                cpu_monitor[cpu_index] = cpu_status
        for k,v in cpu_monitor.items():
            if v != 'ok' and k != 'Details':
                cpu_monitor['Status'] = 'Error'
                cpu_monitor['Details'] = cpu_monitor['Details'] + "Error cpu:" + k + ' '

        if 'Status' not in cpu_monitor.keys():
            cpu_monitor['Status'] = 'Ok'
            cpu_monitor['Details'] = 'Ok'
        return cpu_monitor

    def mem(self):
	mem_monitor = {}
        command = "ipmitool sdr|grep 'Memory' | awk -F '|' '{print $3}' | xargs"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        mem_monitor['Details'] = ''
        mem_status = res.split()[0]
        mem_monitor['Memory Status'] = mem_status
        for k,v in mem_monitor.items():
            if v != 'ok' and k != 'Details':
                mem_monitor['Status'] = 'Error'
                mem_monitor['Details'] = mem_monitor['Details'] + "Error memory:" + k + ' '

        if 'Status' not in mem_monitor.keys():
            mem_monitor['Status'] = 'Ok'
            mem_monitor['Details'] = 'Ok'
        return mem_monitor

    def temp(self):
	pass

    def harddisk(self):
        disk_monitor = {}

        common = DiskCommon()
        megacli = common.megacli()
        lsscsi = common.lsscsi()
        if megacli['Status'] != 'Ok':
            disk_monitor['Status'] = megacli['Status']
            disk_monitor['Details'] = disk_monitor['Details'] + megacli['Status']
        if lsscsi['Status'] != 'Ok':
            disk_monitor['Status'] = lsscsi['Status']
            disk_monitor['Details'] = disk_monitor['Details'] + lsscsi['Status']

        if 'Status' not in disk_monitor.keys():
            disk_monitor['Status'] = 'Ok'
            disk_monitor['Details'] = 'Ok'
        return disk_monitor

    def fans(self):
        fan_monitor = {}
        command = "ipmitool sdr | grep FAN | grep 'Status' | awk -F '|' '{print $1,$3}' | xargs"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        fan_mon_list = res.split()
        fan_monitor['Details'] = ''
        for i in range(0, len(fan_mon_list), 4):
            fan_index = fan_mon_list[i] + ' ' + fan_mon_list[i+1] + ' ' + fan_mon_list[i+2]
            fan_status = fan_mon_list[i+3]
            fan_monitor[fan_index] = fan_status
        for k,v in fan_monitor.items():
            if v != 'ok' and k != 'Details':
                fan_monitor['Status'] = 'Error'
                fan_monitor['Details'] = fan_monitor['Details'] + "Error FAN:" + k + ' '
        if 'Status' not in fan_monitor.keys():
            fan_monitor['Status'] = 'Ok'
            fan_monitor['Details'] = 'Ok'
        return fan_monitor

    def power(self):
        power_monitor = {}
        command = "ipmitool sdr | grep Power | grep -v Button | awk -F'|' '{print $1,$3}' | xargs"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        power_mon_list = res.split()
        power_monitor['Details'] = ''
        for i in range(0, len(power_mon_list), 2):
            if re.match("Power[0-9]", power_mon_list[i]) != None:
                power_index = power_mon_list[i]
                power_status = power_mon_list[i+1]
                power_monitor[power_index] = power_status
        for k,v in power_monitor.items():
            if v != 'ok' and v != 'nc' and k != 'Details':
                power_monitor['Status'] = 'Error'
                power_monitor['Details'] = power_monitor['Details'] + "Error PS:" + k + ' '
        if 'Status' not in power_monitor.keys():
            power_monitor['Status'] = 'Ok'
            power_monitor['Details'] = 'Ok'
        return power_monitor

class H3C(object):
    def __init__(self):
	pass

    def cpu(self):
	cpu_monitor = {}
        command = "ipmitool sdr | grep CPU |  awk -F'|' '{print $1,$3}' | xargs"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        cpu_monitor['Details'] = ''
        cpu_mon_list = res.split()
        for i in range(0, len(cpu_mon_list), 3):
            if re.match("CPU[0-9]", cpu_mon_list[i]):
                cpu_index = cpu_mon_list[i] + cpu_mon_list[i+1]
                cpu_status = cpu_mon_list[i+2]
                cpu_monitor[cpu_index] = cpu_status
        for k,v in cpu_monitor.items():
            if v != 'ok' and k != 'Details':
                cpu_monitor['Status'] = 'Error'
                cpu_monitor['Details'] = cpu_monitor['Details'] + "Error cpu:" + k + ' '

        if 'Status' not in cpu_monitor.keys():
            cpu_monitor['Status'] = 'Ok'
            cpu_monitor['Details'] = 'Ok'
        return cpu_monitor

    def mem(self):
	mem_monitor = {}
	command1 = "ipmitool sdr | grep Memory | awk -F'|' '{print $2}' | xargs"
	command2 = "ipmitool sdr | grep Memory | awk -F'|' '{print $3}' | xargs"
	process1 = Popen(command1, shell=True, stdout=PIPE, stderr=PIPE)
	process2 = Popen(command2, shell=True, stdout=PIPE, stderr=PIPE)
	(res1, stderr) = process1.communicate()
	(res2, stderr) = process2.communicate()
	mem_monitor['Details'] = ''
	mem_errors = re.split("\\n", res1)[0]
	mem_status = re.split("\\n", res2)[0]
	mem_monitor[mem_errors] = mem_status
	for k,v in mem_monitor.items():
	    if v != 'ok' and k != 'Details':
		mem_monitor['Status'] = 'Error'
		mem_monitor['Details'] = mem_monitor['Details'] + "Error memory:" + k + ' '

	if 'Status' not in mem_monitor.keys():
	    mem_monitor['Status'] = 'Ok'
	    mem_monitor['Details'] = 'Ok'
	return mem_monitor

    def temp(self):
	pass

    def harddisk(self):
	disk_monitor = {}
	command = "hpssacli ctrl slot=0 pd all show status | awk '{print $2,$9}' | xargs"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	disk_mon_list = res.split()
	disk_monitor['Details'] = ''
	for i in range(0, len(disk_mon_list), 2):
	    disk_index = disk_mon_list[i]
	    disk_status = disk_mon_list[i+1]
	    disk_monitor[disk_index] = disk_status
	for k,v in disk_monitor.items():
	    if v != 'OK' and v != 'Non-Critical' and k != 'Details':
		disk_monitor['Status'] = 'Error'
		disk_monitor['Details'] = disk_monitor['Details'] + "Error Disk:" + k + ' '

	common = DiskCommon()
	lsscsi = common.lsscsi()
	if lsscsi['Status'] != 'Ok':
	    disk_monitor['Status'] = lsscsi['Status']
	    disk_monitor['Details'] = disk_monitor['Details'] + lsscsi['Status']

	if 'Status' not in disk_monitor.keys():
	    disk_monitor['Status'] = 'Ok'
	    disk_monitor['Details'] = 'Ok'
	return disk_monitor
    def fans(self):
	pass
    def power(self):
	power_monitor = {}
	command = "hpasmcli -s 'show powersupply'|grep -e 'Power supply' -e 'Condition'"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	power_mon_list = filter(None, re.split("\t|: |\n| #", res))
	power_monitor['Details'] = ''
	for i in range(0, len(power_mon_list), 2):
	    if power_mon_list[i] == 'Power supply':
		power_index = 'Index ' + power_mon_list[i+1]
		power_status = power_mon_list[i+3]
	        power_monitor[power_index] = power_status
	for k,v in power_monitor.items():
	    if v != 'Ok' and k != 'Details':
		power_monitor['Status'] = 'Error'
		power_monitor['Details'] = power_monitor['Details'] + "Error PS:" + k + ' '
	if 'Status' not in power_monitor.keys():
	    power_monitor['Status'] = 'Ok'
	    power_monitor['Details'] = 'Ok'
	return power_monitor

class Supermicro(object):
    def __init__(self):
	pass
    def cpu(self):
	cpu_monitor = {}
        command = "ipmitool sdr | grep CPU|grep Vcore | awk -F'|' '{print $1, $3}' | xargs"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        cpu_monitor['Details'] = ''
        cpu_mon_list = res.split()
        for i in range(0, len(cpu_mon_list), 3):
            if re.match("CPU[0-9]", cpu_mon_list[i]):
                cpu_index = cpu_mon_list[i] + cpu_mon_list[i+1]
                cpu_status = cpu_mon_list[i+2]
                cpu_monitor[cpu_index] = cpu_status
        for k,v in cpu_monitor.items():
            if v != 'ok' and k != 'Details':
                cpu_monitor['Status'] = 'Error'
                cpu_monitor['Details'] = cpu_monitor['Details'] + "Error cpu:" + k + ' '

        if 'Status' not in cpu_monitor.keys():
            cpu_monitor['Status'] = 'Ok'
            cpu_monitor['Details'] = 'Ok'
        return cpu_monitor
    def mem(self):
	pass
    def temp(self):
		temp_monitor = {}
		command = "ipmitool sdr | grep Temp|awk -F '|' '{print $3}'|xargs"
		process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
		(res, stderr) = process.communicate()
		temp_mon_list = filter(None, re.split("''|\ * |: |\n", res))
		temp_monitor['Details'] = ''
		for i in range(0, len(temp_mon_list), 2):
		    if temp_mon_list[i] == 'Index':
			temp_index = 'Index ' + temp_mon_list[i+1]
			temp_status = temp_mon_list[i+3]
		        temp_monitor[temp_index] = temp_status
		for k,v in temp_monitor.items():
		    if v != 'Ok' and k != 'Details':
			temp_monitor['Status'] = 'Error'
			temp_monitor['Details'] = temp_monitor['Details'] + "Error TEMP:" + k + ' '
		if 'Status' not in temp_monitor.keys():
		    temp_monitor['Status'] = 'Ok'
		    temp_monitor['Details'] = 'Ok'
		return temp_monitor

    def harddisk(self):
	disk_monitor = {}
        common = DiskCommon()
        megacli = common.megacli()
        lsscsi = common.lsscsi()
        if megacli['Status'] != 'Ok':
            disk_monitor['Status'] = megacli['Status']
            disk_monitor['Details'] = disk_monitor['Details'] + megacli['Status']
        if lsscsi['Status'] != 'Ok':
            disk_monitor['Status'] = lsscsi['Status']
            disk_monitor['Details'] = disk_monitor['Details'] + lsscsi['Status']

        if 'Status' not in disk_monitor.keys():
            disk_monitor['Status'] = 'Ok'
            disk_monitor['Details'] = 'Ok'
        return disk_monitor

    def fans(self):
	fan_monitor = {}
        command = "ipmitool sdr | grep FAN |grep -v disabled | awk -F '|' '{print $3}' | xargs"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        fan_mon_list = res.split()
        fan_monitor['Details'] = ''
        for i in range(0, len(fan_mon_list), 5):
            fan_index = fan_mon_list[i] + ' ' + fan_mon_list[i+1] + ' ' + fan_mon_list[i+2]
            fan_status = fan_mon_list[i+3]
            fan_monitor[fan_index] = fan_status
        for k,v in fan_monitor.items():
            if v != 'ok' and k != 'Details':
                fan_monitor['Status'] = 'Error'
                fan_monitor['Details'] = fan_monitor['Details'] + "Error FAN:" + k + ' '
        if 'Status' not in fan_monitor.keys():
            fan_monitor['Status'] = 'Ok'
            fan_monitor['Details'] = 'Ok'
        return fan_monitor

    def power(self):
	pass

class IBM(object):
    def __init__(self):
	pass
    def cpu(self):
	cpu_monitor = {}
        command = "ipmitool sdr | grep 'CPU [0-9]'|grep -v Temp | awk -F'|' '{print $1, $3}'"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        cpu_monitor['Details'] = ''
        cpu_mon_list = res.split()
        for i in range(0, len(cpu_mon_list), 3):
            if re.match("CPU[0-9]", cpu_mon_list[i]):
                cpu_index = cpu_mon_list[i] + cpu_mon_list[i+1]
                cpu_status = cpu_mon_list[i+2]
                cpu_monitor[cpu_index] = cpu_status
        for k,v in cpu_monitor.items():
            if v != 'ok' and k != 'Details':
                cpu_monitor['Status'] = 'Error'
                cpu_monitor['Details'] = cpu_monitor['Details'] + "Error cpu:" + k + ' '

        if 'Status' not in cpu_monitor.keys():
            cpu_monitor['Status'] = 'Ok'
            cpu_monitor['Details'] = 'Ok'
        return cpu_monitor

    def mem(self):
	mem_monitor = {}
        command = "ipmitool sdr|grep '^DIMM [0-9]' | grep -v Temp | awk -F '|' '{print $3}'"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        mem_monitor['Details'] = ''
        mem_status = res.split()[0]
        mem_monitor['Memory Status'] = mem_status
        for k,v in mem_monitor.items():
            if v != 'ok' and k != 'Details':
                mem_monitor['Status'] = 'Error'
                mem_monitor['Details'] = mem_monitor['Details'] + "Error memory:" + k + ' '

        if 'Status' not in mem_monitor.keys():
            mem_monitor['Status'] = 'Ok'
            mem_monitor['Details'] = 'Ok'
        return mem_monitor

    def temp(self):
		temp_monitor = {}
		command = "ipmitool sdr | grep Temp|awk -F '|' '{print $1, $3}'|xargs"
		process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
		(res, stderr) = process.communicate()
		temp_mon_list = filter(None, re.split("''|\ * |: |\n", res))
		temp_monitor['Details'] = ''
		for i in range(0, len(temp_mon_list), 4):
		    if temp_mon_list[i] == 'Index':
			temp_index = 'Index ' + temp_mon_list[i+1]
			temp_status = temp_mon_list[i+3]
		        temp_monitor[temp_index] = temp_status
		for k,v in temp_monitor.items():
		    if v != 'Ok' and k != 'Details':
			temp_monitor['Status'] = 'Error'
			temp_monitor['Details'] = temp_monitor['Details'] + "Error TEMP:" + k + ' '
		if 'Status' not in temp_monitor.keys():
		    temp_monitor['Status'] = 'Ok'
		    temp_monitor['Details'] = 'Ok'
		return temp_monitor

    def harddisk(self):
	disk_monitor = {}
        common = DiskCommon()
        megacli = common.megacli()
        lsscsi = common.lsscsi()
        if megacli['Status'] != 'Ok':
            disk_monitor['Status'] = megacli['Status']
            disk_monitor['Details'] = disk_monitor['Details'] + megacli['Status']
        if lsscsi['Status'] != 'Ok':
            disk_monitor['Status'] = lsscsi['Status']
            disk_monitor['Details'] = disk_monitor['Details'] + lsscsi['Status']

        if 'Status' not in disk_monitor.keys():
            disk_monitor['Status'] = 'Ok'
            disk_monitor['Details'] = 'Ok'
        return disk_monitor

    def fans(self):
	fan_monitor = {}
        command = "ipmitool sdr | grep Fan|grep RPM|awk -F '|' '{print$1, $3}'|xargs"
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (res, stderr) = process.communicate()
        fan_mon_list = res.split()
        fan_monitor['Details'] = ''
        for i in range(0, len(fan_mon_list), 4):
            fan_index = fan_mon_list[i] + ' ' + fan_mon_list[i+1] + ' ' + fan_mon_list[i+2]
            fan_status = fan_mon_list[i+3]
            fan_monitor[fan_index] = fan_status
        for k,v in fan_monitor.items():
            if v != 'ok' and k != 'Details':
                fan_monitor['Status'] = 'Error'
                fan_monitor['Details'] = fan_monitor['Details'] + "Error FAN:" + k + ' '
        if 'Status' not in fan_monitor.keys():
            fan_monitor['Status'] = 'Ok'
            fan_monitor['Details'] = 'Ok'
        return fan_monitor

    def power(self):
		power_monitor = {}
		command = "ipmitool sdr | grep Power |grep -v ^Power|awk -F '|' '{print $3}'|xargs"
		process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
		(res, stderr) = process.communicate()
		power_mon_list = filter(None, re.split("\t|: |\n| #", res))
		power_monitor['Details'] = ''
		for i in range(0, len(power_mon_list), 2):
		    if power_mon_list[i] == 'Power supply':
			power_index = 'Index ' + power_mon_list[i+1]
			power_status = power_mon_list[i+3]
		        power_monitor[power_index] = power_status
		for k,v in power_monitor.items():
		    if v != 'Ok' and k != 'Details':
			power_monitor['Status'] = 'Error'
			power_monitor['Details'] = power_monitor['Details'] + "Error PS:" + k + ' '
		if 'Status' not in power_monitor.keys():
		    power_monitor['Status'] = 'Ok'
		    power_monitor['Details'] = 'Ok'
		return power_monitor

class Lenovo(object):
    def __init__(self):
	pass

class SuperCloud(object):
    def __init__(self):
	pass

class Cisco(object):
    def __init__(self):
	pass

class DiskCommon(object):
    def __init__(self):
	pass

    def megacli(self):
	megacli_monitor = {}
	command = "/opt/MegaRAID/MegaCli/MegaCli64 -PDList -aAll -NoLog|grep -e 'Enclosure Device ID' -e 'Slot Number' -e 'Media Error Count' | cut -d':' -f2 | xargs"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	megacli_mon_list = res.split()
	megacli_monitor['Details'] = ''
	for i in range(0, len(megacli_mon_list), 3):
	    megacli_index = megacli_mon_list[i] + ':' + megacli_mon_list[i+1]
	    megacli_status = megacli_mon_list[i+2]
	    megacli_monitor[megacli_index] = megacli_status
	for k,v in megacli_monitor.items():
	    if v != '0' and k != 'Details':
		megacli_monitor['Status'] = 'Error'
		megacli_monitor['Details'] = megacli_monitor['Details'] + "Error Disk:" + k + ' '
	if 'Status' not in megacli_monitor.keys():
	    megacli_monitor['Status'] = 'Ok'
	    megacli_monitor['Details'] = 'Ok'
        return megacli_monitor

    def lsscsi(self):
	lsscsi_monitor = {}
	command = "lsscsi -l| awk '{print $1,$7}' | awk '{print $1}' | xargs"
	process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
	(res, stderr) = process.communicate()
	lsscsi_mon_list = res.split()
	lsscsi_monitor['Details'] = ''
	for i in range(0, len(lsscsi_mon_list), 2):
	    lsscsi_index = lsscsi_mon_list[i]
	    lsscsi_status = lsscsi_mon_list[i+1]
	    lsscsi_monitor[lsscsi_index] = lsscsi_status
	for k,v in lsscsi_monitor.items():
	    if v != 'state=running' and k != 'Details':
		lsscsi_monitor['Status'] = 'Error'
		lsscsi_monitor['Details'] = lsscsi_monitor['Details'] + "Error Disk:" + k + ' '
	if 'Status' not in lsscsi_monitor.keys():
	    lsscsi_monitor['Status'] = 'Ok'
	    lsscsi_monitor['Details'] = 'Ok'
        return lsscsi_monitor

    def sas2ircu(self):
	pass
    def sas3ircu(self):
	pass

class HardInfo(object):

    def __init__(self):

        vendor_command = "dmidecode -s system-manufacturer | grep -v '^#' | awk '{print $1}' | tr -d '\n'"
        vendor_process = Popen(vendor_command, shell=True, stdout=PIPE, stderr=PIPE)
        (vendor, stderr) = vendor_process.communicate()
	self.vendor = vendor
        model_command = "dmidecode -s system-product-name|grep -v '^#' | tr -d '\n'"
        model_process = Popen(model_command, shell=True, stdout=PIPE, stderr=PIPE)
        (model, stderr) = model_process.communicate()
	self.model = model

 	self.read_settings()

    def read_settings(self):
	""" Reads the settings from the zabbix-uos-hardinfo.cfg file"""

	config = ConfigParser.SafeConfigParser()
	config.read(os.path.dirname(os.path.realpath(__file__)) + '/zabbix-uos-hardinfo.cfg')

	self.cpu_stat = config.getboolean(self.vendor, 'cpu')
	self.mem_stat = config.getboolean(self.vendor, 'memory')
	self.disk_stat = config.getboolean(self.vendor, 'harddisk')
	self.fans_stat = config.getboolean(self.vendor, 'fans')
	self.power_stat = config.getboolean(self.vendor, 'power')
	self.temp_stat = config.getboolean(self.vendor, 'temperature')

    def get_info(self, vendor,hard_stat):
	""" Get chassis status. """

	mac_info = {}

	if vendor == 'Dell':
	    mac = Dell()
	elif self.vendor == 'HP':
	    mac = HP()
	elif self.vendor == 'Inspur':
	    mac = Inspur()
	elif self.vendor == 'Huawei':
	    mac = Huawei()
	elif self.vendor == 'Red':
	    mac = Dell()
	elif self.vendor == 'H3C':
	    mac = H3C()
	elif self.vendor == 'Supermicro':
	    mac = Supermicro()
	elif self.vendor == 'IBM':
	    mac = IBM()
	else:
	    pass

	if hard_stat == 'cpu':
	    mac_info['cpu'] = mac.cpu()
	if hard_stat == 'mem':
	    mac_info['mem'] = mac.mem()
	if hard_stat == 'temp':
	    mac_info['temp'] = mac.temp()
	if hard_stat == 'disk':
	    mac_info['disk'] = mac.harddisk()
	if hard_stat == 'fans':
	    mac_info['fans'] = mac.fans()
	if hard_stat == 'power':
	    mac_info['power'] = mac.power()

	return self.json_from_dict(mac_info, True)

    def json_from_dict(self, data, pretty=False):
 	if pretty:
	    return json.dumps(data, sort_keys=True, indent=2)
	else:
	    return json.dumps(data)

if __name__ == '__main__':
    #arguments = docopt(__doc__, version='uos_hardinfo 0.1')
    #print arguments
    mac = HardInfo()
    macinfo = mac.get_info(mac.vendor,sys.argv[1])
    print macinfo
