from grammar import *
from streams import *
from terms import *
from parser import *

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
print gram
#TODO: work's uncompiled, but not compiled
gram.compile()
print gram
#print gram
stream = WordStream("the fine cook gave".split())
parser = Parser(stream, gram)
parser.verbose=True
parsed =  parser.parse_full()
print parsed
if parsed:
    print parser
    dec_list, terms = parser.get_generation_lists()
    print terms
    print dec_list
    if gram.parent is not None:
        print gram.transform_to_parent(dec_list)
    if False:
        decs = gram.transform_to_parent(dec_list, include_intermediates=True)
        decs.reverse()
        print len(gram.to_parent_transforms)
        for i in xrange(len(decs)):
            print '*'*20
            print i
            dec = decs[i]
            g = gram.intermediates[i]
            print dec    
            print g
            print list(n.symbol for n in build_tree(None, 0, g, dec).nonepsilon_terms())
            if i<len(gram.to_parent_transforms):
                print gram.to_parent_transforms[i]
    tree = parser.to_parse_tree()
    print tree

