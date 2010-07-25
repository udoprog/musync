#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# musync, a minimalistic set of scripts for syncronization of music
# Copyright (C) 2007 Albin Stjerna, John-John Tedro
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

"""
Basic Classes

printer - handles everything that needs to be printed.
"""

import musync.printer; # app.printer module
import musync.db as db;
import musync.opts
import musync.op
import musync.hints
import musync.formats
import musync.locker
import musync.sign
import musync.errors

import signal;
import sys;
import traceback;
#import codecs;      # For utf-8 file support
#set language-specific stuff:
#language, output_encoding = locale.getdefaultlocale()

#global stop variable

def op_add(app, source):
    """
    Operation to add files to filestructure.
    @param source Path object to file being added.
    """

    if source.isdir():
        app.printer.notice("ignoring directory:", source.path);
        return;
   
    if not source.isfile():
        app.printer.warning("not a file:", source.path);
        return;
    
    if not source.meta:
        app.printer.warning("could not open metadata:", source.path);
        return;
    
    # this causes nice display of artist/album
    app.printer.focus(source.meta);
    
    target = db.build_target(app, source);
    
    if app.locker.islocked(target):
        app.printer.warning("locked:", source.path);
        return

    if app.lambdaenv.pretend:
        app.printer.notice("would add:", source.path);
        app.printer.blanknotice("       as:", target.relativepath());
    else:
        app.printer.action("adding file:", target.relativepath());
        db.add(app, source, target);
    
    if app.lambdaenv.lock:
        op_lock(app, target);

def op_remove(app, source):
    """
    Operation to remove files matching in filestructure.
    @param source Path object to file being removed.
    """

    if source.isdir():
        if not source.inroot():
            app.printer.warning("cannot remove directory (not in root):", source.path);
            return
        
        if not source.isempty():
            app.printer.warning("cannot remove directory (not empty):", source.relativepath());
            return;
        
        if app.lambdaenv.pretend:
            app.printer.notice("would remove empty dir:", source.relativepath());
            return;
        else:
            app.printer.action("removing directory:", source.relativepath());
            source.rmdir();
            return;
        
        return;
    
    elif source.isfile():
        if not source.meta:
            app.printer.warning("could not open metadata:", source.path);
            return;
        
        # this causes nice display of artist/album
        app.printer.focus(source.meta);
        
        # build target path
        target = db.build_target(app, source);
        
        if app.locker.islocked(target):
            app.printer.warning("locked:", target.relativepath());
            return;
        
        if app.locker.parentislocked(target):
            app.printer.warning("locked:", target.relativepath(), "(parent)");
            return;
        
        if not target.isfile():
            app.printer.warning("target file not found:", target.relativepath());
            return;
        
        if app.lambdaenv.pretend:
            app.printer.notice(     "would remove:", source.path);
            app.printer.blanknotice("          as:", target.relativepath());
        else:
            app.printer.action("removing file:", target.relativepath());
            db.remove(app, source, target);
        
        return;
    
    app.printer.warning("cannot handle file:", source.path);

def op_fix(app, source):
    """
    Operation to fix files in filestructure.
    @param source Path object to file being fixed.
    """
    
    if not source.inroot():
        app.printer.warning("can only fix files in 'root'");
        return;
    
    if app.locker.islocked(source):
        app.printer.warning("locked:", source.relativepath());
        return;
    
    if app.locker.parentislocked(source):
        app.printer.warning("locked:", source.relativepath(), "(parent)");
        return;

    if not source.exists():
        app.printer.warning("path not found:", source.path);
        return;
    
    if source.isfile():
        if source.path == app.lambdaenv.lockdb():
            app.printer.action("ignoring lock-file");
            return;
        
        # try to open, if you cannot, remove the files
        if not source.meta:
            app.printer.action("removing", source.path);
            app.lambdaenv.rm(source.path);
	  
    target = None;
    
    if source.isfile():
        if not source.meta:
            app.printer.warning("could not open metadata:", source.path);
            return;

        # print nice focusing here aswell
        app.printer.focus(source.meta);
        
        target = db.build_target(app, source);
    else:
        target = source;
    
    def fix_file(app, s, t):
        if t.path == s.path:
            app.printer.notice("sane - " + t.relativepath());
            return;
        
        if not t.isfile() and not t.islink():
            if app.lambdaenv.pretend:
                app.printer.action("would add insane file - " + s.relativepath());
                app.printer.action("                   as - " + t.relativepath());
            else:
                app.printer.action("adding insane file - " + s.relativepath());
                app.printer.action("                as - " + t.relativepath());
                db.add(app, s, t);
                
                if s.isfile():
                    app.printer.action("removing insane file - " + s.relativepath());
                    app.lambdaenv.rm(s);
    
    def fix_dir(app, s):
        if s.isempty():
            if app.lambdaenv.pretend: 
                app.printer.action("would remove empty dir - " + s.relativepath());
            else:
                app.printer.action("removing empty dir - " + s.relativepath());
                s.rmdir();
            
            if app.lambdaenv.lock:
                op_lock(app, target);
        else:
            app.printer.notice("sane - " + s.relativepath());
    
    if source.isfile():   fix_file(app, source, target);
    elif source.isdir():  fix_dir(app, source);

def op_lock(app, source):
    """
    lock a file, making it unavailable to adding, removing and such.
    @param source Path object to file being locked.
    """

    if not source.inroot():
        app.printer.warning("can only lock files in 'root'");
        return;

    if app.lambdaenv.pretend:
        app.printer.action("would try to lock:", source.path);
        return;
    
    if source.isdir():
        app.locker.lock(source);
        app.printer.notice("dir has been locked:", source.path);
        return;
    elif source.isfile():
        app.locker.lock(source);
        app.printer.notice("file has been locked:", source.path);
        return;
    
    app.printer.warning("cannot handle file:", source.path);

def op_unlock(app, source):
    """
    Unlock a file, making it available to adding, removing and such.
    @param source Path object to file being unlocked.
    """
    
    if not source.inroot():
        app.printer.warning("can only unlock files in 'root'");
        return;

    if app.lambdaenv.pretend:
        app.printer.action("would try to unlock:", source.path);
        return;
    
    if source.isfile():
        if app.locker.islocked(source):
            app.locker.unlock(source);
            app.printer.notice("path has been unlocked:", source.path);
        elif app.locker.parentislocked(source):
            tp = source.parent();
            app.printer.warning("parent is locked:", tp.path);
        else:
            app.printer.warning("path is not locked:", source.path);
        return;
    elif source.isdir():
        app.locker.unlock(source);
        app.printer.notice("dir has been unlocked:", source.path);
        return;
    
    app.printer.warning("cannot handle file:", source.path);

def op_inspect(app, source):
    """
    give a friendly suggestion of how you would name a specific file.
    """
    
    if not source.isfile():
        app.printer.warning("not a file:", source.path);
        return;
    
    if not source.meta:
        app.printer.warning("could not open metadata:", source.path);
        return;

    app.printer.boldnotice(source.meta.filename)
    app.printer.blanknotice("artist:    ", repr(source.meta.artist))
    app.printer.blanknotice("album:     ", repr(source.meta.album))
    app.printer.blanknotice("title:     ", repr(source.meta.title))
    app.printer.blanknotice("track:     ", repr(source.meta.track))
    app.printer.blanknotice("year:      ", repr(source.meta.year))
    app.printer.blanknotice("targetpath:", repr(app.lambdaenv.targetpath(source)), "from", app.settings.targetpath);

def op_check(app, source):
    if source.isdir():
        if source.isempty():
            app.printer.notice("empty directory: " + source.relativepath());
    elif source.isfile():
        if not source.meta:
            app.printer.warning("could not open metadata:", source.path);
            return;

        target = db.build_target(app, source);

        if source.path != target.path:
            app.printer.notice("source != target: " + source.relativepath());

def main(app):
    if len(app.args) < 1:
        raise musync.errors.FatalException("To few arguments");
    
    #try to figure out operation.
    if app.args[0] in ("help"):
        print musync.opts.Usage();
        return 0;
    
    elif app.args[0] in ("rm","remove"):  #remove files from depos

        if app.lambdaenv.verbose:
            if app.lambdaenv.pretend:
                app.printer.boldnotice("# Pretending to remove files...");
            else:
                app.printer.boldnotice("# Removing files...");
        
        musync.op.operate(app, op_remove);
    elif app.args[0] in ("add","sync"): #syncronize files with musicdb

        if app.lambdaenv.verbose:
            if app.lambdaenv.pretend:
                app.printer.boldnotice("# Pretending to add files...");
            else:
                app.printer.boldnotice("# Adding files...");
            
        musync.op.operate(app, op_add);
    elif app.args[0] in ("fix"): #syncronize files with musicdb

        if app.lambdaenv.verbose:
            if app.lambdaenv.pretend:
                app.printer.boldnotice("# Pretending to fix files...");
            else:
                app.printer.boldnotice("# Fixing files...");

        # make sure all paths are referenced relative to root.
        musync.op.operate(app, op_fix);
    elif app.args[0] in ("lock"):

        if app.lambdaenv.verbose:
            if app.lambdaenv.pretend:
                app.printer.boldnotice("# Pretending to lock files...");
            else:
                app.printer.boldnotice("# Locking files...");
        
        musync.op.operate(app, op_lock);
    elif app.args[0] in ("unlock"):

        if app.lambdaenv.verbose:
            if app.lambdaenv.pretend:
                app.printer.boldnotice("# Pretending to unlock files...");
            else:
                app.printer.boldnotice("# Unlocking files...");
        
        musync.op.operate(app, op_unlock);
    elif app.args[0] in ("inspect"):
        app.printer.boldnotice("# Inspecting files...");
        musync.op.operate(app, op_inspect);
    elif app.args[0] in ("check"):
        app.printer.boldnotice("# Checking path...");
        app.lambdaenv.recursive = True;
        musync.op.operate(app, op_check, inroot=True);
    else:
        raise Exception("no such operation: " + app.args[0]);
    
    if app.lambdaenv.verbose:
        if app.lambdaenv.pretend:
            app.printer.boldnotice("# Pretending done!");
        else:
            app.printer.boldnotice("# Done!");
    
    app.locker.stop();
    return 0;

# assign different signal handlers.
try:
    def exithandler(signum,frame):
        signal.signal(signal.SIGINT, signal.SIG_IGN);
        signal.signal(signal.SIGTERM, signal.SIG_IGN);
        musync.sign.Interrupt = True;

    signal.signal(signal.SIGINT, exithandler);
    signal.signal(signal.SIGTERM, exithandler);
#   signal.signal(signal.SIGPIPE, signal.SIG_IGN); removed to suite windows?
except KeyboardInterrupt:
    sys.exit(1);

# This block ensures that ^C interrupts are handled quietly.
def entrypoint():
    try:
        app = musync.opts.AppSession(sys.argv[1:], sys.stdout);
    except Exception, e:
        print traceback.format_exc();
        sys.exit(1);
        return;

    if not app.configured:
        sys.exit(1);
    
    try:
        main(app);
    except Exception as e:
        app.printer.error("Fatal Exception:", str(e));
        if app.lambdaenv.debug:
            print traceback.format_exc();
        sys.exit(1);
    except SystemExit as e: # interrupts and such
        sys.exit(e);
    
    if app.lambdaenv.verbose:
        app.printer.boldnotice("handled", musync.op.handled_files, "files and", musync.op.handled_dirs, "directories");
    
    #musync.hints.run(app);
    
    # FIXME this might be unsafe 
    sys.exit(musync.sign.ret());
