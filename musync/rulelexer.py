# -*- encoding: utf-8 -*-

import re;

class Reader:
  def __init__(self, ignore=list()):
    self._current = None;
    self._ignore = ignore;
    self._pos = 0;
    self._empty = False;
  
  def next(self):
    if self.empty():
      return None;
    
    while True:
      self._current = self._get_next();

      if self._current is None:
        self._empty = True;
        break;
      
      self._pos += 1;
      
      if self._current in self._ignore:
        continue;
      
      break;
    
    return self._current;
  
  def empty(self):
    return self._empty;
  
  def pos(self):
    return self._pos;
  
  def current(self):
    return self._current;

class StringReader(Reader):
  def __init__(self, string, **kw):
    Reader.__init__(self, **kw);
    self._iterstring = iter(string);
  
  def _get_next(self):
    try:
      return self._iterstring.next();
    except StopIteration:
      return None;

class FileReader(Reader):
  def __init__(self, fileobject, **kw):
    Reader.__init__(self, **kw);
    self._fileobject = fileobject;

  def _get_next(self):
    r = self._fileobject.read(1);

    if r is None or r == "":
      return None;

    return r;

class RuleLexer:
  """
  This is a fake lexer/parser to handle the simple syntax for unicode rule replacement.
  """
  REGEXP='s'
  UNICODE='u'

  COMMANDS=[REGEXP, UNICODE];
  
  unicode_token = re.compile("^U?\+?([A-Fa-f0-9]+)$");
  unicodegroup_token = re.compile("^U?\+?([A-Fa-f0-9]+)-U?\+?([A-Fa-f0-9]+)$");
  
  def __init__(self):
    self.tree = list();
    self.errors = list();
    self._line = 0;
  
  def lex(self, reader):
    while not reader.empty():
      line = list();
      
      while reader.next() != '\n':
        if reader.current() is None:
          break;
        
        if reader.current() == "#":
          while reader.next() != '\n':
            pass;
          break;
        
        line.append(reader.current());

      self._line += 1;
      
      ok, pos, message = self.lexrule(''.join(line).strip());
      
      if ok is None:
        continue;
      
      if not ok:
        self.errors.append(((self._line, pos), message));
  
  def lexrule(self, line=None):
    reader = StringReader(line);
    
    #check first character
    if reader.next() not in self.COMMANDS:
      if reader.current() is None:
        return (None, -1, "blank line");
      else:
        return (False, reader.pos(), "invalid syntax: '" + reader.current() + "' is not a valid command");
    
    command = reader.current();
    
    if reader.next() is None:
      return (False, reader.pos(), "invalid syntax: unexpected end of line");

    sep = reader.current();

    rule = list();
    while reader.next() != sep:
      if reader.current() is None:
        return (False, reader.pos(), "invalid syntax: expected separator '" + sep + "'")
      rule.append(reader.current());
    
    rule = ''.join(rule);
    
    if command == self.UNICODE:
      groups = rule.split(",");
      rule = list();
      
      for i, group in enumerate(groups):
        group = group.strip();

        if group == "":
          # no harm in silently ignoring this
          continue;
        
        m = self.unicode_token.match(group)
        if m is not None:
          rule.append(long(m.group(1), 16));
          continue;
        
        m = self.unicodegroup_token.match(group)
        if m is not None:
          rule.append((long(m.group(1), 16), long(m.group(2), 16)));
          continue;
        
        return (False, reader.pos(), "invalid syntax: could not match rule number " + str(i));
    elif command == self.REGEXP:
      try:
        rule = re.compile(rule);
      except Exception, e:
        return (False, reader.pos(), "invalid syntax: " + str(e))
    
    repl = list();
    while reader.next() != sep:
      # implicit end
      if reader.current() is None:
        break;
      
      repl.append(reader.current());
    
    self.tree.append((command, rule, ''.join(repl)));
    return (True, -1, None);

class RuleBook:
  def __init__(self, lexer, **kw):
    self.kw = kw;
    
    self.lexer = lexer;
    self.charrules = list();
    self.chardict = dict();
    self.stringrules = list();
    
    def create_unicoderule(ruleset, to_c):
      res = dict();
      for rule in ruleset:
        if type(rule) == long:
          res[rule] = to_c;
        else:
          fromc, toc = rule;
          for i in range(fromc, toc + 1):
            res[i] = to_c;
      return res;
    
    for rule in lexer.tree:
      if rule[0] == RuleLexer.REGEXP:
        self.stringrules.append((rule[1], rule[2]));
      elif rule[0] == RuleLexer.UNICODE:
        self.chardict.update(create_unicoderule(rule[1], rule[2]));
  
  def match(self, string):
    res = list();
    
    for c in string:
      res.append(self.chardict.get(ord(c), c));
    
    # string pass;
    string = ''.join(res);
    
    for regex, repl in self.stringrules:
      string = regex.sub(repl, string);
    
    return string;

if __name__ == "__main__":
  import sys
  lexer = RuleLexer();
  assert lexer.lexrule(u'u_U+63-U+64,U+65_a_') == (True, -1, None);
  rulebook = RuleBook(lexer)
  print lexer.tree
  #print rulebook.rules[0].root.group[1].matchc
  print rulebook.match("cest")
  sys.exit(0)

  print lexer.tree
  
  lexer2 = RuleLexer();
  lexer2.lex(StringReader("""
s_U+30_å_
r/_/_/
  """))
  
  print lexer2.tree;
  print lexer2.errors
  
  lexer3 = RuleLexer();
  lexer3.lex(FileReader(open("test.txt", "r")))
  
  rulebook = RuleBook(lexer3)
  print rulebook.match(u'testeGÅ');
