#
# This module is for reading states of musync and hinting at what the user might wan't to do.
#
# author: John-John Tedro <pentropa@gmail.com>
# version: 2008.1
# Copyright (C) 2007 Albin Stjerna, John-John Tedro
#
#    This file is part of Musync.
#
#    Musync is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Musync is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Musync.  If not, see <http://www.gnu.org/licenses/>.
#

import musync.op;
from musync.opts import Settings;

def print_hint(text):
    print "HINT: %s"%(text);

def run():
    # will never hint if silent
    if Settings["silent"]:
        return;

    if musync.op.handled_files == 0 and musync.op.handled_dirs > 0:
        print_hint("Did you forget to use --recursive (or -R)?");
        return;
