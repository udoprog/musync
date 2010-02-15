import subprocess as sp
import hashlib

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
    f = open(target, "r")
    
    m = hashlib.md5();
    
    while True:
        s = f.read(2**14)
        
        if not s:
            return m.digest();
        
        m.update(s);

def escapeunicode(text):
    """
    Do not allow _any_ unicode characters to pass by here.
    """
    if type(text) != unicode:
        d_text = str(text).decode("utf-8");
    else:
        d_text = text;
    
    buildstr = list();
    
    for c in d_text:
        if ord(c) > 127:
            buildstr.append("U+{0}".format(hex(ord(c))[2:].upper()));
        else:
            buildstr.append(c);
    
    return "".join(buildstr).encode("ascii");

