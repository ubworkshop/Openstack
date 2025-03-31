#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: zhuima
# Date: 2017-06-21 update V4


"""
1、引入warnings模块，去除urllib3访问https站点的warning信息
2、python正常传参数应该是sys.argv[1] sys.argv[2]
3、zabbix传参的时候应该是sys.argv[2]  sys.argv[3]
"""

import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    import requests
    import json
    import sys
    import time


reload(sys)
sys.setdefaultencoding( "utf-8" )


title = sys.argv[2]
content = sys.argv[3]


class Token(object):
    def __init__(self, corpid, corpsecret):
        self.baseurl = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}'.format(corpid, corpsecret)
        self.expire_time = sys.maxint


    def get_token(self):
        """
        微信Token过期时间为2小时，每天的请求数不能超过2000次
        这里使用时间戳判断，避免每次请求都去重新获取一次
        requests.packages.urllib3.disable_warnings() 防止ssl类的warnings信息
        >>> qs_token = Token(corpid=corpid, corpsecret=corpsecret).get_token()
        token:
            AVOg9PjnEC9dEl1UIMeAgN5adedkLBo7J538GdLLvvinkmpL356Ic341g2WTasX3EDjc7mf06J7GdkyNI0mUB4dfZhuRsdfgSNT7Sf1v2ceiND1uibTQQLECduF_Omdg8RElKMA_UK5qM4AXwSGGQjLqJdX5ZLWeZ-Af1xCTtLDdoHu75VMVOwvEApbmFcxRYsj0So8FEGXSyH5dxxka-3mvMqYESX_lzEIDSFKHcMr3yd1ZJgRlb7_Ejzq_loVj4sT4B7qtCjOC2PRmuyQ6aRcU0Z55ePLJpoz-8KS4W7Qgzg
        full result:
            {u'access_token': u'AVOg9PjnEC9dEl1UIMeAgN5adedkLBo7J538GdLLvvinkmpL356Ic341g2WTasX3EDjc7mf06J7GdkyNI0mUB4ZsdfsdegSNT7Sf1v2ceiND1uibTQQLECduF_Omdg8RElKMA_UK5qM4AXwSGGQjLqJdX5ZLWeZ-Af1xCTtLDdoHu75VMVOwvEApbmFcxRYsj0So8FEGXSyH5dxxka-3mvMqYESX_lzEIDSFKHcMr3yd1ZJgRlb7_Ejzq_loVj4sT4B7qtCjOC2PRmuyQ6aRcU0Z55ePLJpoz-8KS4W7Qgzg', u'expires_in': 7200, u'errcode': 0, u'errmsg': u'ok'}
        """
        if self.expire_time > time.time():
            requests.packages.urllib3.disable_warnings()
            resp = requests.get(self.baseurl, verify=False)
            ret = resp.json()
            if ret.get('errcode') != 0:
                print  ret.get('errmsg')
                sys.exit(1)
            self.expire_time = time.time() + ret.get('expires_in')
            self.access_token = ret.get('access_token')
        return self.access_token


def send_msg(title, content):
    """
    1、corpid 和 corpsecret要从后台获取
    2、agentid 也是从后台获取
    >>> send_msg("测试", "这个是功能测试")
    result:
        {u'invaliduser': u'', u'errcode': 0, u'errmsg': u'ok'}
    """

    corpid = 'wxa1438f39b3e86866'
    corpsecret = 'pj2VOvaqvHPY_9y2wbBSiOxE-DEhF2fx5yZQoknstiM'
    qs_token = Token(corpid=corpid, corpsecret=corpsecret).get_token()
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}".format(
        qs_token)
    payload = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": "1000004",
        "text": {
            "content": "标题:{0}\n内容:{1}".format(title, content)
        },
        "safe": "0"
    }
    requests.packages.urllib3.disable_warnings()
    ret = requests.post(url, data=json.dumps(payload, ensure_ascii=False), verify=False)
    return ret.json()


if __name__ == '__main__':
    #title = "这是测试"
    #content = "豆豆亲笔书写"
    print send_msg(title, content)
