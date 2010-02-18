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
  REGEXP='s'
  SINGLE='u'
  GROUP='g'

  COMMANDS=[REGEXP, GROUP, SINGLE];
  
  unicode_token = re.compile("^U\+([A-Fa-f0-9]+)$");
  unicodegroup_token = re.compile("^U\+([A-Fa-f0-9]+)-U\+([A-Fa-f0-9]+)$");
  
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
    
    if command == self.SINGLE:
      m = self.unicode_token.match(''.join(rule))
      if m is None: return (False, reader.pos(), "invalid syntax: rule is not a valid unicode token")
      rule = long(m.group(1), 16);
    elif command == self.GROUP:
      m = self.unicodegroup_token.match(''.join(rule))
      if m is None: return (False, reader.pos(), "invalid syntax: rule is not a valid unicode group token")
      rule = (long(m.group(1), 16), long(m.group(2), 16));
    elif command == self.REGEXP:
      try:
        rule = re.compile(''.join(rule));
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

class Rule:
  def __init__(self, **kw):
    self.debug = kw.pop("debug", False);

  def match(self, string):
    return [string];

class RegexpRule(Rule):
  def __init__(self, reobj, repl, **kw):
    Rule.__init__(self, **kw)
    self.reobj = reobj;
    self.repl = repl;
  
  def match(self, string):
    return self.reobj.sub(self.repl, string);

class SingleRule(Rule):
  def __init__(self, fr, to, **kw):
    Rule.__init__(self, **kw)
    self.fr = fr;
    self.to = to;

  def match(self, string, **kw):
    res = list();
    for c in iter(string):
      if ord(c) == self.fr:
        res.append(self.to);
      else:
        res.append(c);
    return ''.join(res);

class GroupRule(Rule):
  def __init__(self, frrange, to, **kw):
    Rule.__init__(self, **kw)
    self.frb, self.fre = frrange;
    self.to = to;
  
  def match(self, string):
    res = list();
    
    for c in iter(string):
      o = ord(c);
      if o >= self.frb and o <= self.fre:
        res.append(self.to);
      else:
        res.append(c);
    
    return ''.join(res);

class RuleBook:
  def __init__(self, lexer, **kw):
    self.kw = kw;
    
    self.lexer = lexer;
    self.rules = list();
    
    for rule in lexer.tree:
      if rule[0] == RuleLexer.REGEXP:
        self.rules.append(RegexpRule(rule[1], rule[2], **kw));
      elif rule[0] == RuleLexer.SINGLE:
        self.rules.append(SingleRule(rule[1], rule[2], **kw));
      elif rule[0] == RuleLexer.GROUP:
        self.rules.append(GroupRule(rule[1], rule[2], **kw));
  
  def match(self, string):
    for rule in self.rules:
      string = rule.match(string);
    return string;

if __name__ == "__main__":
  lexer = RuleLexer();
  assert lexer.lexrule(u's_U+30_å_\n') == (True, -1, None);
  assert lexer.lexrule(u'g_U+30-U+31_\n') == (True, -1, None);
  assert lexer.lexrule(u'r_([a-z])+_\n') == (True, -1, None);

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
