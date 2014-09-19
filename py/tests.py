from grammar import *
from streams import *
from terms import *
from parser import *
import os.path

def mysql_str_test():
    string = Symbol('str')
    esc_ap = StringTerminal("''")
    del_ap = StringTerminal("'")
    not_ap = RegexTerminal(r"[^']")
    body_char = Symbol('body_char')
    body = Symbol('body')
    rules = [
        Rule(string, [del_ap, body, del_ap]),
        Rule(body_char, [esc_ap]),
        Rule(body_char, [not_ap]),
        Rule(body, [body_char, body]),
        Rule(body, []),
    ]
    gram = Grammar(rules, start=string)
    gram.compile()

    def is_mysql_string(s):
        stream = StringStream(s)
        parser = Parser(stream, gram)
        return parser.parse_full()

    yield is_mysql_string("'test'")
    yield is_mysql_string("''test'")
    yield is_mysql_string("'''test'''")
    yield is_mysql_string("''")
    yield is_mysql_string("'''")

def regex_test():
    S = Symbol('S')
    A = Symbol('A')
    dot = StringTerminal('.')
    letters = RegexTerminal('([a-zA-Z]+)')
    rules = [
        Rule(S, [A, letters]),
        Rule(A, []),
        Rule(A, [letters, dot, A]),
    ]
    gram = Grammar(rules)
    gram.compile()
    stream = StringStream("this.is.a.test")
    parser = Parser(stream, gram)
    yield parser.parse_full()
    yield parser
    yield parser.to_parse_tree()

def redo_left_recursion_big_test():
    S = Symbol('S')
    A = Symbol('A')
    B = Symbol('B')
    a = StringTerminal('a')
    b = StringTerminal('b')
    rules = [
        Rule(S, [A,B]),
        Rule(A, [a]),
        Rule(A, [S,A]),
        Rule(B, [b]),
        Rule(B, [S,B]),
    ]
    gram = Grammar(rules)
    yield str(gram)
    gram.compile()
    yield "*"*35
    yield str(gram)
    yield "*"*35

    stream = StringStream("aabb")
    parser = Parser(stream, gram)
    parser.parse_full()
    dec_list,_ = parser.get_generation_lists()
    yield dec_list
    yield gram.transform_to_parent(dec_list)

def big_test():
    S = Symbol('S')
    NP = Symbol('NP')
    VP = Symbol('VP')
    AVP = Symbol('AVP')
    N = Symbol('N')
    V = Symbol('V')
    DP = Symbol('DP')
    Det = Symbol('Det')
    Adj = Symbol('Adj')
    Adv = Symbol('Adv')
    rules = [
        Rule(S, [DP, VP]),
        Rule(DP, [Det, NP]),
        Rule(DP, [NP]),
        Rule(NP, [Adj, NP]),
        Rule(NP, [N]),
        Rule(VP, [V]),
        Rule(Det, [WordTerminal("the")]),
        Rule(Adj, [WordTerminal("fine")]),
        Rule(N, [WordTerminal("fine")]),
        Rule(N, [WordTerminal("cook")]),
        Rule(V, [WordTerminal("gave")]),
    ]
    gram = Grammar(rules, store_intermediates=True)
    yield str(gram)
    gram.compile()
    yield str(gram)
    stream = WordStream("the fine cook gave".split())
    parser = Parser(stream, gram)
    parsed =  parser.parse_full()
    yield parser
    dec_list, terms = parser.get_generation_lists()
    yield str(terms)
    yield str(dec_list)
    yield str(gram.transform_to_parent(dec_list))
    tree = parser.to_parse_tree()
    yield str(tree)

def decompile_test():
    yield "Decompile test."
    S = Symbol('S')
    a = StringTerminal('a')
    b = StringTerminal('b')
    a_ = RepeatTerminal(a,2,3)
    rules = [
        Rule(S, [b, a_]),
        Rule(S, [S, b, a_]),
    ]
    gram = Grammar(rules)
    yield gram
    yield ''
    gram.compile()
    yield gram
    yield gram.transform_to_parent([0,2])

def parsetree_complied_test():
    yield "ParseTree Compiled test..."
    S = Symbol('S')
    B = Symbol('B')
    a = StringTerminal('a')
    b = StringTerminal('b')
    a_ = RepeatTerminal(a,2,3)
    rules = [
        Rule(S, [B, a_]),
        Rule(B, [B, b]),
        Rule(B, [b]),
    ]
    gram = Grammar(rules)
    yield str(gram)
    gram.compile()
    stream = StringStream('bbaaaa')
    parser = Parser(stream, gram)
    yield gram
    parsed =  parser.parse_partial()
    yield parsed
    if parsed:
        yield parser
        tree = parser.to_parse_tree()
        yield tree
        yield ''.join(n.instance for n in tree.nonepsilon_terms())

def parsetree_test():
    yield "ParseTree test..."
    S = Symbol('S')
    a = StringTerminal('a')
    b = StringTerminal('b')
    a_ = RepeatTerminal(a,2,3)
    rules = [
        Rule(S, [b, a_]),
    ]
    gram = Grammar(rules)
    stream = StringStream('baaaa')
    parser = Parser(stream, gram)
    yield gram
    yield parser.parse_partial()
    yield parser.to_parse_tree()
    yield parser

def substream_test():
    yield "Substream test..."
    S = Symbol('S')
    a = StringTerminal('a')
    rules = [
        Rule(S, [a, S]),
        Rule(S, [])
    ]
    gram = Grammar(rules)
    stream = StringStream('baaa')
    stream.advance(1)
    parser = Parser(stream.substream(), gram)
    yield parser.parse_partial()
    yield parser

def repeat_term_test():
    yield "Repeat term test..."
    for g in [True,False]:
        if g:
            yield 'Gready:'
        else:
            yield 'Not Gready:'
        S = Symbol('S')
        a = StringTerminal('a')
        b = StringTerminal('b')
        a_ = RepeatTerminal(a,2,3,gready=g)
        rules = [
            Rule(S, [b, a_]),
        ]
        gram = Grammar(rules)
        stream = StringStream('baaaa')
        yield gram
        yield stream
        parser = Parser(stream, gram)
        yield parser.parse_partial()
        yield parser

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
    parser = Parser(stream, grammar)
    yield parser
    def is_match(parser):
       return parser.stream.index>=3
    yield parser.parse_filtered(is_match)
    yield parser
    decs, terms = parser.get_generation_lists()
    yield decs
    yield terms
    #rec = "".join(terms)
    #yield rec
    #assert stream.string.startswith(rec)

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
    parser = Parser(stream, grammar)
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
    test_dir = '../test_results'
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
        repeat_term_test,
        substream_test,
        parsetree_test,
        decompile_test,
        parsetree_complied_test,
        big_test,
        redo_left_recursion_big_test,
        regex_test,
        mysql_str_test,
    ]
    for test in tests:
        print test.__name__
        results = "\n".join(str(o) for o in test())
        fn = test_dir+'/'+test.__name__
        old_results = try_get_file(fn)
        if old_results != results:
            print "!!! Old test results do not match: !!!"
            print results
            if ask_yn("Is this new output valid? (y/n)"):
                with open(fn,'w') as f:
                    f.write(results)
            else:
                print "Test failed."
                exit()
    print "All tests passed!"
