"""
Custom library for lambda expressions.
These functions are automatically imported into the 'm' module.
"""

import subprocess as sp
import hashlib
import rulelexer
import types
import collections
import tempfile
import os

def system(*args, **kw):
    """
    spawn a command and return value as boolean.
    """
    return sp.Popen(args, **kw).wait() == 0;

def execute(*args, **kw):
    """
    spawn a command and return value as boolean.
    """
    kw["stdout"] = sp.PIPE;
    
    # spawn
    proc = sp.Popen(args, **kw);
    
    # I/O
    data = proc.stdout.read();
    proc.stdout.close();
    
    # only return data on returncode == 0
    if proc.wait() == 0:
        return data;
    
    return "";

def filter(data, *args, **kw):
    """
    spawn a command and return value as boolean.
    """
    if data is None:
        return "";
    
    kw["stdin"] = sp.PIPE;
    kw["stdout"] = sp.PIPE;
    
    # spawn
    proc = sp.Popen(args, **kw);
    
    # I/O
    proc.stdin.write(data.encode("utf-8"));
    proc.stdin.close();
    data = proc.stdout.read();
    proc.stdout.close();
    
    # only return data on returncode == 0
    if proc.wait() == 0:
        return data;
    
    return "";

def md5sum(target):
    """

    """
    
    if target is None:
        return None;
    
    try:
        f = open(target, "r")
    except OSError, e:
        return None;
    
    m = hashlib.md5();
    
    while True:
        s = f.read(2**14)
        
        if not s:
            return m.digest();
        
        m.update(s);

def ue(text):
    """
    Do not allow _any_ unicode characters to pass by here.
    """
    if text is None:
        return None;
    
    if type(text) != unicode:
        d_text = str(text).decode("utf-8");
    else:
        d_text = text;
    
    buildstr = list();
    
    for c in d_text:
        if ord(c) > 127:
            buildstr.append("{0}".format(hex(ord(c))[2:].upper()));
        else:
            buildstr.append(c);
    
    return "".join(buildstr).encode("ascii");

cached_books = dict();

def lexer(rb, string):
    global cached_books;
    
    if rb in cached_books:
        return cached_books[rb].match(string);
    
    lexer = rulelexer.RuleLexer();
    lexer.lex(rulelexer.FileReader(open(rb, "r")));

    if len(lexer.errors) > 0:
        for error in lexer.errors:
            (line, col), message =  error;
            print(rb + ":" + str(line) + ":" + str(col), message);
    
    cached_books[rb] = rulelexer.RuleBook(lexer);
    return cached_books[rb].match(string);

def inspect(o):
    print "inspection:", type(o), repr(o);
    return o;

def case(mv, *args, **kw):
    """
    Match a value against a set of cases.

    The following matchmethods are available:

    case('foo', bar="result1", foo="result2") -> "result"
    case('foo', ('bar', "result1"), ('foo', "result2")) -> "result2"
    case('foo', (('bar', 'baz'), "result1"), (('foo', 'biz'), "result2")) -> "result2"

    The match does not have to be a string:

    case(2, (1, "result1"), (2, "result2")) -> "result2"
    """
    for a in args:
        if not isinstance(a, tuple) and len(a) != 2:
            continue;
        
        kv, v = a;
        
        if isinstance(kv, collections.Sequence):
            if mv in kv:
                return v;
        elif mv == kv:
            return v;
    
    # match a kw
    return kw.get(str(mv), kw.get('_', None));

def each(*args):
    """
    Run each argument if a FunctionType, in successive order.
    Stop running on the first function to return false.
    """
    for a in args:
        if type(a) != types.FunctionType:
            continue;
        
        if not a():
            return False;
    
    return True;

def in_tmp(func, *args, **kw):
    """
    Create a temporary file, use it as the first argument to a function, transparently also pass the other arguments.
    
    empty function: in_tmp(lambda tmp: ... ) 
    Function with arguments: in_tmp(lambda tmp, foo: ... , "foo")
    """
    if type(func) != types.FunctionType:
        return None;
    
    fo, tmp=tempfile.mkstemp();
    os.close(fo);
    
    try:
        return func(tmp, *args, **kw);
    finally:
        os.unlink(tmp);

def safecopy(src, dst, hasher=None):
    import shutil;

    parity = None;

    if hasher is not None:
        parity = hasher(src);
    
    shutil.copy(src, dst);
    
    if hasher is not None:
        return hasher(dst) == parity;
    
    return True;

__all__ = ["ue", "case", "inspect", "each", "in_tmp"]
