#!/usr/bin/env python 
from rdp import *
import os.path
import re

S = Symbol('S')
the = WordTerminal('the')
dog = SHTLTerminal('dog', pos='n')
barked = SHTLTerminal('barked', pos='v')
rules = [
    Rule(S, [the, dog, barked])
]
gram = Grammar(rules)
gram.compile()

print "Input: The dog barked."
while True:
    sentence = raw_input().strip().lower()
    if sentence in ["quit", "q", "exit"]:
        exit()
    words = list(re.findall('\w+',sentence))
    stream = WordStream(words)
    parser = Parser(stream, gram)
    print parser.parse_full()
