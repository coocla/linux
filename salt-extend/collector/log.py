"""
Log lib
"""
import os
import sys
import yaml
import logging
import logging.handlers

loggers = []

def config_init():
    try:
        f = file("/etc/collector/config.ini", "r")
        return yaml.load(f.read())
    except Exception,e:
        print "Error: %s" % e
        sys.exit(5)

options = config_init()


def getlogroot(name):
    logroot = os.path.basename(name)
    if logroot.endswith('.py'):
        logroot = logroot[:-3]
    elif logroot.endswith('.pyc'):
        logroot = logroot[:-4]
    return logroot


def setup_log(root=__file__, LogDir="logs", LogLevel="INFO"):
    logroot = getlogroot(root)
    if logroot in loggers:
        return
    loggers.append(logroot)

    if not os.path.isdir(LogDir):
        os.mkdir(LogDir)

    logger = logging.getLogger(logroot)
    logfile = os.path.join(LogDir, logroot + '.log')
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes=10240000, backupCount=5)
    formatter = logging.Formatter('%(asctime)19s  [%(name)s] [%(levelname)-8s] %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(getattr(logging, LogLevel))


def getLogger(root=__file__):
    logroot = getlogroot(root)
    if logroot not in loggers:
        logroot = __file__
    return logging.getLogger(logroot)
