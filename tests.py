from grammar import *
from rdparse import *

def factor_test():
    print "Factoring test..."
    s = Symbol('S')
    a = TerminalSymbol('a')
    b = TerminalSymbol('b')
    c = TerminalSymbol('c')
    rules = [
        Rule(s, [a,b]),
        Rule(s, [a,c]),
    ]
    gram = Grammar(rules)
    print gram
    print '*'*10
    print gram.try_factoring()
    print '*'*10
    print gram
    print

def substitute_test():
    print "Substitution test..."
    s = Symbol('S')
    n = Symbol('N')
    a = TerminalSymbol('a')
    b = TerminalSymbol('b')
    c = TerminalSymbol('c')
    rules = [
        Rule(s, [n,c]),
        Rule(n, [a]),
        Rule(n, [b]),
    ]
    gram = Grammar(rules)
    print gram
    print '*'*10
    print gram.try_substituting()
    print '*'*10
    print gram
    print

def useless_test():
    print "Remove Useless test..."
    s = Symbol('S')
    n = Symbol('N')
    a = TerminalSymbol('a')
    b = TerminalSymbol('b')
    rules = [
        Rule(s, [a]),
        Rule(n, [b])
    ]
    gram = Grammar(rules)
    print gram
    print '*'*10
    print gram.try_removing_useless_rules()
    print '*'*10
    print gram
    print

def recursion_test():
    print "Remove left recursion test..."
    s = Symbol('S')
    a = TerminalSymbol('a')
    rules = [
        Rule(s, [a]),
        Rule(s, [s,a])
    ]
    gram = Grammar(rules)
    print gram
    print '*'*10
    print gram.try_removing_left_recursion()
    print '*'*10
    print gram
    print

def compilation_test():
    print "Compilation test."
    S = Symbol('S')
    A = Symbol('A')
    B = Symbol('B')
    a = TerminalSymbol('a')
    b = TerminalSymbol('b')
    rules = [
        Rule(S, [A,B]),
        Rule(A, [a]),
        Rule(A, [S,A]),
        Rule(B, [b]),
        Rule(B, [S,B]),
    ]
    gram = Grammar(rules)
    print gram
    print gram.is_parseable()
    print '*'*10
    print gram.compile()
    print '*'*10
    print gram
    print gram.is_parseable()
    print

def rdp_test():
    print "RDP Test."
    S = Symbol('S')
    A = Symbol('A')
    B = Symbol('B')
    a = StringTerminal('a')
    b = StringTerminal('b')
    rules = [
        Rule(S, [A,B]),
        Rule(A, [a]),
        Rule(B, [b,A,B]),
        Rule(B, [b]),
    ]
    grammar = Grammar(rules)
    grammar.compile()
    #grammer.compile_rbhm()
    #grammer.compile_rlm()
    print grammar
    stream = StringStream('ababa')
    print stream
    parser = RDParser(stream, grammar)
    print parser
    def is_match(parser):
       return parser.stream.index>=3
    print parser.parse_filtered(is_match)
    print parser
    decs, terms = parser.get_generation_lists()
    print decs
    rec = "".join(terms)
    print rec
    assert stream.string.startswith(rec)

def unfactor_test():
    print "Unfactor Test."
    S = Symbol('S')
    a = StringTerminal('a')
    b = StringTerminal('b')
    c = StringTerminal('c')
    rules = [
        Rule(S, [a,b]),
        Rule(S, [a,c]),
    ]
    gram = Grammar(rules)
    print "Parent Grammar:"
    print gram
    assert(gram.try_factoring())
    print "Factored Grammar:"
    print gram
    print "Reversions:"
    for test in [[2,0],[2,1]]:
        parent_v = gram.transform_to_parent(test)
        print "%s -> %s"%(str(test), str(parent_v))

def resubstitute_test():
    print "Resubstitute Test."
    S = Symbol('S')
    N = Symbol('N')
    a = StringTerminal('a')
    b = StringTerminal('b')
    c = StringTerminal('c')
    rules = [
        Rule(S, [N,c]),
        Rule(N, [a]),
        Rule(N, [b]),
    ]
    gram = Grammar(rules)
    print "Parent Grammar:"
    print gram
    assert(gram.try_substituting())
    print "Factored Grammar:"
    print gram
    print "Reversions:"
    for test in [[2],[3]]:
        parent_v = gram.transform_to_parent(test)
        print "%s -> %s"%(str(test), str(parent_v))

def resubstitute_test():
    print "Resubstitute Test."
    S = Symbol('S')
    N = Symbol('N')
    a = StringTerminal('a')
    b = StringTerminal('b')
    c = StringTerminal('c')
    rules = [
        Rule(S, [N,c]),
        Rule(N, [a]),
        Rule(N, [b]),
    ]
    gram = Grammar(rules)
    print "Parent Grammar:"
    print gram
    assert(gram.try_substituting())
    print "Substituted Grammar:"
    print gram
    print "Reversions:"
    for test in [[2],[3]]:
        parent_v = gram.transform_to_parent(test)
        print "%s -> %s"%(str(test), str(parent_v))

def unremove_test():
    print "Unremove Test."
    S = Symbol('S')
    A = Symbol('A')
    B = Symbol('B')
    a = StringTerminal('a')
    b = StringTerminal('b')
    c = StringTerminal('c')
    rules = [
        Rule(S, [a,A]),
        Rule(B, [b]),
        Rule(A, [a,A]),
        Rule(A, []),
        Rule(B, []),
    ]
    gram = Grammar(rules)
    print "Parent Grammar:"
    print gram
    assert(gram.try_removing_useless_rules())
    print "Cleaned Grammar:"
    print gram
    print "Reversions:"
    for test in [[0,1,1,2],[0,2]]:
        parent_v = gram.transform_to_parent(test)
        print "%s -> %s"%(str(test), str(parent_v))

def redolr_test():
    print "Redo Left Recursion Test."
    S = Symbol('S')
    a1 = Symbol('a1')
    a2 = Symbol('a2')
    b1 = Symbol('b1')
    b2 = Symbol('b2')
    rules = [
        Rule(S, [S,b1]),
        Rule(S, [a2]),
        Rule(S, [S,b2]),
        Rule(S, [a1]),
    ]
    gram = Grammar(rules)
    print "Parent Grammar:"
    print gram
    assert(gram.try_removing_left_recursion())
    print "No Left Recursion Grammar:"
    print gram
    print "Reversions:"
    for test in [[3,0,0,2,4],[1,2,0,4]]:
        parent_v = gram.transform_to_parent(test)
        print "%s -> %s"%(str(test), str(parent_v))

if __name__=='__main__':
    #factor_test()
    #substitute_test()
    #useless_test()
    #recursion_test()
    #compilation_test()
    #rdp_test()
    #unfactor_test()
    #resubstitute_test()
    #unremove_test()
    redolr_test()
