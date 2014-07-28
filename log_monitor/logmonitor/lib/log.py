import os
import sys
import yaml
import logging
from logging.handlers import RotatingFileHandler
from logmonitor.lib import utils

_loggers = {}
options = utils.get_options()

def get_logfile(name):
    if name:
        name = name.split(".")[-1]
        logdir = options["log_dir"]
        return '%s.log' % os.path.join(logdir, name)

def create_logger(name):
    root = logging.getLogger()
    logfile = get_logfile(name)
    loop_handler = RotatingFileHandler(logfile, maxBytes=300*1024*1024, backupCount=5)
    loop_handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)8s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"))
    root.addHandler(loop_handler)

    logger = logging.getLogger("")
    if options["debug"]:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


def getLogger(name):
    if name not in _loggers:
        _loggers[name] = create_logger(name)
    return logging.getLogger(name)
