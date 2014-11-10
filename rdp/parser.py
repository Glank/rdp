# -*- coding: latin-1 -*-

from grammar import *
from streams import ParsingStream
from itertools import ifilter
import traceback

def build_tree(parent, offset, grammar, dec_list):
    rule = grammar.rules[dec_list[offset]]
    delta = 1
    node = ParseNode(rule.head)
    for s in rule.tail:
        if s.is_terminal():
            child = ParseNode(s)
            node.add(child)
        else:
            delta+= build_tree(
                node, offset+delta, grammar, dec_list
            )
    if parent is None:
        return node
    else:
        parent.add(node)
        return delta

class Parser:
    def __init__(self, stream, grammar):
        assert(isinstance(stream, ParsingStream))
        self.todo_stack = [(grammar.start,None)]
        self.parsed_stack = []
        self.stream = stream
        self.grammar = grammar
        self.parsed_terminals = 0
        self.debug_out = None
    def __advance__(self):
        if self.debug_out is not None:
            self.debug_out('> '+str(self)+'\n')
            self.debug_out(str(self.get_generation_lists()[1])+'\n')
            self.debug_out(str(self.stream.get_buffer())+'\n')
        if not self.todo_stack:
            return False
        symbol, args = self.todo_stack.pop()
        if symbol.is_terminal():
            advanced = self.__advance_terminal__(symbol, args)
        else:
            advanced = self.__advance_nonterminal__(symbol, args)
            if not advanced:
                args = None
        if not advanced:
            self.todo_stack.append((symbol, args))
        return advanced
    def __advance_terminal__(self, terminal, args):
        if args is None:
            consume = terminal.try_consume(self.stream)
            if consume is False:
                return False
            consume = iter(consume)
            n,i = 0,None
        else:
            n,i,consume = args
        try:
            #self.stream.backtrack(n)
            n,i = consume.next()
            self.stream.advance(n)
            self.parsed_stack.append((terminal, (n,i,consume)))
            if args is None:
                self.parsed_terminals+=1
            return True
        except StopIteration:
            self.parsed_terminals-=1
            self.todo_stack.append((terminal, (n,i,consume)))
            return self.__backtrack__()
    def __advance_nonterminal__(self, head, rule_index):
        if rule_index is None:
            rule_index = -1
        rule_index+=1
        rules = self.grammar.rules_by_head(head)
        if rule_index>=len(rules):
            return False
        rule = rules[rule_index]
        self.parsed_stack.append((head, rule_index))
        for symbol in reversed(rule.tail):
            self.todo_stack.append((symbol, None))
        return True
    def __backtrack__(self):
        if self.debug_out is not None:
            self.debug_out('< '+str(self)+'\n')
            self.debug_out(str(self.get_generation_lists()[1])+'\n')
            self.debug_out(str(self.stream.get_buffer())+'\n')
        if not self.parsed_stack:
            return False
        symbol, args = self.parsed_stack.pop()
        if symbol.is_terminal():
            n,i,consume = args
            self.stream.backtrack(n)
        else:
            rules = self.grammar.rules_by_head(symbol)
            rule = rules[args]
            assert(len(rule.tail)>0)
            del self.todo_stack[-len(rule.tail):]
            #reset terminals
            def reset(symbol, arg):
                if symbol.is_terminal():
                    return symbol,None
                return symbol,arg
            self.todo_stack = [reset(*n) for n in self.todo_stack]
        self.todo_stack.append((symbol,args))
        return True
    def __iterate__(self):
        if not self.__advance__():
            return self.__backtrack__()
        return True
    def parse_all(self):
        """An iterater that yields this parser for each possible 
        interpretation under the grammar."""
        while True:
            while self.todo_stack:
                if not self.__iterate__():
                    return
            yield self
            assert(self.__iterate__())
    def parse_filtered(self, is_match):
        """Returns true if a parse state that fits is_match is reached.
        is_match should be a function or lambda that this parser
        and returns True for valid matches and False for invalid ones.
        This is useful for parsing mildly context-sensitive grammars.
        """
        for this in self.parse_all():
            if is_match(this):
                return True
        return False
    def parse_partial(self):
        try:
            iter(self.parse_all()).next()
            return True
        except StopIteration:
            return False
    def parse_full(self):
        return self.parse_filtered(
            is_match=lambda s:s.stream.finished())
    def get_generation_lists(self):
        decision_list = []
        term_instances = []
        term_ranges = []
        i = 0
        for symbol, args in self.parsed_stack:
            if symbol.is_terminal():
                if args[1] is not None:
                    ni = i+args[0]
                    term_instances.append(args[1])
                    term_ranges.append((i,ni))
                    i=ni
            else:
                rule = self.grammar.rules_by_head(symbol)[args]
                decision_list.append(self.grammar.index(rule))
        return decision_list, term_instances, term_ranges
    def __str__(self):
        def tostr(a,b):
            if b is None:
                return '(%s,-)'%str(a)
            if a.is_terminal():
                return '(%s,%d)'%(str(a),b[0])
            else:
                return '(%s,%d)'%(str(a),b)
        ret = "["+",".join(tostr(*t) for t in self.todo_stack)+"] "
        ret+= "["+",".join(tostr(*t) for t in self.parsed_stack)+"] "
        ret+= str(self.stream.index)
        return ret
    def to_parse_tree(self, expand_complex=True):
        decs, terms, ranges = self.get_generation_lists()
        grammar = self.grammar
        if self.grammar.parent is not None:
            grammar = self.grammar.parent
            decs = self.grammar.transform_to_parent(decs)    
        ret = build_tree(None, 0, grammar, decs)
        off = 0
        for node in list(ret.nonepsilon_terms()):
            node.instance = terms[off]
            node.range = ranges[off]
            if node.symbol.is_complex() and expand_complex:
                node.expand()
            off+=1
        return ret
    def __repr__(self):
        return 'Parser(?)'

class ParseNode:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []
        self.parent = None
        #used if terminal
        self.instance = None
        self.range = None
        #used if not terminal
        self.prev = None
        self.next = None
    def iter_nodes(self, pfilter=None):
        if pfilter is not None and not pfilter(self):
            return
        yield self
        for child in self.children:
            for node in child.iter_nodes(pfilter=pfilter):
                yield node
    def find_node(self, match_funct):
        for node in self.iter_nodes():
            if match_funct(node):
                return node
    def nonepsilon_terms(self):
        e = Epsilon()
        def net(n):
            if n.children:
                return False
            return n.symbol!=e
        return ifilter(net, self.iter_nodes())
    def expand(self):
        assert(self.symbol.is_complex())
        subtree = self.instance.to_parse_tree()
        self.children = subtree.children
        for c in self.children:
            c.parent = self
    def add(self, child):
        assert(not self.symbol.is_terminal())
        assert(isinstance(child, ParseNode))
        self.children.append(child)
        child.parent = self
    def __str__(self, depth=0):
        ret = '  '*depth
        ret+= str(self.symbol)
        if not self.children and self.instance is not None:
            ret+=':'+str(self.instance)
        for child in self.children:
            ret+='\n'+child.__str__(depth=depth+1)
        return ret
