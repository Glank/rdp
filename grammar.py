# -*- coding: latin-1 -*-

from finite_graph import DirectedGraph
from copy import deepcopy
from bisect import bisect
from itertools import izip

class Symbol:
    def __init__(self, name):
        self.name = name
    def is_terminal(self):
        return isinstance(self, TerminalSymbol)
    def is_complex(self):
        return isinstance(self, ComplexTerminalSymbol)
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
        """Tests if can consume self from the stream.
        Returns False if not consumable.
        Else, returns an iterable object that yields tuples:
        the stream length and value of each possible 
        interpretation of this terminal and the given 
        the input stream's current position. The iterable
        may store reference to the stream and assume that 
        calls to next(self) will come only at times when the 
        stream is in the same initial position when this
        try_consume method was called."""
        raise NotImplementedError()
    def __repr__(self):
        return 'TerminalSymbol(%r)'%self.name
    def __str__(self):
        return "'%s'"%self.name
    def get_instance(self):
        """Optional: If the grammar is generative, this method should
        return the instance of elements of a parse stream that
        correspond to this terminal."""
        raise NotImplementedError()

class ComplexTerminalSymbol(TerminalSymbol):
    """A ComplexTerminalSymbol is one that returns instances based
    on a subgrammar. This is usefull in defining mildly context
    sensitive grammars. 
    The instance values returned by try_consume for a 
    ComplexTerminalSymbol should be instances of a parser.
    """
    def subgrammar(self):
        """Returns the grammar that this parser uses."""
        raise NotImplementedError()

class Epsilon(TerminalSymbol):
    def __init__(self):
        Symbol.__init__(self, '__epsilon__')
    def try_consume(self, stream):
        return [(0,None)]
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

class DecListTransform:
    def transform(self, dec_list):
        """Takes a decision list, and returns a transformd decision list."""
        raise NotImplementedError()

class Unfactor(DecListTransform):
    def __init__(self, added_index):
        #assumes added_index is the max index
        self.added_index = added_index
    def transform(self, dec_list):
        return [i for i in dec_list if i!=self.added_index]

class Resubstitute(DecListTransform):
    def __init__(self, removed_index, subed_indexes, added_start):
        self.removed_index = removed_index
        self.subed_indexes = subed_indexes
        self.added_start = added_start
    def transform(self, dec_list):
        def iter():
            for i in dec_list:
                if i>=self.added_start:
                    yield self.removed_index
                    yield self.subed_indexes[i-self.added_start]
                    continue
                if i>=self.removed_index:
                    i+=1
                yield i
        return list(iter())

class Unremove(DecListTransform):
    def __init__(self, removed_indexes):
        self.removed_indexes = sorted(removed_indexes)
    def transform(self, dec_list):
        def iter():
            for i in dec_list:
                removed_before = bisect(self.removed_indexes, i)
                yield i+removed_before
        return list(iter())

class RedoLeftRecursion(DecListTransform):
    def __init__(self, added_index, alpha_indexes):
        #assumes added_index is the max index
        self.added_index = added_index
        self.alpha_indexes = set(alpha_indexes)
    def transform(self, dec_list):
        def iter():
            rec_stack = None
            for i in dec_list:
                if i in self.alpha_indexes:
                    rec_stack = [i]
                elif rec_stack is None:
                    yield i
                else:
                    if i!=self.added_index:
                        rec_stack.append(i)
                    else:
                        while rec_stack:
                            yield rec_stack.pop()
                        rec_stack = None
        return list(iter())
    def __str__(self):
        ret = "RedoLeftRecursion - "
        ret+= str(self.added_index)+', '
        ret+= str(self.alpha_indexes)
        return ret

class Grammar:
    def __init__(self, rules=None, start=Symbol('S')):
        if rules is None:
            rules = []
        assert(isinstance(rules, list))
        assert(isinstance(start, Symbol))
        self.start = start
        self.rules = rules[:]
        self.rules_by_head_map = None
        self.reverse_lookup_map = None
        #the weekly-equivalent pre-compile grammar
        self.parent = None 
        #rules for converting a decision list from this grammar
        #into a weekly-equivalent one for the parent grammar
        self.to_parent_transforms = None 
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
    def __assert_parent__(self):
        if self.parent is None:
            self.parent = deepcopy(self)
            self.to_parent_transforms = []
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
            #looks like it needs factoring
            self.__assert_parent__()
            end = len(common_prefix)
            z = self.__gen_nonterminal__()
            for rule in rules:
                i = self.index(rule)
                self.rules[i] = Rule(z, rule.tail[end:])
            added_index = len(self.rules)
            self.rules.append(Rule(head, common_prefix+[z]))
            self.to_parent_transforms.append(Unfactor(added_index))
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
        subed_rules = self.rules_by_head(b)
        if not subed_rules:
            return False
        #needs substitution
        self.__assert_parent__()
        betas = [r.tail for r in self.rules_by_head(b)]
        subed_indexes = [self.index(r) for r in subed_rules]
        removed_index = self.index(rule)
        del self.rules[removed_index]
        added_start = len(self.rules)
        for beta in betas:
            self.rules.append(Rule(a,beta+alpha))
        resubstitute = Resubstitute(removed_index, subed_indexes, added_start)
        self.to_parent_transforms.append(resubstitute)
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
        removed = []
        for s in gen_graph.get_unreachable(self.start):
            to_del = self.rules_by_head(s)
            for rule in to_del:
                i = self.index(rule)
                removed.append(i)
                del self.rules[i]
        if removed:
            self.__assert_parent__()
            self.to_parent_transforms.append(Unremove(removed))
        return len(removed)
    def __remove_left_recursion__(self, head):
        rules = self.rules_by_head(head)
        betas = []
        alphas = []
        for rule in rules:
            if rule.tail[0]==head:
                betas.append(rule)
            else:
                alphas.append(rule)
        if not betas or not alphas:
            return False
        #needs recursion removed
        self.__assert_parent__()
        beta_indexes = []
        for b in xrange(len(betas)):
            rule = betas[b]
            beta_indexes.append(self.index(rule))
            betas[b] = rule.tail[1:]
        alpha_indexes = []
        for a in xrange(len(alphas)):
            rule = alphas[a]
            alpha_indexes.append(self.index(rule))
            alphas[a] = rule.tail
        z = self.__gen_nonterminal__(prefix=head.name)
        for i,alpha in izip(alpha_indexes, alphas):
            self.rules[i] = Rule(head, alpha+[z])
        for i,beta in izip(beta_indexes, betas):
            self.rules[i] = Rule(z, beta+[z])
        added_index = len(self.rules)
        self.rules.append(Rule(z, []))       
        redo = RedoLeftRecursion(added_index, alpha_indexes)
        self.to_parent_transforms.append(redo)
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
    def transform_to_parent(self, dec_list):
        for tpt in reversed(self.to_parent_transforms):
            dec_list = tpt.transform(dec_list)
        return dec_list
    def __str__(self):
        it = ('%d)\t%s'%(i,str(r)) for i,r in enumerate(self.rules))
        return '\n'.join(it)

