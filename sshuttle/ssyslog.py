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

import sys
import os
import subprocess as ssubprocess


_p = None


def start_syslog():
    global _p
    _p = ssubprocess.Popen(['logger',
                            '-p', 'daemon.notice',
                            '-t', 'sshuttle'], stdin=ssubprocess.PIPE)


def stderr_to_syslog():
    sys.stdout.flush()
    sys.stderr.flush()
    os.dup2(_p.stdin.fileno(), 2)
