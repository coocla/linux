#!/usr/bin/env python
#-*- coding:utf-8 -*-
#Autho: coocla
#When: 2014/06/14
import MySQLdb
import daemon
import sys
import json
import logger
from DBUtils.PooledDB import PooledDB
from logger import __opts__
from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler

logger.setup_log(root=__file__)
LOGS = logger.getLogger(__file__)

def mysql_call():
    host = __opts__["mysql.host"]
    user = __opts__["mysql.user"]
    port = __opts__["mysql.port"]
    passwd = __opts__["mysql.passwd"]
    db = __opts__["mysql.db"]

    try:
        pool = PooledDB(creator=MySQLdb, maxusage=100, host=host, user=user, passwd=passwd, db=db, port=port)
        conn = pool.connection()
    except:
        LOGS.error("Can't connect to MySQL server on %s" % host)

    return conn

conn = mysql_call()
cursor = conn.cursor()


class Server(TCPServer, ThreadingMixIn):
    pass

class Handler(StreamRequestHandler):
    def handle(self):
        data = self.request.recv(2048)
        data = format_call(data)
        if data:
            storage_db(data)

def format_call(data):
    data = eval(data)
    ret = {}
    if isinstance(data, dict):
        ret["logtype"] = data.keys()[0]
        if ret["logtype"] == "online":
            logbody = [(x.split("=")[0], x.split("=")[1]) for x in data.values()[0].split("&")]
            ret.update(dict(logbody))
            return ret
        else:
            return {}
    LOGS.warning("invalid data, drop it")
    return {}


def storage_db(data):
    for k,v in data.iteritems():
        try:
            v = int(v)
            data[k] = v
        except:
            pass
    sql = "insert into %(logtype)s (sid, dept, usercount, time) value (%(sid)d, %(dept)d, %(usercount)d, %(time)d)" % data
    try:
        cursor.execute(sql)
        cursor.execute("COMMIT")
    except Exception,e:
        cursor.execute("ROLLBACK")
        LOGS.error("%s" % e)

class RunServer(daemon.Daemon):
    def run(self):
        server = Server((__opts__["server"], __opts__["port"]), Handler)
        try:
            server.serve_forever()
            LOGS.info("Start server listen: %s:%d" % (__opts__["server"], __opts__["port"]))
        except Exception,e:
            LOGS.error("Start server error, %s" % e)
    

if __name__ == '__main__':
    if sys.argv[1] == "start":
        log_pos = RunServer('/var/run/log_monitor_server.pid')
        log_pos.start()
    if sys.argv[1] == "stop":
        log_pos = RunServer('/var/run/log_monitor_server.pid')
        log_pos.stop()
    if sys.argv[1] == "restart":
        log_pos = RunServer('/var/run/log_monitor_server.pid')
        log_pos.restart()
