# -*- coding: latin-1 -*-

from grammar import *
from streams import ParsingStream

class Parser:
    def __init__(self, stream, grammar):
        assert(isinstance(stream, ParsingStream))
        self.todo_stack = [(grammar.start,None)]
        self.parsed_stack = []
        self.stream = stream
        self.grammar = grammar
        self.parsed_terminals = 0
        self.verbose = False
    def __advance__(self):
        if self.verbose:
            print '>',self
        if not self.todo_stack:
            return False
        symbol, args = self.todo_stack.pop()
        if symbol.is_terminal():
            advanced = self.__advance_terminal__(symbol, args)
        else:
            advanced = self.__advance_nonterminal__(symbol, args)
        if not advanced:
            self.todo_stack.append((symbol, args))
        return advanced
    def __advance_terminal__(self, terminal, args):
        if args is None:
            consume = terminal.try_consume(self.stream)
            if consume is False:
                return False
            consume = iter(consume)
            n,i = consume.next()
            self.stream.advance(n)
            self.parsed_stack.append((terminal, (n,i,consume)))
            self.parsed_terminals+=1
            return True
        else:
            try:
                n,i,consume = args
                self.stream.backtrack(n)
                n,i = consume.next()
                self.stream.advance(n)
                self.parsed_stack.append((terminal, (n,i,consume)))
                return True
            except StopIteration:
                self.parsed_terminals-=1
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
        if self.verbose:
            print '<',self
        if not self.parsed_stack:
            return False
        symbol, args = self.parsed_stack.pop()
        if not symbol.is_terminal():
            rules = self.grammar.rules_by_head(symbol)
            rule = rules[args]
            assert(len(rule.tail)>0)
            del self.todo_stack[-len(rule.tail):]
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
            if not self.__iterate__():
                return
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
        for symbol, args in self.parsed_stack:
            if symbol.is_terminal():
                term_instances.append(args[1])
            else:
                rule = self.grammar.rules_by_head(symbol)[args]
                decision_list.append(self.grammar.index(rule))
        return decision_list, term_instances
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
    def __build_tree__(self, parent, dec_off, term_off, grammar, 
        dec_list, term_list):
        rule = grammar.rules[dec_list[dec_off]]
        dec_delta = 1
        term_delta = 0
        node = ParseNode(rule.head)
        for s in rule.tail:
            if s.is_terminal():
                child = ParseNode(s, term_list[term_off+term_delta])
                node.add(child)
                term_delta+=1
            else:
                dd,td = self.__build_tree__(
                    node, dec_off+dec_delta, term_off+term_delta,
                    grammar, dec_list, term_list
                )
                dec_delta+=dd
                term_delta+=td
        if parent is None:
            return node
        else:
            parent.add(node)
            return dec_delta, term_delta
    def to_parse_tree(self):
        decs, terms = self.get_generation_lists()
        grammar = self.grammar
        if self.grammar.parent is not None:
            grammar = self.grammar.parent
            decs = self.grammar.transform_to_parent(decs)    
        ret = self.__build_tree__(None, 0, 0, grammar, decs, terms)
        return ret

class ParseNode:
    def __init__(self, symbol, instance=None):
        self.symbol = symbol
        if instance is not None:
            assert(symbol.is_terminal())
        self.instance = instance
        if self.symbol.is_complex():
            subtree = instance.to_parse_tree()
            self.children = subtree.children
        else:
            self.children = []
    def add(self, child):
        assert(isinstance(child, ParseNode))
        self.children.append(child)
    def __str__(self, depth=0):
        ret = '  '*depth
        ret+= str(self.symbol)
        if not self.children and self.instance is not None:
            ret+=':'+str(self.instance)
        for child in self.children:
            ret+='\n'+child.__str__(depth=depth+1)
        return ret
