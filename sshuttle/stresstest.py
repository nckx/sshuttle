#!/usr/bin/env python

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
import select
import struct
import time

listener = socket.socket()
listener.bind(('127.0.0.1', 0))
listener.listen(500)

servers = []
clients = []
remain = {}

NUMCLIENTS = 50
count = 0


while 1:
    if len(clients) < NUMCLIENTS:
        c = socket.socket()
        c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        c.bind(('0.0.0.0', 0))
        c.connect(listener.getsockname())
        count += 1
        if count >= 16384:
            count = 1
        print('cli CREATING %d' % count)
        b = struct.pack('I', count) + 'x' * count
        remain[c] = count
        print('cli  >> %r' % len(b))
        c.send(b)
        c.shutdown(socket.SHUT_WR)
        clients.append(c)
        r = [listener]
        time.sleep(0.1)
    else:
        r = [listener] + servers + clients
    print('select(%d)' % len(r))
    r, w, x = select.select(r, [], [], 5)
    assert(r)
    for i in r:
        if i == listener:
            s, addr = listener.accept()
            servers.append(s)
        elif i in servers:
            b = i.recv(4096)
            print('srv <<  %r' % len(b))
            if i not in remain:
                assert(len(b) >= 4)
                want = struct.unpack('I', b[:4])[0]
                b = b[4:]
                # i.send('y'*want)
            else:
                want = remain[i]
            if want < len(b):
                print('weird wanted %d bytes, got %d: %r' % (want, len(b), b))
                assert(want >= len(b))
            want -= len(b)
            remain[i] = want
            if not b:  # EOF
                if want:
                    print('weird: eof but wanted %d more' % want)
                    assert(want == 0)
                i.close()
                servers.remove(i)
                del remain[i]
            else:
                print('srv  >> %r' % len(b))
                i.send('y' * len(b))
                if not want:
                    i.shutdown(socket.SHUT_WR)
        elif i in clients:
            b = i.recv(4096)
            print('cli <<  %r' % len(b))
            want = remain[i]
            if want < len(b):
                print('weird wanted %d bytes, got %d: %r' % (want, len(b), b))
                assert(want >= len(b))
            want -= len(b)
            remain[i] = want
            if not b:  # EOF
                if want:
                    print('weird: eof but wanted %d more' % want)
                    assert(want == 0)
                i.close()
                clients.remove(i)
                del remain[i]
listener.accept()
