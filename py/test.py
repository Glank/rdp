from grammar import *
from streams import *
from terms import *
from parser import *

S = Symbol('S')
NP = Symbol('NP')
VP = Symbol('VP')
N = Symbol('N')
V = Symbol('V')
rules = [
    Rule(S, [NP, VP]),
    Rule(NP, [N]),
    Rule(VP, [V, N]),
    Rule(VP, [V]),
    Rule(N, [WordTerminal("john")]),
    Rule(N, [WordTerminal("dave")]),
    Rule(V, [WordTerminal("hit")]),
    Rule(V, [WordTerminal("poked")]),
]
gram = Grammar(rules, store_intermediates=True)
print gram
gram.compile()
#print gram
stream = WordStream("john hit dave".split())
parser = Parser(stream, gram)
parsed =  parser.parse_full()
print parsed
if parsed:
    print parser
    dec_list, terms = parser.get_generation_lists()
    print terms
    print dec_list
    decs = gram.transform_to_parent(dec_list, include_intermediates=True)
    decs.reverse()
    for i in xrange(len(decs)):
        dec = decs[i]
        g = gram.intermediates[i]
        print dec    
        print g
        print gram.to_parent_transforms[-i]
    tree = parser.to_parse_tree()
    print tree

