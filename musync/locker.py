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

DB=[]
DB_NEWS=[]
changed = False;
removed = False;

root=None;
lock_file=None;

def unlock(path):
    global changed, removed, DB;
    if not islocked(path):
        raise WarningException("%s - is not locked"%(path.path));
    if not path.inroot():
        raise WarningException("%s - is not in root"%(path.path));
    
    relpath=path.relativepath();
    if not relpath:
        raise WarningException("%s - failed to get relativepath"%(path.path));
    
    DB.remove(relpath);
    changed = True;
    removed = True;

def lock(path):
    global changed, DB_NEWS;
    if islocked(path):
        raise WarningException("%s - is already locked"%(path.path));
    if parentislocked(path):
        raise WarningException("%s - is already locked (parent)"%(path.path));
    if not path.inroot():
        raise WarningException("%s - is not in root"%(path.path));

    relpath=path.relativepath();
    if not relpath:
        raise WarningException("%s - failed to get relativepath"%(path.path));

    DB_NEWS.append(relpath + "\n");
    changed = True;

def islocked(path):
    global DB;

    relpath=path.relativepath();
    if not relpath:
        raise WarningException("%s - failed to get relativepath"%(path.path));

    if relpath in DB:
        return True;
    else:
        return False;

def parentislocked(path):
    p = path.parent();
    if p.isdir() and p.inroot():
        relpath=p.relativepath();
        if not relpath:
            raise WarningException("%s - failed to get relativepath"%(path.path));
        if relpath in DB:
            return True;

    return False;

import os.path;

def sanity_chk():
    if root is None:
        raise FatalException("locker.root is None");

    if lock_file is None:
        raise FatalException("locker.lock_file is None");

def init():
    global DB;
    lockpath=get_lockpath();

    if not os.path.isfile(lockpath):
        f = open(lockpath,"w");
        f.close();
    
    f = open(lockpath,"r");
    DB = [x[:-1] for x in f.readlines()];
    f.close();

def stop():
    global changed, removed, DB, DB_NEWS;
    if changed:
        # this will trigger writing if database has been changed.
        lockpath=get_lockpath();

        if not os.path.isfile(lockpath):
            f = open(lockpath,"w");
            f.close();
        
        if removed:
            f = open(lockpath,"w");
            for p in DB:
                f.write(p);
            f.close();
        else:
            f = open(lockpath, "a");
            f.writelines(DB_NEWS);
            f.close();

def get_lockpath():
    global root, lock_file;
    sanity_chk();
    return "%s/%s"%(root, lock_file);
