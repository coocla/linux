#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import sys
import time
import yaml
import socket
import threading
from datetime import datetime

from logmonitor.lib import utils
from logmonitor.lib import daemon
from logmonitor.lib import log as logging

LOG = logging.getLogger(__name__)
options = utils.get_options(LOG=LOG)

def generate_timename(isdir=False):
    """dynamic generate dirname or timestamp"""
    if not isdir:
        return datetime.now().strftime("%Y%m%d")
    return datetime.now().strftime("%Y-%m-%d")

def logfile_call():
    """Return list about match inputfile options"""
    logfile_dir = options['input_dir'] + "/" + generate_timename(isdir=True)
    logfile_dir = os.path.normpath(logfile_dir)
    match_input_file = options['inputfile']
    try:
        logfile = os.listdir(logfile_dir)
    except Exception,e:
        LOG.error("list logdir %s" % e)
        return []
    match_file = filter(lambda x: filter(lambda y: x.startswith(y), match_input_file), logfile)
    return map(lambda x: os.path.normpath(logfile_dir + "/" + x), match_file)

def tail_f(logfile):
    try:
        LOG.info("Create file object for file %s" % logfile)
        f_obj = file(logfile, "r")
    except IOError:
        LOG.error("No such file or directory for %s" % logfile)
        return "No such file or directory"
    timestamp = generate_timename()
    today = generate_timename(isdir=True)
    if options["posfile_dir"].startswith("/"):
        posfile_dir = options["posfile_dir"]
    else:
        posfile_dir = os.getcwd() + "/" + options["posfile_dir"]
    posfile = os.path.normpath(posfile_dir + "/" + today + os.path.splitext(logfile.split("/")[-1])[0] + ".pos")
    LOG.info("Current pos file is %s" % posfile)
    logtype = filter(lambda x: logfile.split("/")[-1].startswith(x), options["inputfile"])[0]
    while True:
        try:
            current_pos = file(posfile, "r").readline().strip()
            if not current_pos:
                current_pos = f_obj.tell()
        except:
            current_pos = f_obj.tell()
        f_obj.seek(int(current_pos))
        data = f_obj.readline().strip()
        if not data:
            time.sleep(options.get("interval", 120))
            continue
        data = str({logtype: data})
        if send_data(data):
            try:
                current_pos = f_obj.tell()
                file(posfile, "w").write(str(current_pos))
            except Exception,e:
                LOG.error("Fuck pos file made error, %s" % e)
        current_timestamp = generate_timename()
        if timestamp != current_timestamp:
            file(posfile, "w").write(str(0))
            break
            
def send_data(data):
    while True: 
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((options.get("server", "127.0.0.1"), options.get("port", 5678)))
            break
        except:
            LOG.error("Can not connect to server, try connect...")
            time.sleep(10)
    try:
        s.sendall(data)
        s.close()
        LOG.debug('Send data "%s" success.' % data)
        return True
    except Exception,e:
        s.close()
        LOG.error("Fuck send data error, %s" % e)
        return False

def reset_posfile():
    posfile_dir = options["posfile_dir"]
    if not posfile_dir.startswith("/"):
        posfile_dir = os.getcwd() + "/" + posfile_dir
    for file in os.listdir(posfile_dir):
        targetFile = os.path.join(posfile_dir, file)
        if os.path.isfile(targetFile):
            file(targetFile, "w").write("0")
     

def fork_thread():
    while not logfile_call():
        LOG.info("Not found logfile dir or no match file")
        time.sleep(options["interval"])
    LOG.info("Found logfile %s" % logfile_call())
    starttime = generate_timename()
    sended_file_list = []
    while True:
        if starttime != generate_timename():
            LOG.info("Switch log dir to %s" % generate_timename(isdir=True))
            clean_oldposfile()
            send_file_list = logfile_call()
            sended_file_list = []
            starttime = generate_timename()
            LOG.info("Rest timestamp to %s" % starttime)
            reset_posfile()
            LOG.info("Rest pos file to start point")
        else:
            send_file_list = logfile_call()
        if send_file_list:
            for logfile in send_file_list:
                if logfile in sended_file_list:
                    continue
                send_file_list.remove(logfile)
                sended_file_list.append(logfile)
                if os.path.isfile(logfile):
                    LOG.info('Match logfile "%s"' % logfile)
                    t = threading.Thread(target=tail_f, args=(logfile,))
                    LOG.info('Start thread %s' % t.getName())
                    t.start()
        time.sleep(120)

def check_enum():
    for arg in options:
        LOG.info("Check running environment.")
        if arg.endswith("dir"):
            if os.path.isdir(options[arg]):
                LOG.info("Dir %s ok" % options[arg])
                return True
            try:
                os.mkdir(options[arg])
                LOG.info('"%s" not a directory, create it' % options[arg])
                return True
            except Exception,e:
                LOG.info("Create %s fail, %s" % (options[arg],e))
                return False

def clean_oldposfile():
    for old_pos in os.listdir(options["posfile_dir"]):
        today = generate_timename(isdir=True)
        if not old_pos.startswith(today):
            try:
                os.remove(old_pos)
                LOG.info("Delete old pos file %s" % old_pos)
            except Exception,e:
                LOG.error("Delete old pos file %s Fail" % old_pos)


class RunClient(daemon.Daemon):
    def run(self):
        if check_enum():
            clean_oldposfile()
            fork_thread()

if __name__ == '__main__':
    Client = RunClient('/var/run/logmonitor_client.pid')
    getattr(Client, sys.argv[1])()
