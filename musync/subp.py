#
# Musync subprocess - A few nifty subprocessing hacks.
#
# Yes, this enables the program to simplify interprocessing.
#
# author: John-John Tedro <pentropia@gmail.com>
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

from musync.opts import Settings;
import subprocess as sp;
from musync.errors import WarningException, FatalException;
import musync.printer as Printer;

def filter_with(str, field):
    filter_cmd = Settings["filter-with"].split(' ');
    filter_cmd = [ x%{'field': field} for x in filter_cmd ];
    return safe_child(sc_filter_with, [filter_cmd, str]);

def sc_filter_with(args):
    proc = sp.Popen( args[0], stdin=sp.PIPE, stdout=sp.PIPE );
    proc.stdin.write( args[1] );
    proc.stdin.close();
    filter_data = proc.stdout.read();
    state = proc.wait();
    return (state,filter_data);

def transcode_with(cmd, source, dest):
    trans_cmd = cmd.split(' ');
    trans_cmd = [x%{ 'source': source, 'dest': dest} for x in trans_cmd];
    return safe_child(sc_trans_with, trans_cmd);

def sc_trans_with(args):
    proc = sp.Popen(args);
    state = proc.wait();
    return (state, state);

def add_with( source_file, destination_file ):
    add_cmd = Settings["add-with"].split(' ');
    add_cmd = [ x%{ 'source': source_file, 'dest': destination_file } for x in add_cmd ];
    return safe_child(sc_add_with,add_cmd);

def sc_add_with(args):
    proc = sp.Popen( args );
    state = proc.wait();
    return (state, state);

def rm_with(target):
    rm_cmd = Settings["rm-with"].split(' ');
    rm_cmd = [ x%{ 'target': target } for x in rm_cmd ];
    return safe_child(sc_rm_with, rm_cmd);

def sc_rm_with(args):
    proc = sp.Popen( args );
    state = proc.wait();
    return (state, state);

def hash_with(target):
    hash_cmd = Settings["hash-with"].split(' ');
    hash_cmd = [ x%{ 'target': target } for x in hash_cmd ];
    return safe_child(sc_hash_with, hash_cmd);

def sc_hash_with(args):
    proc = sp.Popen(args, stdin=None, stdout=sp.PIPE);
    hash_data = proc.stdout.read();
    proc.stdout.close();
    state = proc.wait();
    return (state, hash_data.split(' ')[0]);

def safe_child(call, args):
    """
    Ok, this is officially the weirdest thing ive ever done in python.
    Now, simple enough, if anything goes wrong with the call, we wan't to try again,
    claiming that the process has been 'shaked'. This is to make sure the main process
    signals doesn't flow over to the subprocess as is default behavior.
    
    Practically this means the subprocess ignores an interrupt by retrying.

    This really is a problem when python relays interrupts at a bad timing to the child process.
    """
    #Utilise the supprocessing module
    state = 1;
    i = 0;
    ret = None;
    while True:
        if i > 0:
            raise FatalException("child process failed to many times");

        try:
            (state, ret) = call(args);
        except Exception, e:
            print e;
            state = 1;
        
        if state != 0:
            Printer.warning( "shaked process" );
            i += 1;
            continue;

        break;
    return ret;

def utf162ascii(text):
    """
    Create pure ascii strings from utf-16 strings with escaped to long chars.
    """
    safe_text = "";
    i = 0;
    while i < len( text ):
        first = ord( text[i] );
        second = ord( text[i+1] );

        if first is 0 and second <= 127:
            safe_text += chr( second );
        else:
            safe_text += str( hex( first ) ) + str( hex( second ) );

        i += 2;

    return safe_text;

def sanitize_with_filter(text, field):
    """
        remove none-filename-ish characters from strings.
        Check configuration to change this behaviour.
    """
    
    all = "";
    i = 0;
    back = None;
    for c in text.encode( "utf-16" ):
        if i < 2:
            i += 1;
            continue;
        if i % 2 is 0:
            back = ord(c);
        else:
            all += chr( ord(c) );
            all += chr( back );
        i += 1;
    
    filter_text = filter_with(all, field);
    
    safe_text = "";
    next = False;
    prev = 0;
    
    # Since we are working with 2-byte per char strings, it must always be possible to divide the strings without rest with 2
    if len( filter_text ) % 2 is not 0:
        raise FatalException( "musync.filter corrupted string" );
    
    safe_text = utf162ascii( filter_text );
    return safe_text;
