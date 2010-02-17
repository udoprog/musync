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

class TermCapHolder:
    pass;

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
    
    def __init__(self, stream):
        import curses
        
        self.haslogged = False;
        self.tc = True;
        self.stream=stream;
        
        self.caps=None;
        self.setf=None;
        self.col = {};
        self.c = TermCapHolder();
        
        if not self.stream.isatty():
            self.blankcaps();
            self.tc = False;
            return
        
        try:
            curses.setupterm(os.environ.get("TERM", "xterm"), self.stream.fileno());
        except Exception, e:
            self.blankcaps();
            self.tc = False;
            # if caps for some reason are not possible. Set them to blanks.
            self.warning("Cannot get capabilities: " + str(e));
            return;
        
        for cap in self._capabilites:
            v = curses.tigetstr(cap);
            
            if not v:
                v = "";
            
            self.col[cap] = v;
            setattr(self.c, cap, v);
        
        self.setf=curses.tigetstr("setf");
        self.setaf=curses.tigetstr("setaf");
        
        colors = {};
        tf = None;
        
        if self.setf:
            tf = self.setf;
            colors = self._colors;
        elif self.setaf:
            tf = self.setaf;
            colors = self._acolors;
        
        for num, color in enumerate(colors):
            v = curses.tparm(tf, num);
            self.col[color] = v;
            setattr(self.c, color, v);
    
    def blankcaps(self):
        """
        Resets all capabilities to blanks.
        """
        for x in self._capabilites:
            self.col[x]="";
            setattr(self.c, x, "");
        
        for x in self._colors:
            self.col[x]="";
            setattr(self.c, x, "");
    
    def setstream(stream):
        """
        Change standard stream.
        """
        self.stream=stream;
    
    def _write(self, fmt, **kw):
        """
        Write something to a stream using termcaps.
        """
        
        stream = kw.pop("stream", None);
        
        self.haslogged = True;
        
        if stream is None:
            stream=self.stream;
        
        kw.update(self.col);
        stream.write(fmt.format(**kw));
    
    def _writeall(self, *args, **kw):
        kw.get("stream", self.stream).write(''.join(args));

class AppPrinter(TermCaps):
    """
    A custom commandline application printer using termcaps.
    """
    def __init__(self, app, stream):
        self.app = app;
        TermCaps.__init__(self, stream);
        self._suppressed = map(lambda s: s.strip().lower(), self.app.settings.get("suppressed", "").split(','));
    
    def warning(self, *text):
        """
        Issues a warning to the user.
        Warnings are meant to happen when something screws up but the program can still complete execution.
        """
        if self.app.settings["silent"] and (self.is_suppressed("warning") or self.is_suppressed("all")):
            return;
        
        self._writeall("[!] ", self.c.red, self._joinstrings(text), self.c.sgr0, "\n");

    def error(self, *text):
        """
        Issues an error to the user.
        Errors should be foolowed by the stopped execution by the program.
        """
        if self.app.settings["silent"] and (self.is_suppressed("error") or self.is_suppressed("all")):
            return;
        
        self._writeall(self.c.bold, "[e] ", self.c.red, self._joinstrings(text), self.c.sgr0, "\n");
    
    def notice(self, *text):
        """
        Issues an notice to the user.
        Notices are to be used sparsely, only to give information to the user that can be necessary.
        """
        if self.app.settings["silent"] and (self.is_suppressed("notice") or self.is_suppressed("all")):
            return;
        
        self._writeall("[:] ", self.c.green, self._joinstrings(text), self.c.sgr0, "\n");
    
    def blanknotice(self, *text):
        if self.app.settings["silent"] and (self.is_suppressed("notice") or self.is_suppressed("all")):
            return;
        
        self._writeall("    ", self.c.green, self._joinstrings(text), self.c.sgr0, "\n");
    
    def boldnotice(self, *text):
        if self.app.settings["silent"] and (self.is_suppressed("notice") or self.is_suppressed("all")):
            return;
        
        
        self._writeall(self.c.bold, "[:] ", self.c.green, self._joinstrings(text), self.c.sgr0, "\n");
    
    def action(self, *text):
        """
        Issues an notice to the user.
        Notices are to be used sparsely, only to give information to the user that can be necessary.
        """
        if self.app.settings["silent"] and (self.is_suppressed("action") or self.is_suppressed("all")):
            return;
        
        self._write("[-]", self.c.magenta, self._joinstrings(text), self.c.sgr0, "\n");
    
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
    
    def is_suppressed(type):
        "Checkes weither message type currently is suppressed trough configuration."
        if type.lower() in self._suppressed:
            return True;
        
        return False;
