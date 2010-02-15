#
# Musync subprocess - A few nifty subprocessing hacks.
#
# Yes, this enables the program to simplify interprocessing.
#
# author: John-John Tedro <pentropia@gmail.com>
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

import os, shutil

import musync.custom as custom

env_base={
  'os': os,
  'shutil': shutil,
  'musync': custom
};

from musync.opts import Settings;
import subprocess as sp;
from musync.errors import WarningException, FatalException;
import musync.printer as Printer;

def filter_with(string, field):
    """
    Wrapper for use with the key 'filter-with'.
    """
    env=dict(env_base);
    env['string'] = string;
    env['field'] = field;
    return eval(Settings["filter-with"], env);

def transcode_with(cmd, source, dest):
    env=dict(env_base);
    env['src'] = source;
    env['dst'] = dest;
    return eval(cmd, env);

def add_with( source_file, destination_file ):
    env=dict(env_base);
    env['src'] = source_file;
    env['dst'] = destination_file;
    return eval(Settings["add-with"], env);

def rm_with(target):
    env=dict(env_base);
    env['target'] = target;
    return eval(Settings["rm-with"], env);

def hash_with(target):
    """
    Uses Hash with.
    """
    env=dict(env_base);
    env['target'] = target;
    return eval(Settings["hash-with"], env).split(' ')[0];

def last_filter(text):
    """
    Do not allow _any_ unicode characters to pass by here.
    """
    d_text = text.decode("utf-8");
    buildstr = list();

    for c in d_text:
        if ord(c) > 127:
            buildstr.append("x{0}".format(ord(c)));
        else:
            buildstr.append(c);
    
    return "".join(buildstr).encode("ascii");

def sanitize_with_filter(text, field):
    """
        remove none-filename-ish characters from strings.
        Check configuration to change this behaviour.
    """
    return last_filter(filter_with(text, field));
