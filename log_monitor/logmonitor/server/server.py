#-*- coding:utf-8 -*-
import MySQLdb
import sys
import json
from DBUtils.PooledDB import PooledDB
from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler


from logmonitor.lib import utils
from logmonitor.lib import daemon
from logmonitor.lib import log as logging

LOG = logging.getLogger(__name__)
print LOG
options = utils.get_options()

class Server(TCPServer, ThreadingMixIn):
    pass

class Handler(StreamRequestHandler):
    def handle(self):
        Storage = Format_and_Save()
        data = self.request.recv(2048)
        try:
            data = json.dumps(data)
        except Exception,e:
            data = ""
            LOG.warning("Invalid data from %s drop it" % self.client_address)
            LOG.debug("Format data error %s" % e)

        if data and isinstance(data, dict):
            LOG.debug("Recv %s log from %s" % (data, self.client_address))
            type = '_'.join(data.keys()[0].split("_")[:-2])
            print data
            

class RunServer(daemon.Daemon):
    def run(self):
        server = Server((options["server"], options["port"]), Handler)
        LOG.info("Start server listen %s:%s" % (options["server"], options["port"]))
        try:
            server.serve_forever()
        except Exception,e:
            LOG.error("Server forever %s" % e)


class MySQL():
    def __init__(self, start=5, max_idle=15, max_connect=30):
        host = options["mysql.host"]
        user = options["mysql.user"]
        port = options["mysql.port"]
        passwd = options["mysql.passwd"]
        db = options["mysql.db"]

        try:
            Pool = PooledDB(
                    creator = MySQLdb, \
                    mincached = start, \
                    maxcached = max_idle, \
                    maxconnections = max_connect, \
                    host = host, \
                    user = user, \
                    port = port, \
                    passwd = passwd, \
                    db = db, \
                    charset = "utf8")
            conn = Pool.connection()
            self.cursor = conn.cursor()
        except Exception,e:
            LOG.error("Initial mysql connect pool error %s" % e)

    def get_exists(self, sql):
        try:
            self.cursor.excute(sql)
            data = self.cursor.fetchall()
        except:
            data = []
        return data

    def insert_or_update(self, sql):
        try:
            self.cursor.excute(sql)
            self.cursor.excute("COMMIT")
            return True
        except Exception,e:
            self.cursor.excute("ROLLBACK")
            LOG.error("Insert or Update error %s" % e)
            return False



if __name__ == '__main__':
    Server = RunServer('/var/run/log_monitor_server.pid')
    getattr(Server, sys.argv[1])()
