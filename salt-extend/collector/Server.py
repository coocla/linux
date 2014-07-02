"""
Listen salt event
collect swith info from grains
insert or update grains and pillar into postgresql
"""

#Python lib
import json
import re, os, sys
import datetime
import daemon
import msgpack
import yaml

#Salt lib
import salt.config
import salt.utils.event

#Custom lib
import log as logging
import models

__opts__ = salt.config.client_config("/etc/salt/master")
logging.setup_log(root=__file__, LogDir=logging.options["LogDir"], LogLevel=logging.options["LogLevel"])
LOG = logging.getLogger(__name__)

class ListenEvent(daemon.Daemon):
    def run(self):
        event = salt.utils.event.MasterEvent(__opts__["sock_dir"])
        for eachevent in event.iter_events(full=True):
            if "salt/job/" in eachevent["tag"]:
                data = eachevent["data"]
                if data.has_key("return"):
                    if data["fun"] in [
                            "grains.append",
                            "grains.remove",
                            "grains.setval",
                            "grains.setvals",
                            "grains.items"]:
                        """Filter grains function"""
                        LOG.debug("%s grains action %s %s" % (data["id"], data["fun"], data["return"]))
                        getattr(self, data["fun"].split(".")[1])\
                                (data["id"], data["return"])
                    elif data["fun"] in [
                            "saltutil.sync_grains",
                            "saltutil.sync_all",
                            "saltutil.sync_modules",
                            "saltutil.refresh_pillar"]:
                        """Filter pillar function"""
                        LOG.debug("%s pillar action %s %s" % (data["id"], data["fun"], data["return"]))
                        id = data["id"]
                        if self.is_same(id):
                            LOG.debug("%s pillar has update, update" % id)
                            data = self.get_by_cache(id)
                            values["id"] = id
                            values["type"] = "server"
                            values["property"] = data
                            models.insert_or_update(values)
                        else:
                            LOG.debug("%s pillar has not update, continue" % id)
                if data["fun"] == "grains.delval":
                    if data.has_key("return") and data["success"]:
                        LOG.debug("grains action %s %s for %s" % (data["fun"], data["id"], data["return"]))
                        getattr(self, "delval")(data["id"], data["fun_args"])


    def items(self, id, data):
        assets = models.get_by_id(id)
        if assets:
            assets = dict(assets.property)
        else:
            assets = self.get_by_cache(id)
        values = {}
        switch = data.pop("switch")
        if assets["grains"].has_key("switch"):
            assets["grains"].pop("switch")
        assets["grains"] = data
        values["id"] = id
        values["type"] = "server"
        values["property"] = assets
        models.insert_or_update(values)
        self.set_switch(switch)


    def append(self, id, data):
        if isinstance(data, dict):
            assets = models.get_by_id(id)
            property = dict(assets.property)
            property["grains"].update(data)
            values = {}
            values["id"] = assets.id
            values["type"] = assets.type
            values["property"] = property
            models.insert_or_update(values)
        else:
            LOG.error("append %s not a dict" % data)


    def setval(self, id, data):
        self.append(id, data)


    def remove(self, id, data):
        self.append(id, data)


    def delval(self, id, fun_args):
        if isinstance(fun_args, list):
            assets = models.get_by_id(id)
            property = dict(assets.property)
            if filter(lambda x: isinstance(x, dict), fun_args):
                try:
                    property["grains"].pop(str(fun_args[0]))
                except Exception,e:
                    LOG.error("%s delete grains error %s" % (id, e))
            else:
                property["grains"][str(fun_args[0])] = None
            values = {}
            values["id"] = assets.id
            values["type"] = assets.type
            values["property"] = property
            models.insert_or_update(values)
        else:
            LOG.error("append %s not a dict" % data)


    def set_switch(self, switchlist):
        values = {}
        for switch in switchlist:
            values["id"] = switch
            values["type"] = "switch"
            values["property"] = {}
            models.insert_or_update(values)


    def is_same(self, id):
        cache_pillar = self.get_by_cache(id, datatype="pillar")
        db_pillar = dict(models.get_by_id(id).property)["pillar"]
        return cmp(cache_pillar, db_pillar)


    def get_by_cache(self, id, datatype=None):
        cache_file = __opts__["cachedir"] + "/minions/%s/data.p" % str(id)
        cache_file = os.path.normpath(cache_file)
        try:
            f = file(cache_file, "rb")
            data = f.read()
            data = msgpack.loads(data, use_list=True)
            if datatype:
                return data.get(datatype, {})
            return data
        except Exception,e:
            LOG.error("read from cache file error %s" % e)
            return {}


if __name__ == '__main__':
    app = ListenEvent("/var/run/collect.pid")
    app.run()
