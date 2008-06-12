#
# Musync - Signal handling.
# this is a workaround version of Portage Emerge's signal handler.
#
# author: John-John Tedro
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
import signal

EXCEPTION = 2
INTERRUPT = 10

# This is used as a flag when interrupt is performed.
Interrupt = False;
# this is what is to be returned on an interrupt or failure.
Ret = INTERRUPT;

def ret():
    global Ret;
    return Ret;
def setret(ret):
    global Ret;
    Ret = ret;
