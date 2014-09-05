# -*- coding: latin-1 -*-

from grammar import *
from streams import ParsingStream

class RDParser:
    def __init__(self, stream, grammar):
        assert(isinstance(stream, ParsingStream))
        self.todo_stack = [(grammar.start,None)]
        self.parsed_stack = []
        self.stream = stream
        self.grammar = grammar
        self.parsed_terminals = 0
    def __advance__(self):
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
            n = consume.next()
            self.stream.advance(n)
            self.parsed_stack.append((terminal, (n,consume)))
            self.parsed_terminals+=1
            return True
        else:
            try:
                n,consume = args
                self.stream.backtrack(n)
                n = consume.next()
                self.stream.advance(n)
                self.parsed_stack.append((terminal, (n,consume)))
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
        if not self.parsed_stack:
            return False
        self.todo_stack.append(self.parsed_stack.pop())
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
        return self.parse_filtered(is_match=lambda s:s.stream.finished())
    def get_generation_lists(self):
        decision_list = []
        term_instances = []
        self.stream.reset()
        for symbol, args in self.parsed_stack:
            if symbol.is_terminal():
                term_instances.append(self.stream.advance(args[0]))
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
