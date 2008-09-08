#!/usr/bin/env python

from distutils.command.build_py import build_py as commands_build_py
from distutils.command.install import install as command_install
from distutils.core import setup

import os,sys

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["README","INSTALL","COPYING","ChangeLog"]
if os.name != "posix":
    print "Your OS isn't officially supported - sorry"
    sys.exit(1);

dfiles = [("/usr/share/musync",["cfg/posix/musync.conf","cfg/posix/musync.sed"])]
conf_decl = "cfgfile=\"/etc/musync.conf\"\n"
msg = """
Examples in /usr/share/musync,
copy these to /etc for almost-out-of-the-box functionality.

READ /etc/musync.conf
NOTE: due to some difficulties with setup.py your files in /usr/share/musync _might_ not have read permissions for everyone, fix this when copying.

Cheers,
Musync Devs
"""

class install(command_install):
    def run(self):

        ### CHECK DEPS ###
        print "checking module dependancies"
        try:
            import mutagen
            if mutagen.version[0] != 1 or mutagen.version[1] < 12:
                print "  mutagen - requires version >=1.12!"
                return;
            else:
                print "  mutagen - version %d.%d OK"%(mutagen.version[0], mutagen.version[1])
                
        except ImportError,e:
            print "  mutagen - does not exist!"
            print "    musync requires mutagen to work, please get it from"
            print "    your favorite packet mangler or visit         "
            print "    http://www.sacredchao.net/quodlibet/wiki/Download"
            return;
            
        command_install.run(self);

        print msg

class build_py(commands_build_py):
    """Specialized Python source builder."""

        # implement whatever needs to be different...
    def build_packages(self):
        commands_build_py.build_packages(self);
        global conf_decl

        f = open("build/lib/musync/opts.py","r");
        print "changing opts.py to suite operating system..."
        lines = f.readlines();
        for x,line in enumerate(lines):
            if line == "MUSYNC_CONF_DECL\n":
                lines[x] = conf_decl;
                print str(x) + ":" + line[:-1] + " changed"
        
        f.close();
        f = open("build/lib/musync/opts.py","w");
        for l in lines:
            f.write(l);
        f.close();

setup(
    name = "musync",
    version = "0.4.0_r1",
    description = "Musync is a simple and usable music organizer which uses metadata to sort the music into libraries.",
    author = "John-John Tedro and Albin Stjerna",
    author_email = "johnjohn.tedro@gmail.com, albin.stjerna@gmail.com",
    url = "http://trac.ostcon.org",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found 
    #recursively.)
    packages = ['musync'],
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    package_data = {'musync' : files },
    #'runner' is in the root.
    scripts = ["scripts/musync"],
    long_description = """
    see http://trac.ostcon.org/MuSync
    """,
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []     
    data_files = dfiles,
    cmdclass = {'build_py': build_py,'install': install}
) 
