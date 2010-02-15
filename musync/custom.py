import subprocess as sp

def system(*args, **kw):
    """
    spawn a command and return value as boolean.
    """
    return sp.Popen(args, **kw).wait();

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
