#!/usr/bin/env python
# coding: utf-8
# wuxiaoliu

import hashlib
import requests
import argparse
import logging
from urllib import urlencode

parser = argparse.ArgumentParser("./sms.py",
                                 description='Zabbix SMS Alerta')

parser.add_argument('username', default='username',
                    help="SMS username")
parser.add_argument('passwd', default='password',
                    help="SMS password")
parser.add_argument('epid', default='0',
                    help="SMS epid")
parser.add_argument('sign', default='sign',
                    help="SMS sign")
parser.add_argument('phone', default='0',
                    help="SMS phone number")
parser.add_argument('message', default='0',
                    help="SMS message")

args = parser.parse_args()

log_file = '/var/log/zabbix/zabbix_sms.log'

logging.basicConfig(filename = log_file,
                    format = "%(levelname)-10s %(asctime)s %(message)s",
                    level = logging.INFO)

API_URL = "http://q.hl95.com:8061"

params = {'username': args.username,
          'password': hashlib.new("md5", args.passwd).hexdigest(),
          'epid': args.epid,
          'phone': args.phone,
          'message': (u"【%s】%s" %(\
                      args.sign.decode("utf-8"),\
                      args.message.decode("utf-8"))).\
                      encode('gb2312')}


if __name__ == "__main__":
    try:
        response = requests.get(API_URL + '?' + urlencode(params),timeout=10)
        message_str = "Message: {notify} | send to: {phone} | result: {result}".format(
                notify=params.get('message'),
                phone=args.phone,
                result=response.content
                )
        logging.info(message_str.decode("gb2312"))
    except:
        logging.exception("Exception Logged")
