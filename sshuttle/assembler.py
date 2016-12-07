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
import zlib
import imp

z = zlib.decompressobj()
while 1:
    name = stdin.readline().strip()
    if name:
        name = name.decode("ASCII")

        nbytes = int(stdin.readline())
        if verbosity >= 2:
            sys.stderr.write('server: assembling %r (%d bytes)\n'
                             % (name, nbytes))
        content = z.decompress(stdin.read(nbytes))

        module = imp.new_module(name)
        parent, _, parent_name = name.rpartition(".")
        if parent != "":
            setattr(sys.modules[parent], parent_name, module)

        code = compile(content, name, "exec")
        exec(code, module.__dict__)
        sys.modules[name] = module
    else:
        break

sys.stderr.flush()
sys.stdout.flush()

import sshuttle.helpers
sshuttle.helpers.verbose = verbosity

import sshuttle.cmdline_options as options
from sshuttle.server import main
main(options.latency_control)
