#-*- coding:utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="logmonitor",
    version="0.1",
    author="coocla",

    install_requires=[
        "MySQL-python",
        "PyYAML",
        "DBUtils",
    ],

    scripts = [
        "bin/log-server",
        "bin/log-client",
    ],

    packages = find_packages(),

    data_files = [
        ("/etc/logmonitor/", ["etc/logmonitor.conf"]),
    ],
)
