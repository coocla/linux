#!/usr/bin/env python

from setuptools import setup, find_packages
import salt.config

opts = salt.config.client_config("/etc/salt/master")

runner_dirs = opts.get('runner_dirs', ['/srv/salt/_runner'])
grains_dirs = opts.get('file_roots', {}).get("base", [])
if not runner_dirs:
    runner_dirs = ['/srv/salt/_runner']

if not grains_dirs:
    grains_dirs = ['/srv/salt']

grains_dirs = "/".join([grains_dirs[0], "_grains"])

setup(
    name = "collector",
    version = "0.1",
    description = "grains and pillar into db",
    author = "coocla",
    install_requires = [
        "SQLALchemy",
        "MySQL-python",
        "msgpack-python",
        "PyYAML",
    ],

    scripts = [
        "bin/salt-collect"
    ],

    packages = find_packages(),

    data_files = [
        ('/etc/collector', ['etc/config.ini']),
        (runner_dirs[0], ['bin/refresh.py']),
        (grains_dirs, ['bin/switch.py']),
    ],
)
