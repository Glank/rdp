from rdp import *
import os.path
import re
import copy

def term_backtrack_bug_test():
    #setup the grammar
    S = Symbol('S')
    is_ = WordTerminal('IS')
    actor = InclusionSetTerminal(
        'actor', set(['WILLSMITH']), max_words=3
    )
    in_ = WordTerminal('IN')
    film = InclusionSetTerminal(
        'film', set(['INDEPENDENCEDAY']), max_words=7
    )
    rules = [
        Rule(S, [is_, actor, in_, film]),
    ]
    gram = Grammar(rules)
    gram.compile()
    sentence = "IS WILL SMITH IN INDEPENDENCE DAY"
    words = list(re.findall('\w+',sentence))
    stream = WordStream(words)
    parser = Parser(stream, gram)
    valid = False
    for interp in parser.parse_all():
        if not stream.finished():
            continue
        yield '*'*70
        yield interp.to_parse_tree()
        valid = True
    if valid:
        yield '*'*70
    else:
        yield "No valid interpretation was found."

def shtl_terminal_test():
    S = Symbol('S')
    the = WordTerminal('the')
    dog = SHTLTerminal('dog', pos='n')
    barked = SHTLTerminal('barked', pos='v')
    rules = [
        Rule(S, [the, dog, barked])
    ]
    gram = Grammar(rules)
    gram.compile()

    yield "Input: The dog barked."
    sentences = [
        "the great dane barked",
        "the cat meowed",
        "the terrier yiped",
        "the puppy yiped",
        "the wolf howled",
        "the some-really-long-name-for-a-dog barked",
        "the",
    ]
    for sentence in sentences:
        yield sentence
        words = list(re.findall('\w+',sentence))
        stream = WordStream(words)
        parser = Parser(stream, gram)
        yield parser.parse_full()

def repeat_terminal_test():
    a = StringTerminal('a')
    for minimum in [0,1,2]:
        for maximum in [None,1,10]:
            if not maximum or minimum<=maximum:
                for gready in [True,False]:
                    t = RepeatTerminal(
                        a,
                        minimum=minimum,
                        maximum=maximum,
                        gready=gready
                    )
                    yield str(t)

def terminal_test():
    t = RegexTerminal('^test\n.*\ntest$', flags=re.MULTILINE|re.IGNORECASE|re.DOTALL)
    yield str(t)
    t = KeywordTerminal('test')
    yield str(t)
    stream = StringStream('testing Test bla')
    yield t.try_consume(stream)
    stream.advance(8)
    yield t.try_consume(stream)
    stream.advance(4)
    yield t.try_consume(stream)
    stream.reset()
    t = KeywordTerminal('Test', case_sensitive=True)
    stream.advance(8)
    yield t.try_consume(stream)
    t = copy.deepcopy(t)
    yield str(t)

def word_stream_test():
    stream = WordStream('this is a test'.split())
    yield stream.has('this')
    yield stream.has('is')
    stream.advance(1)
    yield stream.has('is')
    stream.advance(3)
    yield stream.has('this')
    stream.reset()
    yield stream.has('this')
    stream.advance(2)
    stream2 = stream.substream()
    yield str(stream2)
    yield stream2.has('a')
    yield stream2.has('test')
    stream2.advance(1)
    yield stream2.has('test')

def string_stream_test():
    stream = StringStream("This is a test.")
    yield str(stream.substream())
    stream.advance(10)
    yield str(stream.substream())
    stream.reset()
    yield str(stream.substream())

def abstract_stream_test():
    s = ParsingStream()
    def test(f):
        try:
            f()
            return 'bad'
        except NotImplementedError:
            return 'good'
    yield test(lambda: s.reset())
    yield test(lambda: s.advance(1))
    yield test(lambda: s.backtrack(1))
    yield test(lambda: s.substream())
    yield 'done';

def pfilter_and_find_test():
    S = Symbol('S')
    A = Symbol('A')
    a,b = StringTerminal('a'), StringTerminal('b')
    rules = [
        Rule(S, [A,b,S]),
        Rule(S, []),
        Rule(A, [a]),
        Rule(A, [a,a]),
        Rule(A, [a,a,a]),
    ]
    gram = Grammar(rules)
    stream = StringStream('aabaaabab')
    parser = Parser(stream, gram)
    def pfilter(x):
        return x.symbol!=b
    yield parser.parse_full()
    root = parser.to_parse_tree()
    for node in root.iter_nodes(pfilter=pfilter):
        yield str(node)
    yield '*'*20
    yield root.find_node(lambda x:x.symbol==A)

def not_even_partial_test():
    S = Symbol('S')
    a = StringTerminal('a')
    rules = [
        Rule(S, [a,a,a])
    ]
    gram = Grammar(rules)
    stream = StringStream('aa')
    parser = Parser(stream, gram)
    yield parser.parse_partial()

def accept_empty_test():
    S = Symbol('S')
    rules = [
        Rule(S, []),
    ]
    gram = Grammar(rules)
    stream = StringStream('')
    parser = Parser(stream, gram)
    debugs = []
    def debug_out(s):
        debugs.append(s)
    parser.debug_out = debug_out
    for p in parser.parse_all():
        yield str(p)
    yield ''.join(debugs)
    yield "done"

def comp_terminal_test():
    aob = Symbol('a|b')
    a,b = StringTerminal('a'), StringTerminal('b')
    rules = [
        Rule(aob, [a]),
        Rule(aob, [b]),
    ]
    g = Grammar(rules, start=aob)
    g.compile()
    ct = ComplexTerminalSymbol('a|b', g)
    yield ct
    yield ct.subgrammar()
    yield '*'*20
    S = Symbol('S')
    rules = [
        Rule(S, [ct,S]),
        Rule(S, []),
    ]
    g = Grammar(rules)
    g.compile()
    yield g
    stream = StringStream('abaabba')
    parser = Parser(stream, g)
    debugs = []
    def debug_out(s):
        debugs.append(s)
    parser.debug_out = debug_out
    yield parser.parse_full()
    yield ''.join(debugs)
    yield parser

def grammar_tests():
    S = Symbol('S')
    A = Symbol('A')
    B = Symbol('B')
    rules = [
        Rule(S, [A,A]),
    ]
    g = Grammar(rules)
    yield g.is_parseable()
    yield g.__substitute__(rules[0])
    t0 = TerminalSymbol('t0')
    t1 = TerminalSymbol('t1')
    rules = [
        Rule(S, [A,B]),
        Rule(A, [t0, t0]),
        Rule(A, [t0, t1]),
        Rule(B, [t1, t0]),
        Rule(B, [t1, t1]),
    ]
    g = Grammar(rules)
    yield str(g)
    yield '*'*20
    g.compile()
    yield str(g)
    yield g.transform_to_parent(
        [5,0,4,2], include_intermediates=True
    )

def transform_tests():
    t = DecListTransform()
    try:
        t.transform(None)
        yield 'reached'
    except NotImplementedError as e:
        yield 'not implemented'
    uf = Unfactor(0,[1,2,3,4])
    yield str(uf)
    rs = Resubstitute(0,[1,2,3,4],5)
    yield str(rs)
    ur = Unremove([1,2,3])
    yield str(ur)
    rlr = RedoLeftRecursion(0, [1,2,3], [4,5,6])
    yield str(rlr)

def symbol_tests():
    s = Symbol('S')
    yield repr(s)
    t = TerminalSymbol('t')
    yield repr(t)
    try:
        t.try_consume(None)
        yield 'reached'
    except NotImplementedError as e:
        yield 'not implemented'
    try:
        t.get_instance()
        yield 'reached'
    except NotImplementedError as e:
        yield 'not implemented'
    yield repr(Epsilon())

def rule_test():
    s = Symbol('S')
    r = Rule(s, [s, s])
    yield r.is_left_recursive()
    yield r==r
    yield r!=r

def finite_graph_first_test():
    g = DirectedGraph()
    for v in 'abcdefg':
        g.add_vertex(v)
    edges = [
        ('a','b'),  
        ('b','c'),
        ('b','d'),
        ('d','e'),
        ('d','f'),
        ('f','g'),
        ('g','b'),
    ]
    for e in edges:
        g.add_edge(*e)
    yield g.dfs('a','g')
    yield g.is_cyclic()
    yield g.leaves()

def finite_graph_test():
    yield "Finite graph test."
    g = DirectedGraph()
    yield g.is_cyclic()
    g.add_vertex('a')
    g.add_vertex('b')
    g.add_vertex('c')
    g.add_vertex('d')
    g.add_vertex('e')
    g.add_vertex('f')
    g.add_edge('a','b')
    g.add_edge('b','c')
    g.add_edge('c','d')
    g.add_edge('d','b')
    g.add_edge('e','f')
    yield len(g)
    yield "a->e", g.dfs('a','e')
    yield "e->a", g.dfs('e','a')
    yield "f->a", g.dfs('f','a')
    yield 'Roots:', g.roots()

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
    dec_list,_,_ = parser.get_generation_lists()
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
    dec_list, terms, _ = parser.get_generation_lists()
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
    decs, terms, _ = parser.get_generation_lists()
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
        repeat_term_test,
        substream_test,
        parsetree_test,
        decompile_test,
        parsetree_complied_test,
        big_test,
        redo_left_recursion_big_test,
        regex_test,
        mysql_str_test,
        finite_graph_test,
        finite_graph_first_test,
        rule_test,
        symbol_tests,
        transform_tests,
        grammar_tests,
        comp_terminal_test,
        accept_empty_test,
        not_even_partial_test,
        pfilter_and_find_test,
        abstract_stream_test,
        string_stream_test,
        word_stream_test,
        terminal_test,
        repeat_terminal_test,
        term_backtrack_bug_test,
        shtl_terminal_test,
    ]
    for test in tests:
        print test.__name__
        results = "\n".join(str(o) for o in test())
        fn = test_dir+'/'+test.__name__
        old_results = try_get_file(fn)
        if old_results != results:
            print "!!! Old test results do not match: !!!"
            print results
            print "#"*20+'Old Results'+'#'*20
            print old_results
            if ask_yn("Is this new output valid? (y/n)"):
                with open(fn,'w') as f:
                    f.write(results)
            else:
                print "Test failed."
                exit()
    print "All tests passed!"
    
