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

import musync.printer; # printer module
import musync.dbman as db;
from musync.opts import Settings; # global settings
from musync.errors import WarningException,FatalException; # exceptions
import musync.opts; #options
import musync.op;
import musync.hints;
import musync.formats;

import sys;
import traceback;
#import codecs;      # For utf-8 file support
#set language-specific stuff:
#language, output_encoding = locale.getdefaultlocale()

#global stop variable

import musync.sign;
import musync.locker;

import signal;

def op_add(pl, p):
    """
    Operation to add files to filestructure.
    @param p Path object to file being added.
    """

    printer, logger = pl;
    
    if p.isdir():
        printer.notice("ignoring directory: %s"%(p.path));
        return;
   
    if not p.isfile():
        raise WarningException("not a file: %s"%(p.path));

    # FIXME: remove when done
    #if p.ext not in Settings["supported-ext"]:
    #    raise WarningException("unsupported extension");
    
    meta = musync.formats.open(p.path, **Settings["modify"]);
    
    # this causes nice display of artist/album
    printer.focus(meta);
    
    t = db.build_target(p, meta);
    # FIXME: need transcoding
    #if we are trying to transcode
    if Settings["transcode"]:
        if Settings["pretend"]:
            printer.notice("would transcode: %s"%(p.path));
        (p, t) = db.transcode(p, t);
    
    if musync.locker.islocked(t):
        raise WarningException("locked: %s"%(p.path));

    if Settings["pretend"]:
        printer.notice("would add: %s"%(p.path));
        printer.blanknotice("       as: %s"%(t.relativepath()));
    else:
        printer.action("adding file: %s"%(t.relativepath()));
        db.add(pl, p, t);
    
    if Settings["lock"]:
        op_lock(pl, t);

def op_remove(pl, p):
    """
    Operation to remove files matching in filestructure.
    @param p Path object to file being removed.
    """

    printer, logger = pl;
    
    if p.isdir():
        if not p.inroot():
            raise WarningException("cannot remove directory (not in root): %s"%(p.path));
        
        if not p.isempty():
            raise WarningException("cannot remove directory (not empty): %s"%(p.relativepath()));
        
        if Settings["pretend"]:
            printer.notice("would remove empty dir: %s"%(p.relativepath()));
        else:
            printer.action("removing directory: %s"%(p.relativepath()));
            p.rmdir();
            return;

    # FIXME: remove when done
    #if p.ext not in Settings["supported-ext"]:
    #    raise WarningException("unsupported extension: %s"%(p.path));
    
    if not p.isfile():
        raise WarningException("file not found: %s"%(p.path));
    
    meta = musync.formats.open(p.path, **Settings["modify"]);
    
    # this causes nice display of artist/album
    printer.focus(meta);

    # build target path
    t = db.build_target(p, meta);
    
    if musync.locker.islocked(t):
        raise WarningException("locked: %s"%(t.relativepath()));
    if musync.locker.parentislocked(t):
        raise WarningException("locked: %s (parent)"%(t.relativepath()));

    if not t.isfile():
        raise WarningException("target file not found: %s"%(t.relativepath()));
    
    if Settings["pretend"]:
        printer.notice("would remove: %s"%(p.path));
        printer.blanknotice("          as: %s"%(t.relativepath()));
    else:
        printer.action("removing file: %s"%(t.relativepath()));
        db.remove(p, t);

def op_fix(pl, p):
    """
    Operation to fix files in filestructure.
    Opening fix-log as input file.
    @param p Path object to file being fixed.
    """
    
    printer, logger = pl;
    
    if not p.inroot():
        raise WarningException("can only fix files in 'root'");
    
    if musync.locker.islocked(p):
        raise WarningException("locked: %s"%(p.relativepath()));
    if musync.locker.parentislocked(p):
        raise WarningException("locked: %s (parent)"%(p.relativepath()));

    if not p.exists():
        raise WarningException("path not found: %s"%(p.path));
    
    if p.isfile():
        if p.path == musync.locker.get_lockpath():
            printer.action("ignoring lock-file");
            return;
        
        # try to open, if you cannot, remove the files
        try:
            musync.formats.open(p.path, **Settings["modify"]);
        except Exception, e:
            printer.action("removing (%s): %s"%(p.path, str(e)));
            Settings["rm"](p.path);
            return;
	
    t = None;
    if p.isfile():
        meta = musync.formats.open(p.path, **Settings["modify"]);
        t = db.build_target(p, meta);
    else:
        t = p;

    if Settings["pretend"]:
        printer.notice("would check: %s"%(p.path));
        if t.isfile():
            printer.blanknotice("         as: %s"%(t.relativepath()));
    else:
        if p.isfile():
            db.fix_file(pl, p, t);
        elif p.isdir():
            db.fix_dir(pl, p);
    
    if Settings["lock"]:
        op_lock(pl, t);

def op_lock(pl, p):
    """
    lock a file, making it unavailable to adding, removing and such.
    @param p Path object to file being locked.
    """

    printer, logger = pl;

    if not p.inroot():
        raise WarningException("can only lock files in 'root'");

    if Settings["pretend"]:
        printer.notice("would try to lock: %s"%(p.path));
        return;

    if p.isfile():
        musync.locker.lock(p);
        printer.notice("file has been locked: %s"%(p.path));
    elif p.isdir():
        if not p.inroot():
            raise WarningException("cannot lock directories outside of root");
        musync.locker.lock(p);
        printer.notice("dir has been locked: %s"%(p.path));

def op_unlock(pl, p):
    """
    Unlock a file, making it available to adding, removing and such.
    @param p Path object to file being unlocked.
    """
    
    printer, logger = pl;
    
    if not p.inroot():
        raise WarningException("can only unlock files in 'root'");

    if Settings["pretend"]:
        printer.notice("would try to unlock: %s"%(p.path));
        return;
    
    if p.isfile():
        if musync.locker.islocked(p):
            musync.locker.unlock(p);
            printer.notice("path has been unlocked: %s"%(p.path));
        elif musync.locker.parentislocked(p):
            tp = p.parent();
            raise WarningException("parent is locked: %s"%(tp.path));
        else:
            raise WarningException("path is not locked: %s"%(p.path));
    elif p.isdir():
        musync.locker.unlock(p);
        printer.notice("dir has been unlocked: %s"%(p.path));

def op_name(pl, p):
    """
    give a friendly suggestion of how you would name a specific file.
    """

    printer, logger = pl;

    if p.isfile():
        meta = musync.formats.open(p.path, **Settings["modify"]);
        print "format: ", Settings["format"](meta);
        print "dir:    ", Settings["dir"](meta);
    else:
        raise WarningException("path is not a file");

def main(pl, args):
    printer, logger = pl;
    
    musync.locker.init();
    
    if len(args) < 1:
        raise FatalException("To few arguments");
    
    #try to figure out operation.
    if args[0] in ("rm","remove"):  #remove files from depos

        if Settings["verbose"]:
            if Settings["pretend"]:
                printer.boldnotice("# Pretending to remove files...");
            else:
                printer.boldnotice("# Removing files...");
        
        musync.op.operate(pl, args[1:], op_remove);
    elif args[0] in ("add","sync"): #syncronize files with musicdb

        if Settings["verbose"]:
            if Settings["pretend"]:
                printer.boldnotice("# Pretending to add files...");
            else:
                printer.boldnotice("# Adding files...");
            
        musync.op.operate(pl, args[1:], op_add);
    elif args[0] in ("fix"): #syncronize files with musicdb

        if Settings["verbose"]:
            if Settings["pretend"]:
                printer.boldnotice("# Pretending to fix files...");
            else:
                printer.boldnotice("# Fixing files...");

        # make sure all paths are referenced relative to root.
        musync.op.operate(pl, args[1:], op_fix);
    elif args[0] in ("lock"):

        if Settings["verbose"]:
            if Settings["pretend"]:
                printer.boldnotice("# Pretending to lock files...");
            else:
                printer.boldnotice("# Locking files...");
        
        musync.op.operate(pl, args[1:], op_lock);
    elif args[0] in ("unlock"):

        if Settings["verbose"]:
            if Settings["pretend"]:
                printer.boldnotice("# Pretending to unlock files...");
            else:
                printer.boldnotice("# Unlocking files...");

        musync.op.operate(pl, args[1:], op_unlock);
    elif args[0] in ("name"):
        printer.boldnotice("# Naming files...");
        musync.op.operate(pl, args[1:], op_name);
    else:
        raise FatalException("There is no operation called '%s'"%(args[0]));

    if Settings["verbose"]:
        if Settings["pretend"]:
            printer.boldnotice("# Pretending done!");
        else:
            printer.boldnotice("# Done!");

    musync.locker.stop();
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
    printer = musync.printer.TermCaps(sys.stdout);
    
    # note that this is not the place for WarningExceptions
    args = None; 
        
    try:
        args = musync.opts.read(sys.argv[1:], (printer, None));
    except Exception, e:
        printer.error(str(e));
        if Settings["debug"]:
            print traceback.format_exc();
        sys.exit(1);
        return;
    
    logger = musync.printer.TermCaps(open(Settings["log"], "w"));
    
    try:
        if args is not None: # a nice way to go
            main((printer, logger), args);
    except FatalException, e: # break execution exception.
        printer.error((str(e)));
        if Settings["debug"]:
            print traceback.format_exc();
    except Exception, e: # if this happens, something went really bad.
        printer.error("Fatal Exception - %s"%(str(e)));
        print traceback.format_exc();
        printer.error("Something went very wrong, please report this error at %s"%(musync.opts.REPORT_ADDRESS));
        sys.exit(1);
    except SystemExit, e: # interrupts and such
        sys.exit(e);
    
    if Settings["verbose"] and args is not None:
        printer.boldnotice("handled %d files, %d dirs"%(musync.op.handled_files, musync.op.handled_dirs));
    
    musync.hints.run();
    
    if logger and logger.haslogged:
        print "Wrote to log - check: %(log)s"%{ 'log': Settings["log"] };
    
    # FIXME this might be unsafe 
    sys.exit(musync.sign.ret());
