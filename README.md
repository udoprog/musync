About Musync
============
Musync is a music organizer which sorts music files, from the commandline, to where you want them to be.

It was conceptuated by Albin Stjerna, and mostly implemented by John-John Tedro.

Musync is *highly* customizable using it's configuration files, which relies heavily on python's 'eval' to do it's dirty work, but by default it is highly efficient in doing the following:

* Add your music in a nice filestructure which is compatible with unix naming conventions (only ascii letters).
* Clean any 'ugly letters' into a ascii-readable alternative. Like 'e' with an acute diacritic (é) to ascii 'e'.

Therefore, even if you listen to french, german or russian artists. You will still be able to browse your music archive with ease from a shell.

Configuration
=============
As mentioned, musync is *highly* customizable. The only work that musync performs for you, is automatic iteration of directories, identification of files containing metadata, and performing an event chain.

The event chain for the action 'add' could look like the following:

* *scan for files*
* *filter files with readable metadata and calculate 'dest' using 'targetpath'*
* *perform 'add' on each file*
* *perform 'checkhash' on 'src' and 'dest', if the return value of chechhash does not match, try to add again or fail after a couple of times.

Each of the methods, 'add'. 'checkhash' and 'targetpath' are defined using configuration, and most of them use one or more methods from the musync.custom namespace.

To see the source code of these methods (if you want inspiration for your own), see musync/custom.py for inspiration.

Installation
============

Musync requirements
-------------------

* At least Python 2.6
* Python mutagen >= 1.16 (http://pypi.python.org/pypi/mutagen/)

Commands
--------

Execute the normal python install command (as root):

    sudo python setup.py

Copy the following files to **/etc**

    sudo cp share/musync.rules share/musync.conf /etc/

Modify the following line to fit your needs
Profit

Try out musync on one of your mp3's

  musync inspect test.mp3

To find out more, type:

  musync help
