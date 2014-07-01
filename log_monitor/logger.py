import os
import sys
import yaml
import logging
import logging.handlers

loggers = []
config = os.path.normpath(os.getcwd() + "/etc/config.ini")

def load_setup():
    try:
        f = file(config, "r")
        return yaml.load(f.read())
    except Exception,e:
        print "Error: config file format error."
        sys.exit(5)

__opts__ = load_setup()

def getlogroot(name):
    logroot = os.path.basename(name)
    if logroot.endswith('.py'):
        logroot = logroot[:-3]
    elif logroot.endswith('.pyc'):
        logroot = logroot[:-4]
    return logroot


def setup_log(root=__file__, log_dir=__opts__["log_dir"]):
    logroot = getlogroot(root)
    if logroot in loggers:
        return
    loggers.append(logroot)

    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    logger = logging.getLogger(logroot)
    logfile = os.path.join(log_dir, logroot + '.log')
    hdlr = logging.handlers.RotatingFileHandler(logfile, maxBytes=10240000, backupCount=5)
    formatter = logging.Formatter('%(asctime)19s  [%(name)s] [%(levelname)-8s] %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(getattr(logging,__opts__["log_level"]))


def getLogger(root=__file__):
    logroot = getlogroot(root)
    if logroot not in loggers:
        logroot = __file__
    return logging.getLogger(logroot)
