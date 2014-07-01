#!/usr/bin/python2.4 
# -*- coding:utf-8 -*-
# Author: http://blog.coocla.org

import paramiko
import pyinotify
import os
import commands
import time
import sys
from datetime import datetime

WATCHDIR="/data/"
HOST="192.168.128.99"
USER="FPT"
PASS="password"
pid_file="/var/run/autoupload.pid"
log_file="/data/autoipload.log"
log_file_obj=file(log_file, "w+")

class OnCreateClick(pyinotify.ProcessEvent):
  def process_IN_CLOSE_WRITE(self, event):
    abspath = os.path.join(event.path, event.name)
    if os.path.isdir(abspath):
      print [Now],": Found new directory %s" % event.name
    elif os.path.isfile(abspath):
      print [Now],": Found new file %s" % event.name
      relname = abspath.split(WATCHDIR)[1]
      relpath = os.path.dirname(relname)
      upload(abspath, relpath, relname)

def main():
  wm = pyinotify.WatchManager()
  notifier = pyinotify.Notifier(wm, OnCreateClick())
  wm.add_watch(WATCHDIR, pyinotify.IN_CLOSE_WRITE, rec=True, auto_add=True)
  notifier.loop(daemonize=True, pid_file=pid_file, stdout=log_file)


def upload(abspath, relpath, relname):
  client = paramiko.Transport((HOST,22))
  client.connect(username=USER, password=PASS)
  sftp = paramiko.SFTPClient.from_transport(client)
  sftp.chdir('Upload')
  try:
    sftp.chdir(relpath)
  except:
    print [Now],": No such file or directory %s" % relpath
    log_file_obj.write("[%s] : No such file or directory %s \n" % (str(Now), relpath))
    for dir_name in relpath.split(os.path.sep):
      print [Now],": Create directory %s" % dir_name
      log_file_obj.write("[%s] : Create directory %s \n" % (str(Now), dir_name))
      try:
        sftp.mkdir(dir_name)
      except:
        pass
      sftp.chdir(dir_name)

  sftp.chdir('/Upload')
  try:
    print [Now],"local: %s ,remote: %s" % (abspath, relname)
    log_file_obj.write("[%s] : local: %s ,remote: %s \n" % (str(Now), abspath, relname))
    sftp.put(abspath, relname)
    print [Now],": Upload file %s to %s success." % (abspath, relname)
    log_file_obj.write("[%s] : Upload file %s to %s success. \n" % (str(Now), abspath, relname))
  except Exception,e:
    print [Now],": Upload file %s to %s error." % (abspath, relname)
    log_file_obj.write("[%s] : Upload file %s to %s error. \n" % (str(Now), abspath, relname))
    print "[Error]: %s" % e
    log_file_obj.write("[%s] : [Error] %s \n" % (str(Now), e))
  client.close()
  log_file_obj.flush()

if __name__ == '__main__':
  Now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  if os.path.isfile(pid_file):
    os.remove(pid_file)
  main()
