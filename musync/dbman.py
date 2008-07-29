#
# this is probably the must drugged file in the project
# and this is because it is freaking hard to implement 
# this behaviour nicely.
#
# guidelines for file:
# * put things that performs 'core' functionality in musync,
#   like copying, fixing and such, make sure that all methods are
#   only called once per file (do this in main musync file).
# * don't perform action handling here, this is to be done in
#   the main musync file.
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

import os;
import tempfile;
import musync.subp as sp;
from musync.opts import Settings;
import musync.printer as Printer;
from musync.errors import WarningException, FatalException;

import musync.commons;
# Current artist and album in focus

def build_target(p, cmeta):
    """
    builds a target for many of the functions in musync.dbman
    this is just a complex concatenation of directories and 
    filenames.

    notice! this function resides in this module because we havent
            found a better place yet.

    @param p     Original Path instance which the metadata was
                 extracted from.
    @param cmeta A dict containing the desired meta-name for target.
                 notice that this should have been cleaned with
                 musync.meta.cleanmeta();
    """
    dir = os.path.join(
        Settings["root"],
        Settings["dir"]%{
            'track': cmeta["track"], \
            'title': cmeta["title"], \
            'artist': cmeta["artist"], \
            'album': cmeta["album"], \
            'ext': p.ext
        }
    );

    path = "%s/%s"%( \
        dir, \
        Settings["format"]%{ \
            'track': cmeta["track"], \
            'title': cmeta["title"], \
            'artist': cmeta["artist"], \
            'album': cmeta["album"], \
            'ext': p.ext
        }
    );

    return musync.commons.Path(path);

def hash_compare(path1, path2):
    """
    compares two paths, uses hashing to see if they are equal.
    """
    hash = sp.hash_with(path1);
    hash2 = sp.hash_with(path2);
    return hash == hash2;

def hash_get(path):
    return sp.hash_with(path);

def add(p, t):
    "adds a file to the database"
    if not t.parent().isdir():
        # recursively makes directories.
        try:
            os.makedirs(t.dir)
        except OSError, e:
            raise FatalException(str(e));

    if t.path == p.path:
        raise WarningException("source and target file same");

    if (t.exists() or t.islink()) and not Settings["force"]:
        raise WarningException("file already exists: %s"%(t.relativepath()));

    # by this time, we wan't it removed.
    if (t.exists() or t.islink()):
        sp.rm_with(t.path);

    #FIXED intelligent exists check.
    if not Settings["allow-similar"]:
        for ext in Settings["supported-ext"]:
            d=musync.commons.Path("%s/%s.%s"%(t.dir, t.basename, ext));
            if (d.exists() or d.islink()):
                raise WarningException(
                    "similar file already exists (--allow-similar to ignore): %s"%(
                        d.relativepath()
                    )
                );

    attempts = 0;
    parity = None;
    while True:
        if attempts > 4:
            raise FatalException("      failed to many times! :-O");
        
        if attempts > 0:
            if not p.exists():
                Printer.warning("source file does no longer exist.");
                raise FatalException("cannot perform add operation.");

        if Settings["check-hash"]:
            parity = hash_get(p.path);

        sp.add_with(p.path, t.path);
        
        # if settings prompt, check target file hash.
        if Settings["check-hash"]:
            if hash_get(t.path) == parity:
                Printer.notice( "      check-hash successful :-)" );
            else:
                Printer.warning( "      check-hash failed, retrying :-(" );
                attempts += 1;
                continue;
        break;

    return True;

def remove (p, t):
    "removes a file from the database"
    if t.path == p.path and not Settings["force"]:
        raise WarningException("target is same as source  (use --force if you really wan't to do this)");
   
    sp.rm_with(t.path);
    return True;

import musync.meta;

def fix_file(p, t):
    # this mean we are in the correct place...
    if t.path == p.path:
        Printer.notice("sane - %s"%(t.relativepath()));
        return; # this is sane.

    if not t.isfile() and not t.islink():
        Printer.action("adding insane file - %s"%(p.relativepath()));
        add(p, t);

    Printer.action("removing insane file - %s"%(p.relativepath()));
    sp.rm_with(p.path);

def fix_dir(p):
    if not p.isempty():
        Printer.notice("sane - %s/"%(p.relativepath()));
        return;
    
    Printer.action("removing empty dir - %s"%(p.relativepath()));
    p.rmdir();

#transcoding
def transcode(p, t):
    if p.ext not in Settings["transcode"][0]:
         return (p, t);
    t_from = p.ext;
    t_to = Settings["transcode"][1];
    # this is our new target.
    t = musync.commons.Path("%s/%s.%s"%(t.dir, t.basename, t_to));
    
    # this is the temporary file for the transcode.
    tmp_file = "%s/musync.trans.%s.%s"%(musync.opts.tmp, tempfile.mktemp(), t_to);
    
    if (t.exists() or t.islink()) and not Settings["force"]:
        raise WarningException("file already exists: %s"%(t.relativepath()));

    if not Settings["pretend"]:
        sp.transcode_with(Settings["%s-to-%s"%(t_from, t_to)], p.path, tmp_file);
    # temp-file is the new source.
    p = musync.commons.Path(tmp_file);
    return (p, t);

