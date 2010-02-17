#
# Musync opts - read global settings and keep track of them.
#
# a common line seen in most musync modules:
#     from musync.opts import app.settings;
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

# Program behaviour is completely controlled trough this hashmap.
# Try to read configuration, keep defaults if none found.
TemplateSettings = {
    #general
    "root":             None,
    "export":           False,
    "pretend":          False,
    "export":           False,
    "default-config":   "",
    #"filter-naming":    None,
    "log":              os.path.join(tmp, "musync.log"),
    "add":              None,
    "rm":               None,
    "filter":           None,
    "coloring":         False,
    "hash":             None,
    "checkhash":        None,
    #naming
    "dir":              None,
    "format":           None,
    #options
    "suppressed":       "notice,warning",
    "silent":           False,
    "verbose":          False,
    "recursive":        False,
    "force":            False,
    "lock":             False,
    "progress":         False,
    "lock-file":        None,
    "modify":           {
                            "artist": None,
                            "album":  None,
                            "title":  None,
                            "track":  None,
                            "year":   None,
                            "args":   []
                        },
    "transcode":        None,
    "allow-similar":    None,
    "no-fixme":         False,
    "dateformat":       "\"%Y\"",
    "debug":            True,
};

class LambdaEnviron:
    pass;

class AppSession:
    """
    Global application session.
    Should be common referenced in many methods.
    """
    
    def __init__(self, stream):
        self.settings = dict(TemplateSettings);
        self.locker = None;
        self.args = list();
        self.lambdaenv = LambdaEnviron();
        
        self.printer = musync.printer.AppPrinter(self, stream);
        
        self.eval_env={
          'os': os,
          'shutil': shutil,
          'm': musync.custom,
          's': self.lambdaenv,
        };

### This is changed with setup.py to suite environment ###
#cfgfile="d:\\dump\\programs\\musync_x86\\musync.conf"
cfgfiles=[["/", "etc", "musync.conf"], ["~", ".musync"]];
version = (0,4,1,"_r1");
version_str = "Musync, music syncronizer %d.%d.%d%s";
REPORT_ADDRESS="http://sourceforge.net/projects/musync or johnjohn.tedro@gmail.com";

# used with tmp_set/tmp_revert
reverts = {};

def settings_premanip(app):
    """
    Pre manipulation of settings.
    this is executed in order:
    premanip > sanity > postmanip
    """
    
    # encoding everything as unicode strings.
    for k in app.settings.keys():
        if isinstance(app.settings[k], basestring) and not isinstance(app.settings[k], unicode):
            app.settings[k] = app.settings[k].decode("utf-8");
    
    # parse transcoding.
    if app.settings["transcode"]:
        arg = app.settings["transcode"];
        i = arg.find('=');
        if i < 0:
            raise FatalException("--transcode (or -T) argument invalid");

        t_from = arg[:i].split(',');
        t_to = arg[i+1:];
        
        app.settings["transcode"] = [t_from, t_to];
    
    # iterate all of the modification assignments.
    for arg in app.settings["modify"]["args"]:
        i = arg.find('=');
        
        if i < 0:
            raise FatalException("--modify (or -M) argument invalid");
        
        key = arg[:i];
        modification = arg[i+1:].decode('utf-8');
        
        if key not in app.settings["modify"]:
            app.printer.error("Modify key invalid:", key);
            return False;
        else:
            app.settings["modify"][key] = modification;
            app.printer.notice("modify", key, "to", modification);
    
    return True;
    

def settings_postmanip(app):
    """
    postmanipulation of settings.
    this is executed in order:
    premanip > sanity > postmanip
    """
    
    app.settings["root"] = os.path.abspath(os.path.expanduser(app.settings["root"]));
    
    app.locker = musync.locker.LockFileDB(app.settings["root"], app.settings["lock-file"]);
    
    lockpath = app.locker.get_lockpath();
    
    if not os.path.isdir(app.settings["root"]):
        app.printer.error("         root:", "Root library directory non existant, cannot continue.");
        app.printer.error("current value:", app.settings["root"]);
        return False;
    
    if not os.path.isfile(lockpath):
        app.printer.boldnotice("  lock-file: is missing, I take the liberty to attempt creating one.");
        app.printer.boldnotice("      current value (relative to root):", lockpath);
        app.printer.boldnotice("                             lock-file:", app.settings["lock-file"]);
        try:
            f = open(lockpath, "w");
            f.close();
        except OSError, e:
            app.printer.error("    Failed to create:", str(e));
            return False;
        except IOError, e:
            app.printer.error("    Failed to create:", str(e));
            return False;
    
    return True;

###
# will try to display all noticed errors in configuration
# then return False which will stop the program from further execution.
def settings_sanity(app):
    """
    Sanity check of settings.
    this is executed in order:
    premanip > sanity > postmanip
    """
    
    # try to pass a valid format string
    err=False;
    
    # none sanitycheck
    for key in ["root","lock-file"]:
        if app.settings[key] is None:
            app.printer.error("key must exist:", key);
            err=True;
    
    for key in app.settings:
        val = app.settings[key];
        
        if val is None: # these should have been caught earlier.
            continue;
        
        if isinstance(val, basestring) and "-" not in key and val.startswith("lambda"):
            try:
                cmd = eval(val, app.eval_env);
            except Exception, e:
                app.printer.error(key + ": " + str(e));
                err = True;
                continue;
            
            if type(cmd) != types.FunctionType:
                app.printer.error(key + ": is not a lambda function");
                err = True;
                continue;
            
            app.lambdaenv.__dict__[key] = cmd;
    
    # check that a specific set of lambda functions exist
    for key in ["add", "rm", "filter", "hash", "targetpath", "checkhash"]:
        if not hasattr(app.lambdaenv, key):
            app.printer.error("must be a lambda function:", key);
            err = True;
    
    if app.settings["transcode"]:
        to=app.settings["transcode"][1];
        
        for fr in app.settings["transcode"][0]:
            key = fr + "-to-" + to;
            if key not in app.settings.keys():
                app.printer.error(
                    "transcoding is specified but corresponding <from ext>-to-<to ext> key is missing in configuration."
                );
                app.printer.error("transcode:", fr, "to", to);
                err = True;
            else:
                try:
                    cmd = eval(app.settings[key], app.eval_env);
                except Exception, e:
                    app.printer.error(key + ": " + str(e));
                    err = True;
                    continue;
                
                if type(cmd) != types.FunctionType:
                    app.printer.error(key + ": is not a function");
                    err = True;
                    continue;
                
                app.settings[key] = cmd;
    
    if err:
        app.printer.error("");
        app.printer.error("One or more configuration keys where invalid");
        app.printer.error("Check {0} for errors (correct paths, directories and commands).".format((os.path.join(cfgfiles[0]))));
        app.printer.error("Perhaps you forgot to use --config (or -c)?");
        app.printer.error("");
        return False;

    #WARNINGS
    #deprecated since output now is written to log.
    #if app.settings["progress"] and app.settings["pretend"]:
    #    app.printer.warning("options 'progress' and 'pretend' doesn't go well together.");
    
    return True;

def overlay_settings( app, parser, sect ):
    if parser.has_section(sect):
        # 'general' section
        for opt in parser.options( sect ):
            #Parse booleans
            if opt in [
                "silent",
                "verbose",
                "force",
                "coloring",
                "recursive",
                "pretend",
                "lock",
                "progress",
                "allow-similar",
                "no-fixme",
            ]:
                app.settings[opt] = parser.getboolean(sect, opt);
            else:
                app.settings[opt] = os.path.expandvars(
                    parser.get(sect, opt)
                );
        return True;
    else:
        return False

# return None for stopping of execution
def read(app, argv):
    # Check argument sanity.
    if len(argv) < 1:
        raise FatalException("Insufficient arguments, see -h");
    
    cp = RawConfigParser();
    
    # not using readfiles since doesn't work under windows
    for cfg in map(lambda cfgfile: os.path.expanduser(os.path.join(*cfgfile)), cfgfiles):
        if not os.path.isfile(cfg):
            continue;
        cp.readfp(open(cfg));
    
    # open log
    if not overlay_settings(app, cp, "general"):
        app.printer.error("could not overlay settings from 'general' section");
        return None;
    
    # import the getopt module.
    try:
        # see: http://docs.python.org/lib/module-getopt.html
        opts, args = getopt.gnu_getopt(
            argv,
            "hepVRLsvCBfhl:r:c:M:T:d",
            [
                "export",
                "pretend",
                "version",
                "recursive",
                "lock",
                "progress",
                "silent",
                "verbose",
                "coloring",
                "force",
                "log=",
                "root=",
                "config=",
                "modify=",
                "transcode=",
                "allow-similar",
                "no-fixme",
                "debug",
            ]
       );
    except getopt.GetoptError, e:
        raise FatalException("Unrecognised option '%s', try action 'help'."%( e.opt ));
    
    #keep to set default-config or not
    configuration = None;
    
    for opt, arg in opts:
        #loop through the arguments and do what we're supposed to do:
        if opt in ("-e","--export"):
            app.settings["export"] = True;
        elif opt in ("-p", "--pretend"):
            app.settings["pretend"] = True;
        elif opt in ("-V", "--version"):
            print version_str%version;
            return None;
        elif opt in ("-R", "--recursive"):
            app.settings["recursive"] = True;
        elif opt in ("-L", "--lock"):
            app.settings["lock"] = True;
        elif opt in ("-B", "--progress"):
            app.settings["progress"] = True;
        elif opt in ( "-s", "--silent" ):
            app.settings["silent"] = True;
        elif opt in ( "-v", "--verbose" ):
            app.settings["verbose"] = True;
        elif opt in ("-C", "--coloring"):
            app.settings["coloring"] = True;
        elif opt in ("-r", "--root"):
            app.settings["root"] = arg;
        elif opt in ("-c", "--config"):
            # load optional section
            configuration = arg;
        elif opt in ("-f", "--force"):
            app.settings["force"] = True;
        elif opt in ("-M", "--modify"):
            # render modify-string
            app.settings["modify"]["args"].append(arg);
        elif opt in ("-T", "--transcode"):
            app.settings["transcode"]=arg;
        elif opt in ("--allow-similar"):
            app.settings["allow-similar"] = True;
        elif opt in ("--no-fixme"):
            app.settings["no-fixme"] = True;
        elif opt in ("-d", "--debug"):
            app.settings["debug"] = True;
        else:
            raise FatalException("Undefined option '%s'."%(opt));
    
    # no config specified, use default.
    if not configuration:
        configuration = app.settings["default-config"];
        app.printer.notice("using 'default-config' since --config not found");
    
    #To avoid curcular references.
    anti_circle = [];
    #
    # Everytime default-config is set config must be rescanned.
    #

    default_config = app.settings["default-config"];
    
    while configuration:
        app.settings[ "default-config" ] = False;
        
        # Overlay configs
        for section in configuration.split(','):
            if section in anti_circle:
                app.printer.error("Configuration has circular references, take a good look at key 'default-config'");
                return None;
            
            anti_circle.append( section );
            
            if not overlay_settings(app, cp, section ):
                app.printer.error("could not overlay section:", section);
                return None;
        
        configuration = app.settings["default-config"];
    
    config_fatal = True;
    
    if settings_premanip(app) and settings_sanity(app) and settings_postmanip(app):
        config_fatal = False;
   
    app.settings["default-config"] = default_config;
    
    if app.settings["export"]:
        for key, value in app.settings.iteritems():
            if key != "export":
                print "%s %s"%(key, value);
        return None;

    if config_fatal:
        raise FatalException("example configuration should have been distributed with this program, see README");
    
    app.args = args;
    return app;

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
