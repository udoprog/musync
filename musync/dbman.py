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

#
# Filesystem based Database Manager.
#
#

import os;

from musync.errors import WarningException, FatalException;
from musync.opts import Settings, SettingsObject;

import musync.commons;
# Current artist and album in focus

def build_target(p, meta):
    """
    builds a target for many of the functions in musync.dbman
    this is just a complex concatenation of directories and 
    filenames.

    notice! this function resides in this module because we havent
            found a better place yet.

    @param p     Original Path instance which the metadata was
                 extracted from.
    @param meta A dict containing the desired meta-name for target.
                 notice that this should have been cleaned with
                 musync.meta.cleanmeta();
    """
    
    return musync.commons.Path(os.path.join(Settings["root"], SettingsObject.targetpath(meta)));

def hash_compare(path1, path2):
    """
    compares two paths, uses hashing to see if they are equal.
    """
    hash = SettingsObject.hash(path1);
    hash2 = SettingsObject.hash(path2);
    return hash == hash2;

def hash_get(path):
    return SettingsObject.hash(path);

def add(pl, p, t):
    "adds a file to the database"

    printer, logger = pl;
    
    if not t.parent().isdir():
        # recursively makes directories.
        try:
            os.makedirs(t.dir)
        except OSError, e:
            raise FatalException(str(e));

    if t.path == p.path:
        printer.warning("source and target file same");
        return;
    
    if (t.exists() or t.islink()) and not Settings["force"]:
        printer.warning("file already exists:", t.relativepath());
        return;
    
    # by this time, we wan't it removed.
    if (t.exists() or t.islink()):
        SettingsObject.rm(t.path);
    
    attempts = 0;
    parity = None;
    while True:
        if attempts > 4:
            raise FatalException("      failed to many times! :-O");
        
        if attempts > 0:
            if not p.exists():
                raise FatalException("cannot perform add operation, source file does no longer exist!");

        if Settings["check-hash"]:
            parity = hash_get(p.path);
        
        SettingsObject.add(p.path, t.path);
        
        # if settings prompt, check target file hash.
        if Settings["check-hash"]:
            check = hash_get(t.path);
            
            
            if parity == check:
                printer.notice(  "      check-hash successful :-) {0} equals {1}".format(repr(parity), repr(check)) )
            else:
                printer.warning( "      check-hash failed :-/ {0} is not {1}".format(repr(parity), repr(check)) )
                attempts += 1;
                continue;
        break;

    return True;

def remove (pl, p, t):
    "removes a file from the database"
    
    printer, logger = pl;
    
    if t.path == p.path and not Settings["force"]:
        printer.warning("target is same as source  (use --force if you really wan't to do this)");
        return;
    
    SettingsObject.rm(t.path);
    return True;

def fix_file(pl, p, t):
    # this mean we are in the correct place...
    printer, logger = pl;
    
    if t.path == p.path:
        printer.notice("sane - %s"%(t.relativepath()));
        return; # this is sane.

    if not t.isfile() and not t.islink():
        printer.action("adding insane file - %s"%(p.relativepath()));
        printer.action("                as - %s"%(t.relativepath()));
        add(pl, p, t);
    
    printer.action("removing insane file - %s"%(p.relativepath()));
    SettingsObject.rm(p.path);

def fix_dir(pl, p):
    printer, logger = pl;
    
    if not p.isempty():
        printer.notice("sane - %s"%(p.relativepath()));
        return;
    
    printer.action("removing empty dir - %s"%(p.relativepath()));
    p.rmdir();

#transcoding
def transcode(pl, p, t):
    printer, logger = pl;
    
    if p.ext not in Settings["transcode"][0]:
         return (p, t);
    
    t_from = p.ext;
    t_to = Settings["transcode"][1];
    # this is our new target.
    t = musync.commons.Path("%s/%s.%s"%(t.dir, t.basename, t_to));
    
    # this is the temporary file for the transcode.
    tmp_file = "%s/musync.trans.%s.%s"%(musync.opts.tmp, os.getpid(), t_to);
    
    if (t.exists() or t.islink()) and not Settings["force"]:
        printer.warning("file already exists:", t.relativepath());
        return;
    
    if Settings["pretend"]:
        printer.action("would have transcoded", t_from, "to", to_to);
    else:
        Settings[t_from + "-to-" + t_to](p.path, tmp_file);
    
    # temp-file is the new source.
    p = musync.commons.Path(tmp_file);
    return (p, t);

