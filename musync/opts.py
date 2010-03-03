#
# Musync opts - read global settings and keep track of them.
#
# a common line seen in most musync modules:
#     from musync.opts import app.lambdaenv;
#
# this enables all modules to work by their own settings.
#
# this is also responsible of reading configuration files and command line options.
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
# howto add a new option:
#    add it to default Setting
#    make sure values is read specifically as boolean if necessary (from configuration file)
#    make sure it is added to help-text (if necessary).
#    make sure cli-option is parsed.

import os;
import shutil;
import getopt;
import tempfile;
import types;

from ConfigParser import RawConfigParser;
from musync.errors import FatalException;

import musync.locker;
import musync.custom;
import musync.printer;

#operating system problems
tmp=tempfile.gettempdir(); #general temp directory

class LambdaEnviron(dict):
    def __init__(self, d=dict()):
        dict.__init__(self, d);
    
    def __setattr__(self, key, val):
        self.__setitem__(key, val);
    
    def __getattr__(self, key):
        return self.__getitem__(key);

    def __hasattr__(self, key):
        return self.has_key(key);

LambdaTemplate = {
    'suppressed': lambda: [],
    "pretend": lambda: False,
    "recursive": lambda: False,
    "lock": lambda: False,
    'silent': lambda: False,
    'verbose': lambda: True,
    "force": lambda: False,
    "root": lambda: None,
    "config": lambda: None,
    "modify": lambda: dict(),
    "debug": lambda: True,
    "configurations": lambda: [],
    "lockdb": lambda: None,
    "transcode": lambda: False,
};

class AppSession:
    """
    Global application session.
    Should be common referenced in many methods.
    """
    
    def overlay_settings(self, parser, sect):
        """
        Overlay all settings from a specific section in the configuration file.
        """
        if not parser.has_section(sect):
            self.printer.error("section does not exist: " + sect);
            return False;
        
        ok = True;

        kd = dict();

        for key in parser.options(sect):
            kd[key] = parser.get(sect, key);
        
        for key in dict(kd):
            val = kd[key];
            self.settings[key] = val;
            
            if val == "":
                self.printer.warning("ignoring empty key: " + key);
                kd.pop(key);
                continue;
            
            if val.startswith("import "):
                kd.pop(key);
                
                import_stmt = val[6:].strip();

                parts = import_stmt.split(".")[1:];
                parts.reverse();
                
                imported_m = None;
                
                try:
                    imported_m = __import__(import_stmt);
                except ImportError, e:
                    self.printer.error("[I] " + key + ": " + str(e));
                    ok = False;
                    continue;
                
                while len(parts) > 0:
                    imported_m = getattr(imported_m, parts.pop());
                
                self.lambdaenv[key] = imported_m;
        
        for key in kd:
            val = kd[key];
            
            try:
                val = eval(val, self.lambdaenv);
            except Exception, e:
                self.printer.error(key + ": " + str(e));
                ok = False;
                continue;
            
            self.lambdaenv[key] = val;
        
        return ok;
    
    def read_argv(self, argv):
        cp = RawConfigParser();
        
        noconfig = True;
        
        configuration_files = map(lambda cfgfile: os.path.expanduser(os.path.join(*cfgfile)), cfgfiles);

        # not using readfiles since doesn't work under windows
        for cfg in configuration_files:
            if not os.path.isfile(cfg):
                continue;
            
            noconfig = False;
            cp.readfp(open(cfg));

        if noconfig:
            self.printer.error("no configuration files found!");
            self.printer.error("looked for:", ", ".join(configuration_files));
            self.printer.error("an example configuration should have been bundled with this program");
            return None, None, None;
        
        # open log
        if not self.overlay_settings(cp, "general"):
            self.printer.error("could not overlay settings from 'general' section");
            return None, None, None;
        
        # import the getopt module.
        try:
            # see: http://docs.python.org/lib/module-getopt.html
            opts, argv = getopt.gnu_getopt(
                argv,
                "pVRLsvfc:M:d",
                [
                    "pretend",
                    "version",
                    "recursive",
                    "lock",
                    "silent",
                    "verbose",
                    "force",
                    "root=",
                    "config=",
                    "modify=",
                    "debug",
                ]
            );
            
            return cp, opts, argv;
        except getopt.GetoptError, e:
            self.printer.error("unknown option:", e.opt);
            return None, None, None;

    def __init__(self, argv, stream):
        self.configured = False;
        self.locker = None;
        self.args = None;
        self.printer = musync.printer.AppPrinter(self, stream);
        self.lambdaenv=LambdaEnviron(LambdaTemplate);
        self.settings=LambdaEnviron();
        
        cp, opts, args = self.read_argv(argv);
        
        if cp is None:
            return;
        
        #keep to set default-config or not
        configuration = None;
        
        def parse_modify(self, base, arg):
            if base is None:
                base = dict();
            
            i = arg.find("=");
            if i <= 0:
                self.printer.warning("invalid modify argument", arg);
                return base;
            
            base[arg[:i]] = arg[i+1:]
            return base;
        
        for opt, arg in opts:
            #loop through the arguments and do what we're supposed to do:
            if opt in ("-p", "--pretend"):
                self.lambdaenv.pretend = lambda: True;
            elif opt in ("-V", "--version"):
                print version_str%version;
                return None;
            elif opt in ("-R", "--recursive"):
                self.lambdaenv.recursive = lambda: True;
            elif opt in ("-L", "--lock"):
                self.lambdaenv.lock = lambda: True;
            elif opt in ( "-s", "--silent" ):
                self.lambdaenv.silent = lambda: True;
            elif opt in ( "-v", "--verbose" ):
                self.lambdaenv.verbose = lambda: True;
            elif opt in ("-f", "--force"):
                self.lambdaenv.force = lambda: True;
            elif opt in ("-c", "--config"):
                conf = self.lambdaenv.configurations();
                conf.extend(map(lambda a: a.strip(), arg.split(",")));
                self.lambdaenv.configurations = lambda: conf;
            elif opt in ("-M", "--modify"):
                self.lambdaenv.modify = lambda: parse_modify(self, self.lambdaenv.modify, arg);
            elif opt in ("-d", "--debug"):
                self.lambdaenv.debug = lambda: True;
            elif opt in ("--root"):
                self.lambdaenv.root = lambda: arg;
            else:
              self.printer.error("unkown option:", opt);
        
        #
        # Everytime default-config is set config must be rescanned.
        #
        anti_circle = [];
        
        for config in self.lambdaenv.configurations():
            self.printer.notice("overlaying", config)

            if config in anti_circle:
                self.printer.error("Configuration has circular references, take a good look at key 'default-config'");
                return;
            
            anti_circle.append(config);
            
            if not self.overlay_settings(cp, config):
                self.printer.error("could not overlay section:", section);
                return;
        
        if not os.path.isdir(self.lambdaenv.root()):
            self.printer.error("         root:", "Root library directory non existant, cannot continue.");
            self.printer.error("current value:", self.lambdaenv.root());
            return;
        
        # check that a specific set of lambda functions exist
        for key in ["add", "rm", "hash", "targetpath", "checkhash", "lockdb", "root"]:
            if not self.lambdaenv.has_key(key):
                self.printer.error("must be a lambda function:", key);
                return;
        
        self.setup_locker(self.lambdaenv.lockdb());
        self.args = args;
        self.configured = True;

    def setup_locker(self, path):
        self.locker = musync.locker.LockFileDB(self, path);

### This is changed with setup.py to suite environment ###
#cfgfile="d:\\dump\\programs\\musync_x86\\musync.conf"
cfgfiles=[["/", "etc", "musync.conf"], ["~", ".musync"]];
version = (0,5,0,"_r0");
version_str = "Musync, music syncronizer %d.%d.%d%s";
REPORT_ADDRESS="http://sourceforge.net/projects/musync or johnjohn.tedro@gmail.com";

def Usage ():
    "returns usage information"
    
    return """
    musync - music syncing scripts
    Usage: musync [option(s)] <operation> [file1 [..]]
    
    reads [file1 [..]] or each line from stdin as source files.
    musync is designed to be non-destructive and will never modify source files
    unless it is explicitly specified in configuration.

    musync is not an interactive tool.
    musync syncronizes files into a music repository.
   
        General:
            --export (or -e):
                Will tell you what configurations that will be used
                for certain arguments.
            --version (or -V):
                Echo version information and exit.
            --force (or -f) 'force':
                Force the current action. You might be prompted to force
                certain actions.
            --allow-similar:
                tells musync not to check for similar files.

        Options:
        syntax: *long-opt* (or *short-opt*) [*args*] '*conf-key*' (also *relevant*):

            --no-fixme 'no-fixme':
                ignore 'fixme' problems (you should review fixme-file first).
            --lock (or -L) 'lock' (also 'lock-file'):
                Can be combined with fix or add for locking
                after operation has been performed.
            --pretend (or -p) 'pretend':
                Just pretend to do actions, telling what you would do.
            --recursive (or -R) 'recursive':
                Scan directories recursively.
            --silent (or -s) 'silent':
                Supresses what is defined in 'suppressed'.
            --verbose (or -v) 'verbose':
                Makes musync more talkative.
            --coloring (or -C) 'coloring':
                Invokes coloring of output.
            --root (or -r) <target_root>
                Specify target root.
            --config (or -c) <section1>,<section2>,... 'default-config'
                Specify configuration section.
                These work as overlays and the latest key specified
                is the one used, empty keys do not overwrite pre-defined.
            -M key="new value"
                Use metadata provided here instead of the one in files.
                Valid keys are:
                    artist - artist tag
                    album - album name
                    title - track title
                    track - track number
            -T <from ext>=<to ext>
                Transcode from one extension to another, tries to find
                configuration variable *from*-to-*to*.
                Example: -T flac>ogg (with key flac-to-ogg).
            --debug (-d):
                Will enable printing of  traceback on
                FatalExceptions [exc].

        Fancies:
            --progress (or -B):
                Display a progress meter instead of the usual output.
                Most notices will instead be written to log file.
                
        
        Operations:
            rm  [source..]
                Remove files. If no source - read from stdin.
            add [source..]
                Add files. If no source - read from stdin.
            fix [source..]
                Fix files in repos. If no source - read from stdin.
                Will check if file is in correct position, or move
                it and delete source when necessary. All using standard
                add and rm operations.
            lock [source..]
                Will lock a file preventing it from being removed
                or fixed.
            unlock [source..]
                Will unlock a locked file.
            inspect [source..]
                Inspect a number of files metadata.
            help
                Show the help text and exit.
        

        Files (defaults):
            log: (/tmp/musync.log)
                Created at each run - empty when no problem.
                """
