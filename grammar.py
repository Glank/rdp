#!/usr/bin/python
# -*- coding: latin-1 -*-

from finite_graph import DirectedGraph
class ParsingStream:
    def __init__(self, elems):
        self.elems = elems
        self.index = 0
        self.stack = []
    def has_next(self):
        return self.index<len(self.elems)
    def peek(self):
        return self.elems[self.index]
    def pop(self):
        self.index+=1
        return self.elems[self.index-1]
    def mark(self):
        self.stack.append(self.index)
    def revert(self):
        assert(self.stack)
        self.index = self.stack.pop()

class Symbol:
    def __init__(self, name):
        self.name = name
    def is_terminal(self):
        return isinstance(self, TerminalSymbol)
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return self.name == other.name
    def __repr__(self):
        return 'Symbol(%r)'%self.name
    def __str__(self):
        return self.name

class TerminalSymbol(Symbol):
    def __init__(self, name):
        Symbol.__init__(self, name)
    def try_consume(self, stream):
        raise NotImplementedError()
    def __repr__(self):
        return 'TerminalSymbol(%r)'%self.name
    def __str__(self):
        return "'%s'"%self.name

class Epsilon(TerminalSymbol):
    def __init__(self):
        Symbol.__init__(self, '__epsilon__')
    def try_consume(self, stream):
        return True
    def __repr__(self):
        return "Epsilon()"
    def __str__(self):
        return "ε"

class Rule:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        assert(isinstance(head, Symbol))
        assert(not head.is_terminal())
        assert(isinstance(tail, list))
        assert(bool(tail))
        for symbol in self.tail:
            assert(isinstance(symbol, Symbol))
            if symbol==Epsilon():
                assert (len(self.tail)==1)
    def __str__(self):
        ret = "%s -> "%str(self.head)
        ret+= " ".join(str(n) for n in self.tail)
        return ret

class Grammar:
    def __init__(self, rules):
        self.rules = rules
        assert(isinstance(rules, list))
        self.rules_by_head = {}
        for rule in self.rules:
            assert(isinstance(rule, Rule))
            head = rule.head
            rules_for = self.rules_by_head.get(head, [])
            rules_for.append(rule)
            self.rules_by_head[head] = rules_for
    def is_parseable(self):
        pdg = DirectedGraph() #parse decision graph
        for rule in self.rules:
            a,b = rule.head, rule.tail[0]
            pdg.add_vertex(a)
            pdg.add_vertex(b)
            pdg.add_edge(a,b)
        if pdg.is_cyclic():
            return False
        for leaf in pdg.leaves():
            if not leaf.is_terminal():
                return False
        return True
    def __str__(self):
        return '\n'.join(str(r) for r in self.rules)

if __name__=='__main__':
    s = Symbol('S')
    a = Symbol('a')
    b = Symbol('b')
    c = TerminalSymbol('c')
    d = TerminalSymbol('d')
    rules = [
        Rule(s, [a,b]),
        Rule(a, [s]),
        Rule(a, [c]),
        Rule(b, [Epsilon()]),
        Rule(b, [d,a]),
    ]
    gram = Grammar(rules)
    print gram
    print gram.is_parseable()
