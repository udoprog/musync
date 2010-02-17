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

import sys, os, codecs;

from musync.errors import FatalException;

class TermCaps:
    """
    checks for termcaps and simplifies colored terminal interface.
    """
    
    _colors=["black","blue","green","cyan","red","magenta","yellow","white"];
    _acolors=["black","red","green","yellow","blue","magenta","cyan","white"];
    _capabilites=["bold","rev","smul","cuf1","clear","sgr0","el","ed","cuu1","cr"];
    
    # Current artist and album in focus
    focused = {
        "artist": None,
        "album": None,
        "track": None,
        "title": None
    };
    
    def __init__(self, app, stream):
        self.app = app;
        self.haslogged = False;
        self.tc = True;
        self.stream=stream;
        
        self.caps=None;
        self.setf=None;
        self.colors={};
        self.bcolors={};
        
        self.blankcaps();
        
        if not self.stream.isatty():
            self.blankcaps();
            self.tc = False;
            return
        
        try:
            import curses
            curses.setupterm(os.environ.get("TERM", "xterm"), self.stream.fileno());
        except Exception, e:
            # if caps for some reason are not possible. Set them to blanks.
            self.warning("Cannot get capabilities: " + str(e));
            self.tc = False;
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
        """
        Resets all capabilities to blanks.
        """
        for x in self._capabilites:
            self.bcolors[x]="";
            self.colors[x]="";
        for x in self._colors:
            self.bcolors[x]="";
            self.colors[x]="";
    
    def setstream(stream):
        """
        Change standard stream.
        """
        self.stream=stream;
    
    def _write(self, fmt, **kw):
        """
        Write something to a stream using termcaps.
        """
        
        tc = kw.pop("tc", None);
        stream = kw.pop("stream", None);
        
        self.haslogged = True;
        
        if tc is None:
            tc = self.tc;
        
        if stream is None:
            stream=self.stream;
        
        if tc:
            kw.update(self.colors);
        else:
            kw.update(self.bcolors);
        
        stream.write(fmt.format(**kw));
  
    def warning(self, *text):
        """
        Issues a warning to the user.
        Warnings are meant to happen when something screws up but the program can still complete execution.
        """
        if self.app.settings["silent"] and (isSuppressed("warning") or isSuppressed("all")):
            return;
        
        self._write("[!] {red}{msg}{sgr0}\n", msg=self._joinstrings(text));

    def error(self, *text):
        """
        Issues an error to the user.
        Errors should be foolowed by the stopped execution by the program.
        """
        if self.app.settings["silent"] and (isSuppressed("error") or isSuppressed("all")):
            return;
        
        self._write("{bold}[exc] {red}{msg}{sgr0}\n", msg=self._joinstrings(text));

    def notice(self, *text):
        """
        Issues an notice to the user.
        Notices are to be used sparsely, only to give information to the user that can be necessary.
        """
        if self.app.settings["silent"] and (isSuppressed("notice") or isSuppressed("all")):
            return;
        
        self._write("[:] {green}{msg}{sgr0}\n", msg=self._joinstrings(text));

    def blanknotice(self, *text):
        if self.app.settings["silent"] and (isSuppressed("notice") or isSuppressed("all")):
            return;
        
        self._write("    {green}{msg}{sgr0}\n", msg=self._joinstrings(text));

    def boldnotice(self, *text):
        if self.app.settings["silent"] and (isSuppressed("notice") or isSuppressed("all")):
            return;
        
        self._write("{bold}[:] {green}{msg}{sgr0}\n", msg=self._joinstrings(text));

    def action(self, *text):
        """
        Issues an notice to the user.
        Notices are to be used sparsely, only to give information to the user that can be necessary.
        """
        if self.app.settings["silent"] and (isSuppressed("action") or isSuppressed("all")):
            return;
        
        self._write("[-] {magenta}{msg}{sgr0}\n", msg=self._joinstrings(text));
    
    def _joinstrings(self, items):
        result = list();
        
        for i in items:
            if not isinstance(i, basestring):
                continue;
            
            if isinstance(i, unicode):
                result.append(i.encode("utf-8"));
            else:
                result.append(i);
        
        return ' '.join(result);
    
    def focus(self, meta):
        """
        Set database focus on specific file and display some informative data.
        """
        if self.focused["artist"] != meta.artist:
            self.focused["artist"] = meta.artist;
            self.boldnotice(">", self.focused["artist"]);
        
        if self.focused["album"] != meta.album:
            self.focused["album"] = meta.album;
            self.boldnotice("> >", self.focused["artist"], "/", self.focused["album"] );
        
        self.focused["title"] = meta.title;
        self.focused["track"] = meta.track;

def isSuppressed(type):
    "Checkes weither message type currently is suppressed trough configuration."
    if type.lower() in map(lambda s: s.strip().lower(), self.app.settings["suppressed"].split(',')):
        return True;
    
    return False;
