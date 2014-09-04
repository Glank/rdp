# -*- coding: latin-1 -*-

from finite_graph import DirectedGraph

class Symbol:
    def __init__(self, name):
        self.name = name
    def is_terminal(self):
        return isinstance(self, TerminalSymbol)
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return self.name == other.name
    def __ne__(self, other):
        return not self == other
    def __repr__(self):
        return 'Symbol(%r)'%self.name
    def __str__(self):
        return self.name

class TerminalSymbol(Symbol):
    def __init__(self, name):
        Symbol.__init__(self, name)
    def try_consume(self, stream):
        """Tries to consume self from the stream, returns
        False if not consumed or the number of elements from
        the stream consumed (any non-negative) and advances
        the stream's index."""
        raise NotImplementedError()
    def __repr__(self):
        return 'TerminalSymbol(%r)'%self.name
    def __str__(self):
        return "'%s'"%self.name

class Epsilon(TerminalSymbol):
    def __init__(self):
        Symbol.__init__(self, '__epsilon__')
    def try_consume(self, stream):
        return 0
    def __repr__(self):
        return "Epsilon()"
    def __str__(self):
        return "ε"

class Rule:
    def __init__(self, head, tail):
        self.head = head
        self.tail = [t for t in tail if t!=Epsilon()]
        if not self.tail:
            self.tail = [Epsilon()]
        assert(isinstance(head, Symbol))
        assert(not head.is_terminal())
        assert(isinstance(tail, list))
        for symbol in self.tail:
            assert(isinstance(symbol, Symbol))
            if symbol==Epsilon():
                assert (len(self.tail)==1)
        self.__h__= hash(tuple([self.head]+self.tail))
    def __str__(self):
        ret = "%s -> "%str(self.head)
        ret+= " ".join(str(n) for n in self.tail)
        return ret
    def is_left_recursive(self):
        return self.tail[0]==self.head
    def unique_symbols(self):
        yield self.head
        returned = set([self.head])
        for s in self.tail:
            if s not in returned:
                yield s
                returned.add(s)
    def __eq__(self, other):
        if not self.head==other.head:
            return False
        if not len(self.tail)==len(other.tail):
            return False
        for a,b in zip(self.tail, other.tail):
            if not a==b:
                return False
        return True
    def __ne__(self, other):
        return not self == other
    def __hash__(self):
        return self.__h__

class Grammar:
    def __init__(self, rules=None, start=Symbol('S')):
        self.start = start
        if rules is None:
            rules = []
        self.rules = rules[:]
        self.rules_by_head_map = None
        self.reverse_lookup_map = None
        assert(isinstance(rules, list))
    def add(self, rule):
        if rule not in self.rules:
            self.rules.append(rule)
    def remove(self, rule):
        self.rules.remove(rule)
    def index(self, rule):
        if self.reverse_lookup_map is None:
            return self.rules.index(rule)
        return self.reverse_lookup_map[rule]
    def is_parseable(self, with_manipulation=False):
        pdg = DirectedGraph() #parse decision graph
        for rule in self.rules:
            a,b = rule.head, rule.tail[0]
            pdg.add_vertex(a)
            pdg.add_vertex(b)
            pdg.add_edge(a,b)
        if not with_manipulation:
            if pdg.is_cyclic():
                return False
        for leaf in pdg.leaves():
            if not leaf.is_terminal():
                return False
        return True
    def rules_by_head(self, head):
        if self.rules_by_head_map is not None:
            return self.rules_by_head_map[head]
        return [r for r in self.rules if r.head==head]
    def unique_symbols(self):
        returned = set()
        for rule in self.rules:
            for s in rule.unique_symbols():
                if s not in returned:
                    yield s
                    returned.add(s)
    def __gen_nonterminal__(self, prefix=''):
        i = 0
        unique = set(self.unique_symbols())
        nt = Symbol('_%s%d'%(prefix,i))
        while nt in unique:
            i+=1
            nt = Symbol('_%s%d'%(prefix,i))
        return nt
    def __factor__(self, head):
        rules = self.rules_by_head(head)
        if len(rules)<=1:
            return False
        common_prefix = rules[0].tail[:]
        for rule in rules[1:]:
            i = 0
            end = min(len(common_prefix), len(rule.tail))
            while i<end and common_prefix[i]==rule.tail[i]:
                i+=1
            del common_prefix[i:]
        if common_prefix:
            end = len(common_prefix)
            z = self.__gen_nonterminal__()
            self.add(Rule(head, common_prefix+[z]))
            for rule in rules:
                self.remove(rule)
                self.add(Rule(z, rule.tail[end:]))
            return True
        return False
    def try_factoring(self):
        factored = 0
        for symbol in self.unique_symbols():
            if not symbol.is_terminal():
                if self.__factor__(symbol):
                    factored+= 1
        return factored
    def __substitute__(self, rule):
        a,b,alpha = rule.head, rule.tail[0], rule.tail[1:]
        if b.is_terminal():
            return False
        if not alpha:
            return False
        betas = [r.tail for r in self.rules_by_head(b)]
        if not betas:
            return False
        self.remove(rule)
        for beta in betas:
            self.add(Rule(a,beta+alpha))
        return True
    def try_substituting(self):
        for rule in self.rules:
            if self.__substitute__(rule):
                return 1
        return 0
    def try_removing_useless_rules(self):
        gen_graph = DirectedGraph()
        for rule in self.rules:
            for symbol in rule.unique_symbols():
                if not symbol.is_terminal():
                    gen_graph.add_vertex(symbol)
            for symbol in rule.tail:
                if not symbol.is_terminal():
                    gen_graph.add_edge(rule.head, symbol)
        removed = 0
        for root in gen_graph.roots():
            if root!=self.start:
                to_del = self.rules_by_head(root)
                for rule in to_del:
                    self.remove(rule)
                    removed+=1
        return removed
    def __remove_left_recursion__(self, head):
        rules = self.rules_by_head(head)
        betas = []
        alphas = []
        for rule in rules:
            if rule.tail[0]==head:
                betas.append(rule.tail[1:])
            else:
                alphas.append(rule.tail)
        if not betas or not alphas:
            return False
        for rule in rules:
            self.remove(rule)
        z = self.__gen_nonterminal__(prefix=head.name)
        self.add(Rule(z, []))       
        for alpha in alphas:
            self.add(Rule(head, alpha+[z]))       
        for beta in betas:
            self.add(Rule(z, beta+[z]))       
        return True
    def try_removing_left_recursion(self):
        removed = 0
        for symbol in list(self.unique_symbols()):
            if not symbol.is_terminal():
                if self.__remove_left_recursion__(symbol):
                    removed+= 1
        return removed
    def try_compiling(self):
        functs = [
            self.try_removing_useless_rules,
            self.try_removing_left_recursion,
            self.try_factoring,
            self.try_substituting,
        ]
        for funct in functs:
            improved = funct()
            if improved>0:
                return improved
        return 0
    def compile_rbhm(self):
        self.rules_by_head_map = {}
        for rule in self.rules:
            corules = self.rules_by_head_map.get(rule.head, [])        
            corules.append(rule)
            self.rules_by_head_map[rule.head] = corules
    def compile_rlm(self):
        self.reverse_lookup_map = {}
        for i, rule in enumerate(self.rules):
            self.reverse_lookup_map[rule] = i
    def compile(self):
        improved = self.try_compiling()
        total = improved
        while improved:
            improved = self.try_compiling()
            total+= improved
        self.compile_rbhm()
        self.compile_rlm()
        return total
    def __str__(self):
        return '\n'.join('%d)\t%s'%(i,str(r)) for i,r in enumerate(self.rules))

