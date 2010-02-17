#
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

from musync.errors import WarningException, FatalException; # exceptions
import string;
import os.path;

class LockFileDB:
    def __init__(self, root, lock_file=".lock"):
        self.changed = False;
        self.removed = False;
        self.root = root;
        self.lock_file = lock_file;

        lockpath=self.get_lockpath();

        if not os.path.isfile(lockpath):
            f = open(lockpath, "w");
            f.close();
        
        f = open(lockpath, "r");
        self.DB = [x.strip(string.whitespace) for x in f.readlines()];
        f.close();
        
        self.DB_NEWS=[]

    def unlock(self, path):
        if not self.islocked(path):
            raise WarningException("%s - is not locked"%(path.path));

        if not path.inroot():
            raise WarningException("%s - is not in root"%(path.path));
        
        relpath=path.relativepath();
        
        if not relpath:
            raise WarningException("%s - failed to get relative path"%(path.path));
        
        self.DB.remove(relpath);
        self.changed = True;
        self.removed = True;

    def lock(self, path):
        if self.islocked(path):
            raise WarningException("%s - is already locked"%(path.path));
        if self.parentislocked(path):
            raise WarningException("%s - is already locked (parent)"%(path.path));
        if not path.inroot():
            raise WarningException("%s - is not in root"%(path.path));

        relpath=path.relativepath();
        if not relpath:
            raise WarningException("%s - failed to get relativepath"%(path.path));

        self.DB_NEWS.append(relpath + "\n");
        self.changed = True;

    def islocked(self, path):
        relpath=path.relativepath();
        
        if not relpath:
            raise WarningException("%s - failed to get relativepath"%(path.path));

        if relpath in self.DB:
            return True;
        else:
            return False;

    def parentislocked(self, path):
        p = path.parent();
        
        if p.isdir() and p.inroot():
            relpath=p.relativepath();
            if not relpath:
                raise WarningException("%s - failed to get relativepath"%(path.path));
            if relpath in self.DB:
                return True;
        
        return False;
    
    def sanity_chk(self):
        if self.root is None:
            raise FatalException("locker.root is None");
        
        if self.lock_file is None:
            raise FatalException("locker.lock_file is None");

    def stop(self):
        if self.changed:
            # this will trigger writing if database has been changed.
            lockpath=self.get_lockpath();

            if not os.path.isfile(lockpath):
                f = open(lockpath, "w");
                f.close();
            
            if self.removed:
                f = open(lockpath, "w");
                for p in self.DB:
                    f.writelines(p);
                    f.write("\n");
                f.close();
            else:
                f = open(lockpath, "a");
                f.writelines(self.DB_NEWS);
                f.close();

    def get_lockpath(self):
        self.sanity_chk();
        return os.path.join(self.root, self.lock_file);
