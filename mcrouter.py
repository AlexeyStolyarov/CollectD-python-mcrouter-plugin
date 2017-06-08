#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import select
import socket

try:
    import collectd
except:
    import collectd_tools.collectd_mockup as collectd

# default values
config = {
    'INSTANCE': 'default',
    'HOST': '127.0.0.1',
    'PORT': 11211,
    'TIMEOUT': 200,
    'PLUGIN_NAME': 'mcrouter'
}

RETURNED_VARS = {
    'cmd_set_count': 'derive',
    'cmd_get_count': 'derive',
    'cmd_delete_count': 'derive',
    'duration_us': 'gauge',
    'proxy_reqs_processing': 'gauge',
    'proxy_reqs_waiting': 'gauge',
    'asynclog_requests': 'derive'
    #    'proxy_reqs_processing': 'derive'
}


def _read_socket(arg_host, arg_port=1121):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((arg_host, int(arg_port)))
    client.send("stats\n")

    running = True
    buffer = ""

    while (running):
        r, w, e = select.select([client, ], [], [], config["TIMEOUT"])
        if not (r or w or e):
            raise TimeoutException()
        for s in r:
            if (s is client):
                buffer = buffer + client.recv(16384)
                running = (len(buffer) == 0)

    client.close()
    data = buffer.decode('utf-8').split('\r\n')
    return data

def mcrouter_read(arg_host, arg_port=1121, arg_timeout=1):
    data_tmp = _read_socket(arg_host, arg_port)
    #
    # splitting, primary filtering and convert to dictonary
    #
    data = {}
    for i in data_tmp:
        for line in RETURNED_VARS.keys():
            # if RETURNED_VARS.key matches something like "STAT cmd_delete_count 24972" /.*\scmd_delete_count\s.*/
            if re.match(".*\s%s\s.*" % (line,), i):
                tmp = i.split(' ')
                data[tmp[1]] = (tmp[2], RETURNED_VARS[line])

    return data


def config_callback(arg_config):
    global config
    # if we on the beginning of <Module mcrouter> block
    # recursion for getting child values from module block
    if arg_config.key == 'Module' and arg_config.values[0] == config["PLUGIN_NAME"] and arg_config.parent is None:
        for i in arg_config.children:
            config_callback(i)
        return

    known_keys = ['HOST', 'PORT', 'INSTANCE']
    if arg_config.key not in known_keys:
        raise Exception('Unknown config option: %s' % arg_config.key)

    if config.values:
        config[arg_config.key] = arg_config.values[0]  # arg_config.values is tuple

    collectd.info('config parse: %s => %s;' % (arg_config.key, arg_config.values[0]))

def read_callback():
    data = mcrouter_read(config["HOST"], config["PORT"], config["TIMEOUT"])

    for x in data:
        metric = collectd.Values()
        metric.plugin = config["PLUGIN_NAME"]
        metric.plugin_instance = config["INSTANCE"]
        metric.type = data[x][1]
        metric.type_instance = x
        metric.values = (data[x][0],)
        metric.dispatch()


collectd.register_config(config_callback)
collectd.register_read(read_callback)
