#!/usr/bin/env python
"""Cloudkick Agent Plugin to monitor supervisord managed processes.

Also logs process status to syslog.

Usage:
  $ supervisord_status process
  status ok process=xxx message={'z': 'yyy'}  # Help: ...
"""
__author__ = 'Greg Albrecht <gba@splunk.com>'
__copyright__ = 'Copyright 2012 Splunk, Inc.'
__license__ = 'Apache License 2.0'
__help__ = 'https://github.com/ampledata/cloudkick-supervisord'


import argparse
import ConfigParser
import logging
import logging.handlers
import os
import socket
import xmlrpclib


def create_logger(lformat=None, lprefix=None, lfacility=None):
    """Sets up logging."""
    if lformat is None:
        lformat = '%(message)s  # Help: %(help)s'
    if lprefix is None:
        lprefix = 'supervisord_status: '
    if lfacility is None:
        lfacility = 'local5'

    if os.path.exists('/dev/log'):
        log_dest = '/dev/log'  # Log Locally
    else:
        log_dest = ('localhost', 514)

    base_logger = logging.getLogger('ck')
    base_logger.setLevel(logging.DEBUG)

    console_logger_formatter = logging.Formatter(lformat)
    console_logger = logging.StreamHandler()
    console_logger.setFormatter(console_logger_formatter)

    syslog_logger_formatter = logging.Formatter(lprefix + lformat)
    syslog_logger = logging.handlers.SysLogHandler(log_dest, lfacility)
    syslog_logger.setFormatter(syslog_logger_formatter)

    base_logger.addHandler(console_logger)
    base_logger.addHandler(syslog_logger)
    return logging.LoggerAdapter(base_logger, {'help': __help__})


def get_supervisord_status(rpc_server, rpc_port, process_name):
    """Gets process statename from supervisord.

    Example Usage & Test
    ====================
    ::

        >>> server = 'localhost'
        >>> port = '9001'
        >>> process = 'sutd'
        >>> status, msg = get_supervisord_status(server, port, process)
        >>> status
        ok

    Parameters
    ==========
    @rpc_server: supervisord RPC Server Name.
    @rpc_port: supervisord RPC Server Port.
    @param process_name: Process name as known by supervisord.
    @type rpc_server: str
    @type rpc_port: str
    @type process_name: str

    @return: Process status in Cloudkick style: 'ok' or 'err'.
    @rtype: str
    """
    proc_exception = ''
    proc_info = {}
    proc_status = 'err'

    rpc_url = ':'.join(['http', '//%s' % rpc_server, rpc_port])

    supervisord = xmlrpclib.Server(rpc_url)
    try:
        proc_info = supervisord.supervisor.getProcessInfo(process_name)
    except xmlrpclib.Fault, ex:
        proc_exception = ex
    except socket.error, ex:
        proc_exception = ex

    if proc_info.get('statename') == 'RUNNING':
        proc_status = 'ok'
    elif proc_exception:
        proc_info['exception'] = '%s' % proc_exception

    return (proc_status, proc_info)


def parse_conf():
    """Parse command-line and config file options.

    Derived from http://bit.ly/KTz7Z3
    """
    default_conf = {'server': 'localhost', 'port': '9001'}

    conf_parser = argparse.ArgumentParser(add_help=False)
    conf_parser.add_argument(
        '-c', '--conf_file',
        help='Specify config file.',
        metavar='FILE',
        default='/etc/supervisord_status.conf')
    args, remaining_argv = conf_parser.parse_known_args()

    if args.conf_file and os.path.exists(args.conf_file):
        config = ConfigParser.SafeConfigParser()
        config.read([args.conf_file])
        default_conf = dict(config.items('conf'))

    # Don't surpress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser],
        # print script description with -h/--help
        description=__doc__,
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.set_defaults(**default_conf)
    parser.add_argument('--server', help='supervisord RPC Server Name.')
    parser.add_argument('--port', help='supervisord RPC Server Port.')
    parser.add_argument('process', nargs='*')
    args = parser.parse_args(remaining_argv)
    return args


def main():
    """Processes arguments and prints status."""
    status = 'err'
    message = {'help': 'supervisord_status -h'}
    process_name = ''

    args = parse_conf()
    rpc_server = args.server
    rpc_port = args.port

    if args.process:
        process_name = args.process[-1]

    logger = create_logger()

    if process_name:
        status, message = get_supervisord_status(
            rpc_server=rpc_server,
            rpc_port=rpc_port,
            process_name=process_name)

    message['server'] = rpc_server
    message['port'] = rpc_port

    logger.debug(
        "status %s process=%s message=%s" % (status, process_name, message))
