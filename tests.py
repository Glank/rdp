from grammar import *

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

if __name__=='__main__':
    #factor_test()
    #substitute_test()
    #useless_test()
    #recursion_test()
    compilation_test()
