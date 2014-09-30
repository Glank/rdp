from rdp import *
import os.path

def comp_terminal_test():
    stream = StringStream('abaabba')
    aob = Symbol('a|b')
    a,b = StringTerminal('a'), StringTerminal('b')
    rules = [
        Rule(aob, [a]),
        Rule(aob, [b]),
    ]
    g = Grammar(rules, start=aob)
    g.compile()
    parser = Parser(stream, g)
    print parser.parse_partial()
    print parser
    ct = ComplexTerminalSymbol('a|b', g)
    print ct
    print ct.subgrammar()
    print '*'*20
    S = Symbol('S')
    rules = [
        Rule(S, [ct,S]),
        Rule(S, []),
    ]
    g = Grammar(rules)
    g.compile()
    print g
    parser = Parser(stream, g)
    def debug_out(x):
        print x,
    parser.debug_out = debug_out
    for parser in parser.parse_all():
        print parser

comp_terminal_test()
