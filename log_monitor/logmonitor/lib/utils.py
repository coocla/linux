#-*- coding:utf-8 -*-
import sys
import yaml

Conf_File = "/etc/logmonitor/logmonitor.conf"

def get_options(LOG=None):
    try:
        f = file(Conf_File, "r")
        return yaml.load(f.read())
    except Exception,e:
        print "load config %s" % e
        sys.exit(5)

