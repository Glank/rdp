# -*- coding: latin-1 -*-

from grammar import *

class ParsingStream:
    def reset(self):
        """Resets the stream to the very beginning."""
        raise NotImplementedError()
    def advance(self, amount):
        """Advances the stream. Returns <amount>
        elements that were passed."""
        raise NotImplementedError()
    def backtrack(self, amount):
        """Goes backwards in the stream <amount> elements.
        Calling s.advance(a) then s.backtrack(a) should
        result in the s being exactly the same."""
        raise NotImplementedError()

class StringStream(ParsingStream):
    def __init__(self, string):
        self.string = string
        self.index = 0
    def has(self, word):
        if (self.index+len(word))>len(self.string):
            return False
        return self.string[self.index:].startswith(word)
    def advance(self, amount):
        self.index+=amount
        assert(self.index<=len(self.string))
        return self.string[self.index-amount:self.index]
    def backtrack(self, amount):  
        self.index-=amount
        assert(self.index>=0)
    def finished(self):
        return self.index==len(self.string)
    def reset(self):
        self.index = 0
    def __str__(self):
        return self.string

class StringTerminal(TerminalSymbol):
    def try_consume(self, stream):
        assert(isinstance(stream, StringStream))
        if stream.has(self.name):
            stream.advance(len(self.name))
            return len(self.name)
        return False

class RDParser:
    def __init__(self, stream, grammar):
        assert(isinstance(stream, ParsingStream))
        self.todo_stack = [(grammar.start,-1)]
        self.parsed_stack = []
        self.stream = stream
        self.grammar = grammar
        self.state = 'unparsed'
    def __advance__(self):
        if not self.todo_stack:
            return False
        head, rule_index = self.todo_stack.pop()
        if head.is_terminal():
            advanced = self.__advance_terminal__(head)
        else:
            advanced = self.__advance_nonterminal__(head, rule_index)
        if not advanced:
            self.todo_stack.append((head, rule_index))
        return advanced
    def __advance_terminal__(self, terminal):
        consumed = terminal.try_consume(self.stream)
        if consumed is False:
            return False
        self.parsed_stack.append((terminal, consumed))
        return True
    def __advance_nonterminal__(self, head, rule_index):
        rule_index+=1
        rules = self.grammar.rules_by_head(head)
        if rule_index>=len(rules):
            return False
        rule = rules[rule_index]
        self.parsed_stack.append((head, rule_index))
        for symbol in reversed(rule.tail):
            self.todo_stack.append((symbol, -1))
        return True
    def __backtrack__(self):
        if not self.parsed_stack:
            return False
        removed = 0
        symbol, arg = self.parsed_stack.pop()
        while symbol.is_terminal():
            removed+=1
            self.stream.backtrack(arg)
            symbol, arg = self.parsed_stack.pop()
        rule = self.grammar.rules_by_head(symbol)[arg]
        for i in xrange(len(rule.tail)-removed):
            self.todo_stack.pop()
        self.todo_stack.append((symbol, arg))
        return True
    def __iterate__(self):
        if not self.__advance__():
            return self.__backtrack__()
        return True
    def parse_partial(self):
        assert(self.state=='unparsed')
        while self.todo_stack:
            if not self.__iterate__():
                self.state = 'invalid'
                return False
        self.state = 'parsed'
        return True
    def parse_full(self):
        return parse_filtered(self, is_match=lambda s:s.stream.finished())
    def parse_filtered(self, is_match):
        """is_match should be a function or lambda that this parser
        and returns True for valid matches and False for invalid ones.
        This is useful for parsing mildly context-sensitive grammars.
        """
        assert(self.state=='unparsed')
        self.state = 'parsing'
        matches = False
        while not matches:
            while self.todo_stack:
                if not self.__iterate__():
                    self.state = 'invalid'
                    return False
            _,terms = self.get_generation_lists()
            matches = is_match(self)
            if not matches and not self.__iterate__():
                self.state = 'invalid'
                return False
        self.state = 'parsed'
        return True
    def get_generation_lists(self):
        assert(self.state=='parsed' or self.state=='parsing')
        decision_list = []
        term_instances = []
        self.stream.reset()
        for symbol, arg in self.parsed_stack:
            if symbol.is_terminal():
                term_instances.append(self.stream.advance(arg))
            else:
                rule = self.grammar.rules_by_head(symbol)[arg]
                decision_list.append(self.grammar.index(rule))
        return decision_list, term_instances
    def __str__(self):
        ret = "["+",".join('(%s,%d)'%(str(a),b) for a,b in self.todo_stack)+"] "
        ret+= "["+",".join('(%s,%d)'%(str(a),b) for a,b in self.parsed_stack)+"] "
        ret+= str(self.stream.index)
        return ret

