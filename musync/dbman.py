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

import musync.errors;
import musync.commons;
import tempfile;

import os;
# Current artist and album in focus

def build_target(app, source, **kw):
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
    
    return musync.commons.Path(app, os.path.join(app.lambdaenv.root, app.lambdaenv.targetpath(source)), **kw);

def hash_get(app, path):
    return app.lambdaenv.hash(path);

def add(app, p, t):
    "adds a file to the database"

    from md5 import md5

    if not t.parent().isdir():
        # recursively makes directories.
        try:
            os.makedirs(t.dir)
        except OSError, e:
            raise musync.errors.FatalException(str(e));

    if t.path == p.path:
        app.printer.warning("source and target file same");
        return;
    
    if (t.exists() or t.islink()) and not app.lambdaenv.force:
        app.printer.warning("file already exists:", t.relativepath());
        return;
    
    # by this time, we wan't it removed.
    if (t.exists() or t.islink()):
        app.lambdaenv.rm(t);
    
    attempts = 0;
    parity = None;
    while True:
        if attempts > 4:
            raise musync.errors.FatalException("      failed to many times! :-O");
        
        if attempts > 0:
            if not p.exists():
                raise musync.errors.FatalException("cannot perform add operation, source file no longer exists (this is why you should not use an destructive operation like move for adding files)!");
        
        if app.lambdaenv.checkhash:
            parity = hash_get(app, p.path);
        
        app.lambdaenv.add(p.path, t.path);
        
        # if settings prompt, check target file hash.
        if app.lambdaenv.checkhash:
            check = hash_get(app, t.path);
            
            if parity == check:
                app.printer.notice(  "      checkhash successful :-) {0} equals {1}".format(md5(repr(parity)).hexdigest(), md5(repr(check)).hexdigest()) )
            else:
                app.printer.warning( "      checkhash failed :-/ {0} is not {1}".format(repr(parity), repr(check)) )
                attempts += 1;
                continue;
        break;

    return True;

def remove (app, p, t):
    "removes a file from the database"
    
    if t.path == p.path and not app.lambdaenv.force:
        app.printer.warning("target is same as source  (use --force if you really wan't to do this)");
        return;
    
    app.lambdaenv.rm(t);
    return True;
