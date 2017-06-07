#!/usr/bin/python
# -*- coding: utf-8 -*-

import telnetlib

try:
    import collectd
except:
    import collectd_tools.collectd_mockup as collectd

HOST = '10.20.16.27'
PORT = 11211
TIMEOUT = 1

PLUGIN_NAME = 'mcrouter_plugin'

RETURNED_VARS = (
    'destination_batches_sum',
    'proxy_reqs_processing'
)


def mcrouter_read(arg_host, arg_port=1121, arg_timeout=1):
    tn = telnetlib.Telnet(arg_host, arg_port, arg_timeout)
    tn.read_until("'^]'.", 5)

    tn.write("stats" + "\n")
    data_tmp = tn.read_until("END", TIMEOUT)

    #
    # splitting, primary filtering and convert to dictonary
    #
    data = {}
    for i in data_tmp.splitlines():
        for line in RETURNED_VARS:
            if line in i:
                tmp = i.split(' ')
                data[tmp[1]] = tmp[2]

    return data


def read_callback(data=None):
    data = mcrouter_read(HOST, PORT, TIMEOUT)
    for x in data:
        metric = collectd.Values()
        metric.plugin = PLUGIN_NAME
        metric.plugin_instance = ''
        metric.type = x
        metric.type_instance = 1
        metric.values = (data[x],)
        metric.dispatch()


collectd.register_read(read_callback)
