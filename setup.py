#!/usr/bin/env python
"""Cloudkick Agent Plugin for supervisord.

Installs supervisord_status into plugins directory.

Help: https://github.com/ampledata/cloudkick_supervisord
"""
__author__ = 'Greg Albrecht <gba@splunk.com>'
__copyright__ = 'Copyright 2012 Splunk, Inc.'
__license__ = 'Apache License 2.0'


import os
import setuptools
import shutil


def read_readme():
    """Reads in README file for use in setuptools."""
    with open('README') as rmf:
        return rmf.read()


def create_plugin():
    """Copies setuptools-created script to Cloudkick Agent Plugin directory."""
    script_path = '/usr/local/bin/supervisord_status'
    plugin_path = '/usr/lib/cloudkick-agent/plugins/'
    if os.path.exists(script_path) and os.path.exists(plugin_path):
        print "Copying %s to %s" % (script_path, plugin_path)
        shutil.copy2(script_path, plugin_path)


setuptools.setup(
    name='cloudkick_supervisord',
    version='1.0.0',
    description='Cloudkick Agent Plugin for supervisord.',
    long_description=read_readme(),
    author='Greg Albrecht',
    author_email='gba@splunk.com',
    url='https://github.com/ampledata/cloudkick-supervisord',
    license='Apache License 2.0',
    py_modules=['status'],
    install_requires=['argparse'],
    entry_points={
        'console_scripts': ['supervisord_status = status:main']
    }
)


create_plugin()
