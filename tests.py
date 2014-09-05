from grammar import *
from rdparse import *
import os.path

def factor_test():
    yield "Factoring test..."
    s = Symbol('S')
    a = TerminalSymbol('a')
    b = TerminalSymbol('b')
    c = TerminalSymbol('c')
    rules = [
        Rule(s, [a,b]),
        Rule(s, [a,c]),
    ]
    gram = Grammar(rules)
    yield gram
    yield '*'*10
    yield gram.try_factoring()
    yield '*'*10
    yield gram

def substitute_test():
    yield "Substitution test..."
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
    yield gram
    yield '*'*10
    yield gram.try_substituting()
    yield '*'*10
    yield gram

def useless_test():
    yield "Remove Useless test..."
    s = Symbol('S')
    n = Symbol('N')
    a = TerminalSymbol('a')
    b = TerminalSymbol('b')
    rules = [
        Rule(s, [a]),
        Rule(n, [b])
    ]
    gram = Grammar(rules)
    yield gram
    yield '*'*10
    yield gram.try_removing_useless_rules()
    yield '*'*10
    yield gram

def recursion_test():
    yield "Remove left recursion test..."
    s = Symbol('S')
    a = TerminalSymbol('a')
    rules = [
        Rule(s, [a]),
        Rule(s, [s,a])
    ]
    gram = Grammar(rules)
    yield gram
    yield '*'*10
    yield gram.try_removing_left_recursion()
    yield '*'*10
    yield gram

def compilation_test():
    yield "Compilation test."
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
    yield gram
    yield gram.is_parseable()
    yield '*'*10
    yield gram.compile()
    yield '*'*10
    yield gram
    yield gram.is_parseable()

def rdp_test():
    yield "RDP Test."
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
    yield grammar
    stream = StringStream('ababa')
    yield stream
    parser = RDParser(stream, grammar)
    yield parser
    def is_match(parser):
       return parser.stream.index>=3
    yield parser.parse_filtered(is_match)
    yield parser
    decs, terms = parser.get_generation_lists()
    yield decs
    rec = "".join(terms)
    yield rec
    assert stream.string.startswith(rec)

def unfactor_test():
    yield "Unfactor Test."
    S = Symbol('S')
    a = StringTerminal('a')
    b = StringTerminal('b')
    c = StringTerminal('c')
    rules = [
        Rule(S, [a,b]),
        Rule(S, [a,c]),
    ]
    gram = Grammar(rules)
    yield "Parent Grammar:"
    yield gram
    assert(gram.try_factoring())
    yield "Factored Grammar:"
    yield gram
    yield "Reversions:"
    for test in [[2,0],[2,1]]:
        parent_v = gram.transform_to_parent(test)
        yield "%s -> %s"%(str(test), str(parent_v))

def resubstitute_test():
    yield "Resubstitute Test."
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
    yield "Parent Grammar:"
    yield gram
    assert(gram.try_substituting())
    yield "Factored Grammar:"
    yield gram
    yield "Reversions:"
    for test in [[2],[3]]:
        parent_v = gram.transform_to_parent(test)
        yield "%s -> %s"%(str(test), str(parent_v))

def resubstitute_test():
    yield "Resubstitute Test."
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
    yield "Parent Grammar:"
    yield gram
    assert(gram.try_substituting())
    yield "Substituted Grammar:"
    yield gram
    yield "Reversions:"
    for test in [[2],[3]]:
        parent_v = gram.transform_to_parent(test)
        yield "%s -> %s"%(str(test), str(parent_v))

def unremove_test():
    yield "Unremove Test."
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
    yield "Parent Grammar:"
    yield gram
    assert(gram.try_removing_useless_rules())
    yield "Cleaned Grammar:"
    yield gram
    yield "Reversions:"
    for test in [[0,1,1,2],[0,2]]:
        parent_v = gram.transform_to_parent(test)
        yield "%s -> %s"%(str(test), str(parent_v))

def redolr_test():
    yield "Redo Left Recursion Test."
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
    yield "Parent Grammar:"
    yield gram
    assert(gram.try_removing_left_recursion())
    yield "No Left Recursion Grammar:"
    yield gram
    yield "Reversions:"
    for test in [[3,0,0,2,4],[1,2,0,4]]:
        parent_v = gram.transform_to_parent(test)
        yield "%s -> %s"%(str(test), str(parent_v))

def simple_rdp_test():
    yield "Simple RDP Test."
    S = Symbol('S')
    A = Symbol('A')
    a = StringTerminal('a')
    rules = [
        Rule(S, [a,A]),
        Rule(A, []),
        Rule(A, [a]),
    ]
    grammar = Grammar(rules)
    grammar.compile()
    #grammer.compile_rbhm()
    #grammer.compile_rlm()
    yield grammar
    stream = StringStream('aa')
    yield stream
    parser = RDParser(stream, grammar)
    yield parser
    yield parser.parse_full()
    yield parser

def try_get_file(name):
    if os.path.isfile(name):
        with open(name,'r') as f:
            return f.read()
    return None

def ask_yn(question):
    answer = None
    while answer not in ['y','n','yes','no']:
        print question
        answer = raw_input().lower()
    return answer in ['y','yes']

if __name__=='__main__':
    test_dir = 'test_results'
    tests = [
        factor_test,
        substitute_test,
        useless_test,
        recursion_test,
        compilation_test,
        rdp_test,
        unfactor_test,
        resubstitute_test,
        unremove_test,
        redolr_test,
        simple_rdp_test,
    ]
    for test in tests:
        results = "\n".join(str(o) for o in test())
        fn = test_dir+'/'+test.__name__
        old_results = try_get_file(fn)
        if old_results != results:
            print "!!! Old test results do not match current results: !!!"
            print results
            if ask_yn("Is this new output valid? (y/n)"):
                with open(fn,'w') as f:
                    f.write(results)
            else:
                print "Test failed."
                exit()
    print "All tests passed!"
