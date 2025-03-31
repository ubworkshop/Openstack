#!/usr/bin/python  
#coding=utf-8  
  
import urllib  
import urllib2  
import sys
  
def post(url, data):   
    req = urllib2.Request(url)  
    data = urllib.urlencode(data)  
    #enable cookie  
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())  
    response = opener.open(req, data)  
    return response.read()  
  
def main():  
    posturl = "http://itsm.cloudtds.com.cn/api/monitor/alarm/save"
    description=sys.argv[1]
    title=sys.argv[2]
    print description
    print title
    data = {'priority':'2','description':description,'title':title,'postType':'1'}
 
    print post(posturl, data)  
  
if __name__ == '__main__':  
    main()  
