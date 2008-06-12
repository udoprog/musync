#
# This modules single purpose is to handle the core operation of musync when either
# reding the files from stdin, or reading trailing arguments.
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

from musync.errors import FatalException, WarningException;
import musync.printer as Printer;
from musync.opts import Settings;
import musync.opts;
import musync.commons;
import sys;

import traceback;
import musync.sign;

# keep track of how many directories and files we are handling.
handled_dirs = 0;
handled_files = 0;

import cStringIO;

def operate_progress_mode(args, call, inroot=False):
    """
    Redirects stdout to log-file.
    FIXME: this should have the possibility to be faster than normal output.
    FIXME: this is not working with new termcap.
    """
    Printer.boldnotice("Output redirected to log");
    Printer.log("===Progress Output===\n"); 

    null_log = Printer.f_log;
    stdout = sys.stdout;
    sys.stdout = null_log;
    Printer.init(); # reinitiate printer.
    #prev_suppressed = Settings["suppressed"];
    #prev_silent = Settings["silent"];
    # suppress the stuff interrupting this bar.
    #Settings["suppressed"] = "notice,action";
    #Settings["silent"] = True;
    
    list=[];
    for p in readargs(args, inroot):
        list.append(p);

    l = len(list) - 1;
    cll = 0;
    line = "";
    #cl = 0;
    for i,p in enumerate(list):
        if musync.sign.Interrupt is True:
            stdout.write("\n");
            sys.stdout = stdout;
            musync.sign.setret(musync.sign.INTERRUPT);
            raise FatalException("Caught Interrupt");

        try:
            #musync.opts.tmp_set("coloring", False);
            call(p);
            #musync.opts.tmp_revert("coloring");
        except WarningException,e: # WarningExceptions are just pritned, then move of to next file.
            #musync.opts.tmp_revert("coloring"); # make sure configuration is correct.
            stdout.write("\r" + (" "*cll));
            stdout.write("\r");
            sys.stdout = stdout;
            Printer.warning(str( e ));
            stdout.flush();
            sys.stdout = null_log;

        # first latest printed line.

        # line to print
        pr = "\r%d/%d"%(i, l);
        # count line
        
        cll = len(pr) - 1;
        stdout.write(pr);
        stdout.flush();
    stdout.write("\n");

    #Settings["suppressed"] = prev_suppressed;
    #Settings["silent"] = prev_silent;
    sys.stdout = stdout;
    null_log.close();

    Printer.init();

def operate(args, call, inroot=False):
    """
    Operation abstraction, this is the only function used by different operations.
    """
    if Settings["progress"]: ## run with progress.
        list=[];
        for p in readargs(args, inroot):
            list.append(p);
       
        Printer.stdout_log();
        l=len(list);
        Printer.write("\n", stream=sys.stdout);
        for i,p in enumerate(list):
            if musync.sign.Interrupt is True:
                Printer.stdout_normal();
                musync.sign.setret(musync.sign.INTERRUPT);
                raise FatalException("Caught Interrupt");
            try:
                if i + 1 == l:
                    d=100;
                else:
                    d=int((i*100)/l);
                r=100-d;
                Printer.write("%(cr)s%(cuu1)s%(el)s[" + "="*d + " "*r + "] " + str(d) + "%%\n", stream=sys.stdout);
                call(p);
            except WarningException,e: # WarningExceptions are just pritned, then move of to next file.
                pass;
                #Printer.warning( str( e ) );
    #    #operate_progress_mode(args, call, inroot=inroot);
    #    return;
        Printer.stdout_normal();
    
    else:
        for p in readargs(args, inroot):
            if musync.sign.Interrupt is True:
                musync.sign.setret(musync.sign.INTERRUPT);
                raise FatalException("Caught Interrupt");
            try:
                call(p);
            except WarningException,e: # WarningExceptions are just pritned, then move of to next file.
                Printer.warning( str( e ) );

def readargs(args, inroot):
    """
    reads paths in different ways depending on number of arguments.
    yields the filepaths for easy access.
    """
    if len(args) <= 0:
        try:
            file = sys.stdin.readline()[:-1];
        except Exception, e:
            raise FatalException(str(e));

        while file:
            for p in readpaths(file, inroot):
                yield p;

            file = sys.stdin.readline()[:-1];
    else:
        while len( args ) > 0:
            for p in readpaths(args[0], inroot):
                yield p;

            args = args[1:];

    return;

def readpaths(path, inroot):
    global handled_dirs, handled_files;
    if inroot:
        path = Settings["root"] + "/" + path;

    p = musync.commons.Path(path);

    if p.isfile():
        handled_files += 1;
    elif p.isdir():
        if Settings["recursive"]:
            for f in p.children():
                for t in readpaths(f.path, inroot):
                    yield t;
        
        if p.isroot():
            return;
        handled_dirs += 1;

    yield p;
