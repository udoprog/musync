# Musync commons - common classes and methods
#
# most methods are straight-forward,
# they have been left for documentation later.
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

import os;

import musync.formats;

class Path:
    """
    opens files and helps in manipulations.
    this is a wrapper for directories, used in musync
    to represent different locations on a filesystem and
    aid in simplifying the code at _many_ locations.
    """
    
    def __init__(self, app, path, **kw):
        """
        initiate variables.
        """

        self.app = app;
        
        self._path = os.path.abspath(path);
        
        if "dir" in kw:
            self.dir = kw.get("dir");
        else:
            self.dir = os.path.dirname(self._path);
        
        if "ext" in kw:
            self.ext = kw.get("ext");
        else:
            self.ext = os.path.splitext(self._path)[1].lower();
            if len(self.ext) > 0 and self.ext[0] == ".":
                self.ext = self.ext[1:];
        
        if "basename" in kw:
            self.basename = kw.get("basename");
        else:
            self.basename = os.path.splitext(self._path)[0];
        
        # open metadata if this is a file
        # if this is None, it's an indication that the file is not supported.
        if self.isfile():
            self.meta = musync.formats.open(self.path, **self.app.lambdaenv.modify);
    
    def get_path(self):
        if self.ext:
            return os.path.join(self.dir, self.basename) + "." + self.ext;
        else:
            return os.path.join(self.dir, self.basename);
    
    path = property(get_path)
    
    def isfile(self):
        return os.path.isfile(self.path);

    def isdir(self):
        return os.path.isdir(self.path);
    
    def islink(self):
        return os.path.islink(self.path);

    def exists(self):
        return os.path.exists(self.path);

    def isempty(self):
        if self.isdir():
            if len(os.listdir(self.path)) > 0:
                return False;
        return True;

    def basename(self):
        return os.path.basename(self.path);
    def dirname(self):
        return os.path.dirname(self.path);

    def rmdir(self):
        if self.isdir():
            if self.isempty():
                os.rmdir(self.path);

    def children(self):
        """
        this will yield all the children of a directory,
        making them accessable trough a "for foo in bar.children():"
        situation. usable for iteration, the 'yielded' children
        are already instantiated with this class.
        """
        try:
            for file in sorted(os.listdir(self.path)):
                yield Path(self.app, os.path.join(self.path, file));
        except OSError:
            return;
        return;
    
    def parent(self):
        return Path(self.app, os.path.dirname(self.path));

    def walk(self, test):
        """
        walks trough all paths that are beneath this path.
        this means a recursive walk trough all childrens and subchildren
        of this node.
        Yields them for simplification.
        """
        if self.isfile():
            yield self;
        elif self.isdir():
            for child in self.children():
                for c in child.walk(test):
                    yield c;
                else:
                    yield child;
        return;
    # the following are only helpful in musync
    def inroot(self):
        if not self.isroot() and self.path.startswith(self.app.lambdaenv.root):
            return True;
        return False;
    def isroot(self):
        if self.path == self.app.lambdaenv.root:
            return True;
        return False;
    def relativepath(self):
        """
        Get the relative path in root, this is useful since the root directory might be very long
        which could result in unecessary lengths in strings.
        """
        if not self.inroot():
            return False;
        
        return os.path.relpath(self.path, self.app.lambdaenv.root);
