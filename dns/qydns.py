#!?usr/bin/env python
#-*- coding:utf-8 -*-
"""
Dump all record form dnspod.
"""

import httplib, urllib
import socket
import re

try: import json
except: import simplejson as json


class ApiCn:
    def __init__(self, email, password, **kw):
        self.base_url = "dnsapi.cn"
        self.params = dict(
                login_email = email,
                login_password = password,
                format = "json")
        self.params.update(kw)
        self.path = None

    def request(self, **kw):
        self.params.update(kw)
        if not self.path:
            name = re.sub(r'([A-Z])', r'.\1', self.__class__.__name__)
            self.path = "/" + name[1:]
        conn = httplib.HTTPSConnection(self.base_url)
        headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/json",
                "User-Agent": "dnspod-python/0.01 (im@chuangbo.li; DNSPod.CN API v2.8)"}
        conn.request("POST", self.path, urllib.urlencode(self.params), headers)

        response = conn.getresponse()
        data = response.read()
        conn.close()
        ret = json.loads(data)
        if ret.get("status", {}).get("code", None) == "1":
            return ret
        else:
            raise Exception(ret)

    __call__ = request


class _DomainApiBase(ApiCn):
    """
    Domain base class
    """
    def __init__(self, domain_id, **kw):
        kw.update(dict(domain_id = domain_id))
        ApiCn.__init__(self, **kw)

class _RecordBase(_DomainApiBase):
    """
    Record base class
    """
    def __init__(self, record_id, **kw):
        kw.update(dict(record_id = record_id))
        _DomainApiBase.__init__(self, **kw)

class DomainList(ApiCn):
    """
    Return all domain info
    """
    pass

class DomainId(ApiCn):
    """
    Return the domain id on domain name
    """
    def __init__(self, domain, **kw):
        kw.update(dict(domain = domain))
        ApiCn.__init__(self, **kw)

class RecordList(_DomainApiBase):
    """
    Return the record list on domain id
    """
    pass


class Domain(object):
    def __init__(self, email, password):
        self.login_email = email
        self.password = password

    def List(self):
        """
        Return list about doamin, doamin_id, records
        """
        ret = json.loads(json.dumps(DomainList(self.login_email, self.password)()))["domains"]
        return map(lambda x: {"name": x["name"], "id": x["id"], "records": x["records"]}, ret)

    def SendDomain(self):
        for single in self.List():
            self.LastRet(single)
        #self.LastRet({'records': u'836', 'name': u'youxi.com', 'id': 225747})

    def LastRet(self, single_domain):
        index = 0
        while 1:
            print "@@ ### DEBUG ### @@"
            print index
            if index+499 < int(single_domain["records"]):
                ret = RecordList(
                        email = self.login_email,
                        password = self.password,
                        domain_id = single_domain["id"],
                        offset = index,
                        length = index+499)()
                index += 500
                for i in json.loads(json.dumps(ret))["records"]:
                    if i["name"] in ["@", "*"]:
                        continue
                    OutputFile(rfile, ifile).record(i["name"] + "." + single_domain["name"])
                    OutputFile(rfile, ifile).ip(i["value"])
            else:
                ret = RecordList(
                        email = self.login_email,
                        password = self.password,
                        domain_id = single_domain["id"],
                        offset = index,
                        length = int(single_domain["records"]) - index)()
                for i in json.loads(json.dumps(ret))["records"]:
                    if i["name"] in ["@", "*"]:
                        continue
                    OutputFile(rfile, ifile).record(i["name"] + "." + single_domain["name"])
                    OutputFile(rfile, ifile).ip(i["value"])
                break


class OutputFile(object):
    def __init__(self, recordfile, ipfile):
        self.f_record = recordfile
        self.f_ip = ipfile

    def record(self, data):
        f_obj = file(self.f_record, 'a+')
        f_obj.write(str(data) + "\n")

    def ip(self, data):
        f_obj = file(self.f_ip, 'a+')
        f_obj.write(str(data) + "\n")

if __name__ == "__main__":
    rfile = '/tmp/record.txt'
    ifile = '/tmp/iplist.txt'
    Domain("xxxxxx", "xxxxxxx").SendDomain()
