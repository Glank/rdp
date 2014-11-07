#!/usr/bin/env python 
from rdp import *

S = Symbol('S') #sentence/start symbol
NP = Symbol('NP') #noun phrase
VP = Symbol('VP') #verb phrase
PN = Symbol('PN') #proper noun
RC = Symbol('RC') #relative clause
N = Symbol('N') #noun
V = Symbol('V') #verb
bufN = WordTerminal('BUFFALO')
bufV = WordTerminal('BUFFALO')
bufPN = WordTerminal('BUFFALO')
rules = [
    Rule(S, [NP, VP]),
    Rule(RC, [NP, V]),
    Rule(NP, [PN, N]),
    Rule(NP, [NP, RC]),
    Rule(VP, [V, NP]),
    Rule(N, [bufN]),
    Rule(V, [bufV]),
    Rule(PN, [bufPN]),
]
gram = Grammar(rules, store_intermediates=True)
gram.compile()
print gram
#exit()

test = """
    Buffalo buffalo buffalo Buffalo buffalo Buffalo buffalo buffalo
""".strip().upper()

print test
stream = WordStream(test.split())
print stream
parser = Parser(stream, gram)
for interp in parser.parse_all():
    if not stream.finished():
        continue
    print '*'*70
    print interp.to_parse_tree()
