import musync.commons;
import musync.sign;
import musync.dbman as db;

import sys;
import os;

class Goal(object):
    prefix = None;
    required = [];
    optional = [];
    
    fileonly = False;
    build_target = False;
    require_filemeta = False;
    only_root = False;
    
    functions = dict();
    
    def __init__(self, app):
        self.app = app;
        self.printer = app.printer;
    
    def run_file(self, source):
        self.printer.warning("Goal#run_file not defined");
    
    def pretend_file(self, source):
        self.printer.warning("Goal#pretend_file not defined");
    
    def run_dir(self, source):
        self.printer.warning("Goal#run_dir not defined");
    
    def pretend_dir(self, source):
        self.printer.warning("Goal#pretend_dir not defined");
    
    def operate(self):
        """
        Operation abstraction, this is the only function used by different operations.
        """
        
        for p in self._readargs(self.app.args[1:]):
            if musync.sign.Interrupt is True:
                self.printer.error("Caught Interrupt");
                return;
            
            if p.path == self.app.lambdaenv.lockdb():
                self.printer.warning("ignoring lockdb:", p.path);
                continue;
            
            if not p.exists():
                self.printer.warning("does not exist:", p.path);
                continue;
            
            if self.only_root and not p.inroot():
                self.printer.warning("not in root:", p.path);
                continue;
            
            if p.isdir():
                if self.fileonly:
                    self.printer.warning("ignoring (not a file):", p.path);
                    continue;
                
                if self.app.lambdaenv.pretend:
                    self.pretend_dir(p);
                else:
                    self.run_dir(p);
            
            if p.isfile():
                if (self.require_filemeta or self.build_target) and p.meta is None:
                    self.printer.warning("could not open metadata:", p.path);
                    continue;
                
                args = [p];
                
                if self.build_target:
                    target = self._build_target(p);
                    
                    if self.app.locker.islocked(target):
                        self.printer.warning("locked:", target.path);
                        continue;
                    
                    if self.app.locker.parentislocked(target):
                        self.printer.warning("locked (parent):", target.path);
                        continue;
                    
                    args.append(target);
                
                if self.app.lambdaenv.pretend:
                    self.pretend_file(*args);
                else:
                    self.run_file(*args);
    
    def _readargs(self, args):
        """
        reads paths in different ways depending on number of arguments.
        yields the filepaths for easy access.
        """
        if len(args) <= 0:
            while True:
                arg = sys.stdin.readline()[:-1];
            
                if not arg:
                    break;
                
                for p in self._readpaths(arg):
                    yield p;
        else:
            for arg in args:
                for p in self._readpaths(arg):
                    yield p;
        
        return;

    def _readpaths(self, path):
        """
        
        """
        p = musync.commons.Path(self.app, path);
        
        if p.isdir():
            if self.app.lambdaenv.recursive:
                for f in p.children():
                    for t in self._readpaths(f.path):
                        yield t;
            
            if p.isroot():
                return;

        yield p;

    def _build_target(self, source, **kw):
        """
        builds a target for many of the functions in musync.dbman
        this is just a complex concatenation of directories and 
        filenames.

        notice! this function resides in this module because we havent
                found a better place yet.

        @param p     Original Path instance which the metadata was
                     extracted from.
        @param meta A dict containing the desired meta-name for target.
                     notice that this should have been cleaned with
                     musync.meta.cleanmeta();
        """
        
        return musync.commons.Path(self.app,
                os.path.join(self.app.lambdaenv.root, self.app.lambdaenv.targetpath(source)), **kw);

    @classmethod
    def getgoal(cls, prefix):
        if prefix is None:
            return None;

        for goal in cls.__subclasses__():
            if prefix.lower() in goal.prefix:
                return goal;
        
        return None;
    
    @classmethod
    def getgoals(cls):
        return cls.__subclasses__();

class AddGoal(Goal):
    prefix = ["add"];
    required = ["add"];
    optional = ["pre-add", "post-add"];
    
    fileonly = True;
    require_filemeta = True;
    build_target = True;
    
    def run_file(self, source, target):
        if self.functions.has_key("pre-add"):
            self.functions.get("pre-add")(source, target);
        
        # this causes nice display of artist/album
        self.printer.focus(source.meta);
        
        if not self.app.lambdaenv.force and target.exists():
            self.printer.error("already exists (not forced):", target.relativepath());
            return;
        
        self.printer.action("adding file:", target.relativepath());
        
        if not self.functions.get("add")(source, target):
            self.printer.error("add operation failed");
            return;
        
        if not target.exists():
            self.printer.error("target was not created:", target.relativepath());
            return;
        
        if self.functions.has_key("post-add"):
            self.functions.get("post-add")(source, target);
    
    def pretend_file(self, source, target):
        self.printer.focus(source.meta);
        
        if self.app.locker.islocked(target):
            self.printer.warning("locked:", source.path);
            return;
        
        if target.exists():
            self.printer.error("already exists:", target.relativepath());
            return;
        
        self.printer.notice("would run add with:");
        self.printer.notice("    src:", source.path);
        self.printer.notice("    dst:", tasrget.path);

class InspectGoal(Goal):
    prefix = ["inspect"];
    required = ["targetpath"];
    
    fileonly = True;
    require_filemeta = True;
    
    def run_file(self, source):
        """
        give a friendly suggestion of how you would name a specific file.
        """
        
        self.printer.boldnotice(source.meta.filename)
        self.printer.blanknotice("artist:    ", repr(source.meta.artist))
        self.printer.blanknotice("album:     ", repr(source.meta.album))
        self.printer.blanknotice("title:     ", repr(source.meta.title))
        self.printer.blanknotice("track:     ", repr(source.meta.track))
        self.printer.blanknotice("year:      ", repr(source.meta.year))
        self.printer.blanknotice("targetpath:", repr(self.functions.get("targetpath")(source)), "from", self.app.settings.targetpath);
        # this causes nice display of artist/album
        self.printer.focus(source.meta);

    def pretend_file(self, source):
        self.printer.notice("would inspect:", source.path);

class LockGoal(Goal):
    prefix = ["lock"]
    
    only_root = True;

    def run_dir(self, source):
        self.app.locker.lock(source);
        self.printer.notice("dir has been locked:", source.path);
    
    def run_file(self, source):
        self.app.locker.lock(source);
        self.printer.notice("file has been locked:", source.path);

    def pretend_dir(self, source):
        self.printer.notice("would lock directory:", source.path);
    
    def pretend_file(self, source):
        self.printer.notice("would lock file:", source.path);

class UnlockGoal(Goal):
    prefix = ["unlock"]
    
    only_root = True;

    def run_dir(self, source):
        self.app.locker.unlock(source);
        self.printer.notice("dir has been unlocked:", source.path);
    
    def run_file(self, source):
        if self.app.locker.islocked(source):
            self.app.locker.unlock(source);
            self.printer.notice("path has been unlocked:", source.path);
        elif self.app.locker.parentislocked(source):
            tp = source.parent();
            self.printer.warning("parent is locked:", tp.path);
        else:
            self.printer.warning("path is not locked:", source.path);

    def pretend_file(self, source):
        self.printer.notice("would lock file:", source.path);

    def pretend_dir(self, source):
        self.printer.notice("would lock directory:", source.path);

class FixGoal(Goal):
    prefix = ["fix"];
    require = ["add"]
    
    root_only = True;
    build_target = True;
    
    def run_dir(self, source):
        if not source.isempty():
            self.printer.notice("sane:", source.relativepath());
            return;
        
        self.printer.action("removing empty dir:", p.relativepath());
        source.rmdir();
    
    def run_file(self, source, target):
        if self.functions.has_key("pre-add"):
            self.functions.get("pre-add")(source, target);
        
        if source.path == target.path:
            self.printer.notice("sane:", target.relativepath());
            return;
        
        if not self.app.lambdaenv.force and target.exists():
            self.printer.warning("already exists (not forced):", target.relativepath());
            return;
        
        self.printer.action("fixing file:", source.relativepath());
        self.printer.action("         as:", target.relativepath());
        
        if not self.functions.get("add")(source, target):
            self.printer.error("add operation failed");
            return;
        
        if not target.exists():
            self.printer.error("target was not created:", target.relativepath());
            return;

class RemoveGoal(Goal):
    prefix = ["remove", "rm"];
    required = ["rm"];
    optional = ["pre-rm"];
    
    fileonly = True;
    build_target = True;
    
    def run_file(self, source, target):
        if self.functions.has_key("pre-rm"):
            self.functions.get("pre-rm")(source, target);
        
        if source.path == target.path and not self.app.lambdaenv.force:
            self.printer.warning("target is same as source (not forced):", target.relativepath());
            return;
        
        if not target.exists():
            self.printer.warning("target does not exist:", target.relativepath());
            return;
        
        self.printer.action("removing file:", target.relativepath());
        
        self.functions.get("rm")(target);
        
        if target.exists():
            self.printer.error("target was not removed:", target.relativepath());
            return;

    def pretend_file(self, source, target):
        if self.functions.has_key("pre-rm"):
            self.functions.get("pre-rm")(source, target);
        
        if source.path == target.path and not self.app.lambdaenv.force:
            self.printer.warning("target is same as source (not forced):", target.relativepath());
            return;
        
        if not target.exists():
            self.printer.warning("target does not exist:", target.relativepath());
            return;
        
        self.printer.notice("would remove file:", target.relativepath());
