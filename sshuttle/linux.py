# This file is part of sshuttle, a transparent SSH proxy/VPN.
# Copyright (C) 2016 the sshuttle authors
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free
# Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import socket
import subprocess as ssubprocess
from sshuttle.helpers import log, debug1, Fatal, family_to_string


def nonfatal(func, *args):
    try:
        func(*args)
    except Fatal as e:
        log('error: %s\n' % e)


def ipt_chain_exists(family, table, name):
    if family == socket.AF_INET6:
        cmd = 'ip6tables'
    elif family == socket.AF_INET:
        cmd = 'iptables'
    else:
        raise Exception('Unsupported family "%s"' % family_to_string(family))
    argv = [cmd, '-t', table, '-nL']
    p = ssubprocess.Popen(argv, stdout=ssubprocess.PIPE)
    for line in p.stdout:
        if line.startswith(b'Chain %s ' % name.encode("ASCII")):
            return True
    rv = p.wait()
    if rv:
        raise Fatal('%r returned %d' % (argv, rv))


def ipt(family, table, *args):
    if family == socket.AF_INET6:
        argv = ['ip6tables', '-t', table] + list(args)
    elif family == socket.AF_INET:
        argv = ['iptables', '-t', table] + list(args)
    else:
        raise Exception('Unsupported family "%s"' % family_to_string(family))
    debug1('>> %s\n' % ' '.join(argv))
    rv = ssubprocess.call(argv)
    if rv:
        raise Fatal('%r returned %d' % (argv, rv))


_no_ttl_module = False


def ipt_ttl(family, *args):
    global _no_ttl_module
    if not _no_ttl_module:
        # we avoid infinite loops by generating server-side connections
        # with ttl 42.  This makes the client side not recapture those
        # connections, in case client == server.
        try:
            argsplus = list(args) + ['-m', 'ttl', '!', '--ttl', '42']
            ipt(family, *argsplus)
        except Fatal:
            ipt(family, *args)
            # we only get here if the non-ttl attempt succeeds
            log('sshuttle: warning: your iptables is missing '
                'the ttl module.\n')
            _no_ttl_module = True
    else:
        ipt(family, *args)
