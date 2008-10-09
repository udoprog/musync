#
# Musync printer - Handles core printing and logging.
#
# almost nothing said trough the program should be said not using this module.
# this is to keep consistency in output.
#
# Notice that logs cannot be opened until settings has been read using
# musync.opts.read(argv).
#
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

haslogged = None;
f_log = None;
f_fixlog = None;
needfixes = None;
Settings = None;
termcap=None;

import sys, os, codecs;
from musync.opts import Settings;
from musync.errors import FatalException;

class TermCaps:
    """
    checks for termcaps and simplifies colored terminal interface.
    """
    stdout=None;
    caps=None;
    setf=None;
    colors={};
    bcolors={};
    tc=True;

    _colors=["black","blue","green","cyan","red","magenta","yellow","white"];
    _acolors=["black","red","green","yellow","blue","magenta","cyan","white"];
    _capabilites=["bold","rev","smul","cuf1","clear","sgr0","el","ed","cuu1","cr"];

    def __init__(self, stdout=sys.stdout):
        self.stdout=stdout;
        
        self.blankcaps();

        try:
            if not stdout.isatty():
                raise;

            import curses
            curses.setupterm();
        except:
            self.blankcaps();
            return;
        
        for cap in self._capabilites:
            self.colors[cap]=curses.tigetstr(cap);
            if not self.colors[cap]:
                self.colors[cap]="";

        self.setf=curses.tigetstr("setf");
        self.setaf=curses.tigetstr("setaf");
        if self.setf:
            for num, color in enumerate(self._colors):
                self.colors[color]=curses.tparm(self.setf, num);
        elif self.setaf:
            for num, color in enumerate(self._acolors):
                self.colors[color]=curses.tparm(self.setaf, num);
        else:
            for color in self._colors:
                self.colors[color]="";
    
    def blankcaps(self):
        for x in self._capabilites:
            self.bcolors[x]="";
            self.colors[x]="";
        for x in self._colors:
            self.bcolors[x]="";
            self.colors[x]="";

    def setstdout(stream):
        self.stdout=stream;

    def write(self, str, stream=None, tc=None):
        if tc is None:
            tc = self.tc;

        if stream is None:
            stream=self.stdout;

        if tc:
            stream.write(str%self.colors);
        else:
            stream.write(str%self.bcolors);

def stdout_log():
    global f_log, haslogged;
    termcap.stdout=f_log;
    termcap.tc=False;
    termcap.write("===Progress Output===\n");
    haslogged=True;

def stdout_normal():
    termcap.stdout=sys.stdout;
    termcap.tc=True;

def init():
    # hacked the termcap here.
    global termcap;
    termcap=TermCaps();
    # logfiles.

def openlogs():
    global f_log, haslogged, f_fixlog, needfixes;
    try:
        f_log = open( Settings["log"], "w" );
        f_fixlog = codecs.open( Settings["fix-log"], "w", "utf-8" );
    except Exception,e:
        raise FatalException(str(e));
    haslogged = False;
    needfixes = False;

# FIXME i don't wan't to be camelcased!
def closelogs():
    "Close logs"
    global f_log, f_fixlog;
    
    if f_log != None:
        f_log.close();
    if f_fixlog != None:
        f_fixlog.close();

def log(text):
    global haslogged;
    "append message to normal log-file"
    haslogged = True;
    f_log.write(text);

def fixlog(path, meta):
    global needfixes;
    "manages fixlog, files that musync cannot handle but should be able (like bad metadata) is appended here"
    # Check first that the file exists
    f_fixlog.write(path + "\n" );
    for key in ["album","artist","title","track"]:
        if meta[key] is None:
            meta[key] = "None";
        f_fixlog.write("%s: %s"%(key, meta[key]));
        f_fixlog.write( '\n' );

    needfixes = True;

def write(text, stream=None, tc=True):
    termcap.write(text, stream, tc);

def warning(text):
    """
    Issues a warning to the user.
    Warnings are meant to happen when something screws up but the program can still complete execution.
    """
    if Settings["silent"] and (isSuppressed("warning") or isSuppressed("all")):
        return;

    termcap.write("[!] %(red)s" + text + "%(sgr0)s\n");

def error(text):
    """
    Issues an error to the user.
    Errors should be foolowed by the stopped execution by the program.
    """
    if Settings["silent"] and (isSuppressed("error") or isSuppressed("all")):
        return;

    termcap.write("%(bold)s[exc] %(red)s" + text + "%(sgr0)s\n");

def notice(text):
    """
    Issues an notice to the user.
    Notices are to be used sparsely, only to give information to the user that can be necessary.
    """
    if Settings["silent"] and (isSuppressed("notice") or isSuppressed("all")):
        return;

    termcap.write("[:] %(green)s" + text + "%(sgr0)s\n");

def blanknotice(text):
    if Settings["silent"] and (isSuppressed("notice") or isSuppressed("all")):
        return;

    termcap.write("    %(green)s" + text + "%(sgr0)s\n");

def boldnotice(text):
    notice("%(bold)s" + text);

def action(text):
    """
    Issues an notice to the user.
    Notices are to be used sparsely, only to give information to the user that can be necessary.
    """
    if Settings["silent"] and (isSuppressed("action") or isSuppressed("all")):
        return;

    termcap.write("[-] %(magenta)s" + text + "%(sgr0)s\n");

def isSuppressed(type):
    "Checkes weither message type currently is suppressed trough configuration."
    if type in Settings["suppressed"].split(','):
        return True;
    return False;

# Current artist and album in focus
focused = {
    "artist": None,
    "album": None,
    "track": None,
    "title": None
};
    
def focus(cmeta):
    """
    Set database focus on specific file and display some informative data.
    """
    global focused;
    
    if focused["artist"] != cmeta["artist"]:
        focused["artist"] = cmeta["artist"];
        boldnotice( " > %s"%( focused["artist"] ) );
    
    if focused["album"] != cmeta["album"]:
        focused["album"] = cmeta["album"];
        boldnotice( " > > %s/%s"%( focused["artist"], focused["album"] ) );
    
    focused["title"] = cmeta["title"];
    focused["track"] = cmeta["track"];

