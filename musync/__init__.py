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
import musync.dbman as db;
import musync.opts; #options
import musync.op;
import musync.hints;
import musync.formats;
import musync.locker;
import musync.sign;
import musync.errors;

import signal;
import sys;
import traceback;
#import codecs;      # For utf-8 file support
#set language-specific stuff:
#language, output_encoding = locale.getdefaultlocale()

#global stop variable

def op_add(app, p):
    """
    Operation to add files to filestructure.
    @param p Path object to file being added.
    """

    if p.isdir():
        app.printer.notice("ignoring directory:", p.path);
        return;
   
    if not p.isfile():
        app.printer.warning("not a file:", p.path);
        return;
    
    if not p.meta:
        app.printer.warning("could not open metadata:", p.path);
        return;
    
    # this causes nice display of artist/album
    app.printer.focus(p.meta);
    
    t = db.build_target(app, p);
    # FIXME: need transcoding
    #if we are trying to transcode
    if app.settings["transcode"]:
        r = db.transcode(app, p, t);
        
        if not r:
            return;
        
        p, t = r;
    
    if app.locker.islocked(t):
        app.printer.warning("locked:", p.path);
        return

    if app.settings["pretend"]:
        app.printer.notice("would add:", p.path);
        app.printer.blanknotice("       as:", t.relativepath());
    else:
        app.printer.action("adding file:", t.relativepath());
        db.add(app, p, t);
    
    if app.settings["lock"]:
        op_lock(app, t);

def op_remove(app, p):
    """
    Operation to remove files matching in filestructure.
    @param p Path object to file being removed.
    """

    if p.isdir():
        if not p.inroot():
            app.printer.warning("cannot remove directory (not in root):", p.path);
            return
        
        if not p.isempty():
            app.printer.warning("cannot remove directory (not empty):", p.relativepath());
            return;
        
        if app.settings["pretend"]:
            app.printer.notice("would remove empty dir:", p.relativepath());
            return;
        else:
            app.printer.action("removing directory:", p.relativepath());
            p.rmdir();
            return;
        
        return;
    
    elif p.isfile():
        if not p.meta:
            app.printer.warning("could not open metadata:", p.path);
            return;
        
        # this causes nice display of artist/album
        app.printer.focus(p.meta);
        
        # build target path
        t = db.build_target(app, p);
        
        if app.locker.islocked(t):
            app.printer.warning("locked:", t.relativepath());
            return;
        
        if app.locker.parentislocked(t):
            app.printer.warning("locked:", t.relativepath(), "(parent)");
            return;
        
        if not t.isfile():
            app.printer.warning("target file not found:", t.relativepath());
            return;
        
        if app.settings["pretend"]:
            app.printer.notice(     "would remove:", p.path);
            app.printer.blanknotice("          as:", t.relativepath());
        else:
            app.printer.action("removing file:", t.relativepath());
            db.remove(app, p, t);
        
        return;
    
    app.printer.warning("cannot handle file:", p.path);

def op_fix(app, p):
    """
    Operation to fix files in filestructure.
    @param p Path object to file being fixed.
    """
    
    if not p.inroot():
        app.printer.warning("can only fix files in 'root'");
        return;
    
    if app.locker.islocked(p):
        app.printer.warning("locked:", p.relativepath());
        return;
    
    if app.locker.parentislocked(p):
        app.printer.warning("locked:", p.relativepath(), "(parent)");
        return;

    if not p.exists():
        app.printer.warning("path not found:", p.path);
        return;
    
    if p.isfile():
        if p.path == app.locker.get_lockpath():
            app.printer.action("ignoring lock-file");
            return;
        
        # try to open, if you cannot, remove the files
        if not p.meta:
            app.printer.action("removing", p.path);
            app.lambdaenv.rm(p.path);
	  
    t = None;
    if p.isfile():
        if not p.meta:
            app.printer.warning("could not open metadata:", p.path);
            return;

        t = db.build_target(app, p);
    else:
        t = p;

    if app.settings["pretend"]:
        app.printer.notice("would check:", p.path);
        if t.isfile():
            app.printer.blanknotice("         as:", t.relativepath());
    else:
        if p.isfile():
            db.fix_file(app, p, t);
        elif p.isdir():
            db.fix_dir(app, p);
    
    if app.settings["lock"]:
        op_lock(app, t);

def op_lock(app, p):
    """
    lock a file, making it unavailable to adding, removing and such.
    @param p Path object to file being locked.
    """

    if not p.inroot():
        app.printer.warning("can only lock files in 'root'");
        return;

    if app.settings["pretend"]:
        app.printer.notice("would try to lock:", p.path);
        return;
    
    if p.isdir():
        app.locker.lock(p);
        app.printer.notice("dir has been locked:", p.path);
        return;
    elif p.isfile():
        app.locker.lock(p);
        app.printer.notice("file has been locked:", p.path);
        return;
    
    app.printer.warning("cannot handle file:", p.path);

def op_unlock(app, p):
    """
    Unlock a file, making it available to adding, removing and such.
    @param p Path object to file being unlocked.
    """
    
    if not p.inroot():
        app.printer.warning("can only unlock files in 'root'");
        return;

    if app.settings["pretend"]:
        app.printer.notice("would try to unlock:", p.path);
        return;
    
    if p.isfile():
        if app.locker.islocked(p):
            app.locker.unlock(p);
            app.printer.notice("path has been unlocked:", p.path);
        elif app.locker.parentislocked(p):
            tp = p.parent();
            app.printer.warning("parent is locked:", tp.path);
        else:
            app.printer.warning("path is not locked:", p.path);
        return;
    elif p.isdir():
        app.locker.unlock(p);
        app.printer.notice("dir has been unlocked:", p.path);
        return;
    
    app.printer.warning("cannot handle file:", p.path);

def op_inspect(app, p):
    """
    give a friendly suggestion of how you would name a specific file.
    """
    
    if not p.isfile():
        app.printer.warning("not a file:", p.path);
        return;
    
    if not p.meta:
        app.printer.warning("could not open metadata:", p.path);
        return;

    app.printer.boldnotice(p.meta.filename)
    app.printer.blanknotice("artist:    ", repr(p.meta.artist))
    app.printer.blanknotice("album:     ", repr(p.meta.album))
    app.printer.blanknotice("title:     ", repr(p.meta.title))
    app.printer.blanknotice("track:     ", repr(p.meta.track))
    app.printer.blanknotice("year:      ", repr(p.meta.year))
    app.printer.blanknotice("targetpath:", repr(app.lambdaenv.targetpath(p)), "from", repr(app.settings["targetpath"]));

def main(app):
    args = app.args;
    
    if len(args) < 1:
        raise musync.errors.FatalException("To few arguments");
    
    #try to figure out operation.
    if args[0] in ("help"):
        print musync.opts.Usage();
        return 0;
    elif args[0] in ("rm","remove"):  #remove files from depos

        if app.settings["verbose"]:
            if app.settings["pretend"]:
                app.printer.boldnotice("# Pretending to remove files...");
            else:
                app.printer.boldnotice("# Removing files...");
        
        musync.op.operate(app, op_remove);
    elif args[0] in ("add","sync"): #syncronize files with musicdb

        if app.settings["verbose"]:
            if app.settings["pretend"]:
                app.printer.boldnotice("# Pretending to add files...");
            else:
                app.printer.boldnotice("# Adding files...");
            
        musync.op.operate(app, op_add);
    elif args[0] in ("fix"): #syncronize files with musicdb

        if app.settings["verbose"]:
            if app.settings["pretend"]:
                app.printer.boldnotice("# Pretending to fix files...");
            else:
                app.printer.boldnotice("# Fixing files...");

        # make sure all paths are referenced relative to root.
        musync.op.operate(app, op_fix);
    elif args[0] in ("lock"):

        if app.settings["verbose"]:
            if app.settings["pretend"]:
                app.printer.boldnotice("# Pretending to lock files...");
            else:
                app.printer.boldnotice("# Locking files...");
        
        musync.op.operate(app, op_lock);
    elif args[0] in ("unlock"):

        if app.settings["verbose"]:
            if app.settings["pretend"]:
                app.printer.boldnotice("# Pretending to unlock files...");
            else:
                app.printer.boldnotice("# Unlocking files...");
        
        musync.op.operate(app, op_unlock);
    elif args[0] in ("inspect"):
        app.printer.boldnotice("# Inspecting files...");
        musync.op.operate(app, op_inspect);
    else:
        raise musync.errors.FatalException("no such operation: " + args[0]);
    
    if app.settings["verbose"]:
        if app.settings["pretend"]:
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
    app = musync.opts.AppSession(sys.stdout);
    
    try:
        app = musync.opts.read(app, sys.argv[1:]);
    except Exception, e:
        app.printer.error(str(e));
        if app.settings["debug"]:
            print traceback.format_exc();
        sys.exit(1);
        return;
    
    #try:
    #    logger = musync.printer.TermCaps(app, open(app.settings["log"], "w"));
    #except IOError, e:
    #    app.printer.warning("Could not initiate log:", str(e));
    #    logger = app.printer;
    #except OSError, e:
    #    app.printer.warning("Could not initiate log:", str(e));
    #    logger = app.printer;
    
    try:
        if app.args is not None:
            main(app);
    except musync.errors.FatalException, e: # break execution exception.
        app.printer.error((str(e)));
        if app.settings["debug"]:
            print traceback.format_exc();
    except Exception, e: # if this happens, something went really bad.
        app.printer.error("Fatal Exception:", str(e));
        print traceback.format_exc();
        app.printer.error("Something went very wrong, please report this error at:", musync.opts.REPORT_ADDRESS);
        sys.exit(1);
    except SystemExit, e: # interrupts and such
        sys.exit(e);
    
    if app.settings["verbose"] and args is not None:
        app.printer.boldnotice("handled", musync.op.handled_files, "files and", musync.op.handled_dirs, "directories");
    
    musync.hints.run(app);
    
    # FIXME this might be unsafe 
    sys.exit(musync.sign.ret());
