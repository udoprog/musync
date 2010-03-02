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

import string;
import os.path;

class LockFileDB:
    def __init__(self, app, lock_file):
        self.app = app;
        self.changed = False;
        self.removed = False;
        self.lock_file = lock_file;
        
        if not os.path.isfile(self.lock_file):
            f = open(self.lock_file, "w");
            f.close();
        
        f = open(self.lock_file, "r");
        self.DB = [x.strip(string.whitespace) for x in f.readlines()];
        f.close();
        
        self.DB_NEWS=[]

    def unlock(self, path):
        if not self.islocked(path):
            self.app.notice("is not locked:", path.path);
            return False;
        
        if not path.inroot():
            self.app.warning("is not in root:", path.path);
            return False;
        
        self.DB.remove(path.relativepath());
        self.changed = True;
        self.removed = True;

    def lock(self, path):
        if self.islocked(path):
            self.app.notice("is already locked:", path.path);
            return False;

        if self.parentislocked(path):
            self.app.notice("is already locked (parent):", path.path);
            return False;
        
        if not path.inroot():
            self.app.warning("is not in root:", path.path);
            return False;
        
        self.DB_NEWS.append(path.relativepath() + "\n");
        self.changed = True;

    def islocked(self, path):
        if path.relativepath() in self.DB:
            return True;
        else:
            return False;
    
    def parentislocked(self, path):
        if path.parent().relativepath() in self.DB:
            return True;
        
        return False;
    
    def stop(self):
        if self.changed:
            # this will trigger writing if database has been changed.
            if not os.path.isfile(self.lock_path):
                f = open(self.lock_path, "w");
                f.close();
            
            if self.removed:
                f = open(self.lock_path, "w");
                for p in self.DB:
                    f.writelines(p);
                    f.write("\n");
                f.close();
            else:
                f = open(self.lock_path, "a");
                f.writelines(self.DB_NEWS);
                f.close();
