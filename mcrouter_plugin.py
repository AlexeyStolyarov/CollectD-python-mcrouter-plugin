#!/usr/bin/python
# -*- coding: utf-8 -*-

import telnetlib

HOST = '10.20.16.28'
PORT = '11211'
TIMEOUT = '3'

tn = telnetlib.Telnet(HOST, PORT, TIMEOUT)
tn.read_until("'^]'.", 5)

tn.write("stats" + "\n")
data = tn.read_until("END", TIMEOUT)
print data

