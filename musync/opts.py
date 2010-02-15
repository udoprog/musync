#
# Musync opts - read global settings and keep track of them.
#
# a common line seen in most musync modules:
#     from musync.opts import Settings;
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

from ConfigParser import RawConfigParser;
from musync.errors import FatalException;
from musync import eval_env;

import os;
import getopt;
import tempfile;
import types;

#operating system problems
tmp=tempfile.gettempdir(); #general temp directory

### This is changed with setup.py to suite environment ###
#cfgfile="d:\\dump\\programs\\musync_x86\\musync.conf"
cfgfiles=[["/", "etc", "musync.conf"], ["~", ".musync"]];
version = (0,4,0,"_rc4");
version_str = "Musync, music syncronizer %d.%d.%d%s";
REPORT_ADDRESS="http://sourceforge.net/projects/musync or johnjohn.tedro@gmail.com";

# used with tmp_set/tmp_revert
reverts = {};

def tmp_set(key, value):
    """
    Used to temporary set a Settings key to another value.
    Revert with tmp_revert
    """
    global reverts, Settings;
    if reverts.has_key(key) and reverts[key] is not None:
        raise FatalException("cannot temporary set config - key already set");

    if not Settings.has_key(key):
        raise FatalException("key does not exist in configuration");

    reverts[key] = Settings[key];
    Settings[key] = value;

def tmp_revert(key):
    """
    Used to revert a Settings key that has been set using tmp_set.
    """
    global reverts, Settings;
    if not reverts.has_key(key):
        return;

    if not Settings.has_key(key):
        return;
    
    Settings[key] = reverts[key];
    reverts[key] = None;

# Program behaviour is completely controlled trough this hashmap.
# Try to read configuration, keep defaults if none found.
Settings = {
    #general
    "root":             None,
    "export":           False,
    "pretend":          False,
    "export":           False,
    "default-config":   "",
    #"filter-naming":    None,
    "log":              os.path.join(tmp, "musync.log"),
    "fix-log":          os.path.join(tmp, "musync-fixes.log"),
    "add-with":         None,
    "rm-with":          None,
    "filter-with":      None,
    "coloring":         False,
    "hash-with":        None,
    "check-hash":       False,
    #naming
    "dir":              "%(artist)s/%(album)s",
    "format":           "%(track)02d-%(title)s%(ext)s",
    #"supported-ext":    ".mp3,.ogg,.flac",
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
                            "album": None,
                            "title": None,
                            "track": None,
                            "year": None,
                            "args": []
                        },
    "transcode":        None,
    "allow-similar":    None,
    "no-fixme":         False,
    "dateformat":       "\"%Y\"",
    "debug":            None,
};

def settings_premanip(pl):
    """
    Pre manipulation of settings.
    this is executed in order:
    premanip > sanity > postmanip
    """
    
    printer, logger = pl;
    
    # encoding everything as strings.
    for k in Settings.keys():
      if isinstance(Settings[k], unicode):
        Settings[k] = Settings[k].encode("utf-8");

    # parse transcoding.
    if Settings["transcode"]:
        arg = Settings["transcode"];
        i = arg.find('=');
        if i < 0:
            raise FatalException("--transcode (or -T) argument invalid");

        t_from = arg[:i].split(',');
        t_to = arg[i+1:];
        
        Settings["transcode"] = [t_from, t_to];
    
    # iterate all of the modification assignments.
    for arg in Settings["modify"]["args"]:
        i = arg.find('=');
        if i < 0:
            raise FatalException("--modify (or -M) argument invalid");

        key = arg[:i];
        modification = arg[i+1:];
        
        if key not in Settings["modify"]:
            raise FatalException("Modify key '%s' invalid"%( key ));
        else:
            Settings["modify"][key] = modification;
            printer.notice("using: %s=\"%s\""%( key, modification ));

    return True;
    

def settings_postmanip(pl):
    """
    postmanipulation of settings.
    this is executed in order:
    premanip > sanity > postmanip
    """

    printer, logger = pl;
    
    Settings["root"] = os.path.abspath(os.path.expanduser(Settings["root"]));
    import musync.locker; # needed for settings global variables
    musync.locker.root = Settings["root"];
    musync.locker.lock_file = Settings["lock-file"];
   
    # attempt to create 'lock-file'
    lockpath=musync.locker.get_lockpath();

    if not os.path.isdir(Settings["root"]):
        printer.error("         root: Root library directory non existant, cannot continue.");
        printer.error("current value: %s"%(Settings["root"]));
        return False;
    
    if not os.path.isfile(lockpath):
        printer.boldnotice("  lock-file: is missing, I take the liberty to attempt creating one.");
        printer.boldnotice("      current value (relative to root): %s"%(lockpath));
        printer.boldnotice("                             lock-file: %s"%(Settings["lock-file"]));
        try:
            f = open(lockpath, "w");
            f.close();
        except Exception, e:
            printer.error("    Failed to create - %s"%(str(e)));
            return False;
    
    return True;

###
# will try to display all noticed errors in configuration
# then return False which will stop the program from further execution.
def settings_sanity(pl):
    """
    Sanity check of settings.
    this is executed in order:
    premanip > sanity > postmanip
    """
    
    printer, logger = pl;
    
    # try to pass a valid format string
    err=False;
    try:
        Settings["format"]%{'artist':"",'album':"",'title':"",'track':0,'ext':""};
    except TypeError:
        printer.error("configuration key 'format' invalid");
        err=True;

    #if not os.path.iswriteable(Settings["root"]):
    #    printer.error("root: is not writeable");
    #    err=True;

    # none sanitycheck
    for key in ["root","lock-file","add-with","rm-with","filter-with","hash-with"]:
        if Settings[key] is None:
            printer.error("%s: must exist."%(key));
            printer.error("    current value: %s"%(Settings[key]));
            err=True;
        else:
            # do a dummy replace to check formats and SHIT
            try:
                for k in Settings[key].split(' '):
                    k%{
                        'source': "foo",
                        'dest': "bar",
                        'artist': "baz",
                        'album': "foobar",
                        'track': 0,
                        'year': 0,
                        'ext': "baz",
                        'target': "fbz",
                    };
            except ValueError, e:
                printer.error("%s: %s."%(key, str(e)));
                printer.error("    current value: %s"%(Settings[key].replace("%", "%%")));
                printer.error("    possible problems with python format; e.g. '%%(source)s' being '%%(source)'.");
                err = True;
    
    # these must exist as path
    for key in ["rm-with", "add-with", "filter-with", "hash-with"]:
        if Settings[key] is None: # these should have been caught earlier.
            continue;
        
        try:
            cmd = eval(Settings[key], eval_env);
        except Exception, e:
            printer.error(key + ": " + str(e));
            err = True;
            continue;
        
        if type(cmd) != types.FunctionType:
            printer.error(key + ": is not a function");
            err = True;
            continue;
        
        Settings[key] = cmd;
    
    if Settings["transcode"]:
        to=Settings["transcode"][1];
        for fr in Settings["transcode"][0]:
            key = "%s-to-%s"%(fr, to);
            if key not in Settings.keys():
                printer.error(
                    "transcoding is specified but corresponding <from ext>-to-<to ext> key is missing in configuration."
                );
                printer.error("transcode: %s=%s"%(fr, to));
                err = True;
            else:
                try:
                    cmd = eval(Settings[key], eval_env);
                except Exception, e:
                    printer.error(key + ": " + str(e));
                    err = True;
                    continue;
                
                if type(cmd) != types.FunctionType:
                    printer.error(key + ": is not a function");
                    err = True;
                    continue;
                
                Settings[key] = cmd;
    
    if err:
        printer.error("");
        printer.error("One or more configuration keys where invalid");
        printer.error("Check {0} for errors (correct paths, directories and commands).".format((os.path.join(cfgfiles[0]))));
        printer.error("Perhaps you forgot to use --config (or -c)?");
        printer.error("");
        return False;

    #WARNINGS
    #deprecated since output now is written to log.
    #if Settings["progress"] and Settings["pretend"]:
    #    printer.warning("options 'progress' and 'pretend' doesn't go well together.");

    return True;

def OverlaySettings( parser, sect ):
    if parser.has_section(sect):
        #print "Overlaying [%s] settings"%( sect );
        
        # 'general' section
        for opt in parser.options( sect ):
            #Parse booleans
            if opt in [
                "silent",
                "verbose",
                "force",
                "coloring",
                "check-hash",
                "recursive",
                "pretend",
                "lock",
                "progress",
                "allow-similar",
                "no-fixme",
            ]:
                Settings[opt] = parser.getboolean(sect, opt);
            else:
                Settings[opt] = os.path.expandvars(
                    parser.get(sect, opt)
                );
        return;
    else:
        raise FatalException("missing configuration key - %s"%( sect ));

# return None for stopping of execution
def read(argv, pl):
    printer, logger = pl;
    
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
    OverlaySettings(cp, "general");
    
    # import the getopt module.
    try:
        # see: http://docs.python.org/lib/module-getopt.html
        opts, args = getopt.gnu_getopt(
            argv,
            "hepVRLsvCBfhl:r:c:M:T:d",
            [
                "help",
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
                "check-hash",
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
        raise FatalException("Unrecognised option '%s', try -h or --help."%( e.opt ));
    
    #keep to set default-config or not
    configuration = None;
    
    for opt, arg in opts:
        #loop through the arguments and do what we're supposed to do:
        if opt in ("-h", "--help"):
            return Usage();
        elif opt in ("-e","--export"):
            Settings["export"] = True;
        elif opt in ("-p", "--pretend"):
            Settings["pretend"] = True;
        elif opt in ("-V", "--version"):
            print version_str%version;
            return None;
        elif opt in ("-R", "--recursive"):
            Settings["recursive"] = True;
        elif opt in ("-L", "--lock"):
            Settings["lock"] = True;
        elif opt in ("-B", "--progress"):
            Settings["progress"] = True;
        elif opt in ( "-s", "--silent" ):
            Settings["silent"] = True;
        elif opt in ( "-v", "--verbose" ):
            Settings["verbose"] = True;
        elif opt in ("-C", "--coloring"):
            Settings["coloring"] = True;
        elif opt in ("-r", "--root"):
            Settings["root"] = arg;
        elif opt in ("-c", "--config"):
            # load optional section
            configuration = arg;
        elif opt in ("-l", "--log"):
            Settings["fix-log"] = arg;
        elif opt in ("-f", "--force"):
            Settings["force"] = True;
        elif opt in ("-h", "--check-hash"):
            Settings["check-hash"] = True;
        elif opt in ("-M", "--modify"):
            # render modify-string
            Settings["modify"]["args"].append(arg);
        elif opt in ("-T", "--transcode"):
            Settings["transcode"]=arg;
        elif opt in ("--allow-similar"):
            Settings["allow-similar"] = True;
        elif opt in ("--no-fixme"):
            Settings["no-fixme"] = True;
        elif opt in ("-d", "--debug"):
            Settings["debug"] = True;
        else:
            raise FatalException("Undefined option '%s'."%(opt));
    
    # no config specified, use default.
    if not configuration:
        configuration = Settings["default-config"];
        printer.notice("[using 'default-config' since --config not found]");
    
    #To avoid curcular references.
    anti_circle = [];
    #
    # Everytime default-config is set config must be rescanned.
    #

    default_config = Settings["default-config"];
    
    while configuration:
        Settings[ "default-config" ] = False;
        
        # Overlay configs
        for section in configuration.split(','):
            if section in anti_circle:
                raise FatalException("Configuration has circular references, take a good look at key 'default-config'");
            
            anti_circle.append( section );
            OverlaySettings( cp, section );
        
        configuration = Settings["default-config"];
    
    config_fatal = True;
    
    if settings_premanip(pl) and settings_sanity(pl) and settings_postmanip(pl):
        config_fatal = False;
   
    Settings["default-config"] = default_config;

    if Settings["export"]:
        for key, value in Settings.iteritems():
            if key != "export":
                print "%s %s"%(key, value);
        return None;

    if config_fatal:
        raise FatalException("example configuration should have been distributed with this program, see README");

    return args;

def Usage ():
    "prints usage information"
    
    print """
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
            --help (or -h):
                Show this text and exit.
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
            --log (or -l) <fix-log> 'fix-log':
                Specify where the fix-log is to be written (or read when
                operation 'fix')
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
        
        Files (defaults):
            log: (/tmp/musync.log)
                Created at each run - empty when no problem.
            fix-log: (/tmp/musync-fixes.log)
                Created at each run - lists all files in need
                of fixing to be used with musync, usually metadata
                problems.
                """
    return None;
