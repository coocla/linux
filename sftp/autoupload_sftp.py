#!/usr/bin/python2.4 
# -*- coding:utf-8 -*-
# Author: http://blog.coocla.org

import paramiko
import pyinotify
import os

WATCHDIR="xxxxxx"
HOST="xxxxxx"
USER="xxxxxx"
PASS="xxxxxx"
pid_file="/var/run/autoupload.pid"

class OnCreateClick(pyinotify.ProcessEvent):
  def process_IN_CLOSE_WRITE(self, event):
    abspath = os.path.join(event.path, event.name)
    if os.path.isdir(abspath):
      pass
    elif os.path.isfile(abspath):
      print "Found new file: %s" % event.name
      relname = abspath.split(WATCHDIR)[1]
      relpath = os.path.dirname(relname)
      upload(abspath, relpath, relname)

def main():
  wm = pyinotify.WatchManager()
  notifier = pyinotify.Notifier(wm, OnCreateClick())
  wm.add_watch(WATCHDIR, pyinotify.IN_CLOSE_WRITE, rec=True, auto_add=True)
  notifier.loop(daemonize=True, pid_file=pid_file)


def upload(abspath, relpath, relname):
  client = paramiko.Transport((HOST,22))
  client.connect(username=USER, password=PASS)
  sftp = paramiko.SFTPClient.from_transport(client)
  sftp.chdir('/Upload')
  try:
    print "local: %s ,remote: %s" % (abspath, relname)
    sftp.chdir(relpath)
    print "Upload file %s to %s success." % (abspath, relname)
  except:
    print "No such file or directory %s" % relpath
    for dir_name in relpath.split(os.path.sep):
      print "Create directory %s" % dir_name
      sftp.mkdir(dir_name)
      sftp.chdir(dir_name)

  sftp.chdir('/Upload')
  try:
    print "local: %s ,remote: %s" % (abspath, relname)
    sftp.put(abspath, relname)
    print "Upload file %s to %s success." % (abspath, relname)
  except Exception,e:
    print "Upload file %s to %s error." % (abspath, relname)
    print "[Error]: %s" % e
  client.close()

if __name__ == '__main__':
  if os.path.isfile(pid_file):
    os.remove(pid_file)
  main()
