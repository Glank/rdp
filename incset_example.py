#!/usr/bin/env python 
from rdp import *
from pybloom import BloomFilter

#the incusion set comes from the names of people
#in an rdf document which are pre-compiled into
#a bloom filter.
with open('blooms/uni_names', 'r') as f:
    uni_names = BloomFilter.fromfile(f)

S = Symbol('S')
is_ = WordTerminal('is')
person = InclusionSetTerminal('person', uni_names, max_words=4)
in_ = WordTerminal('in')
the = WordTerminal('the')
doc = SHTLTerminal('file', pos='n')
rules = [
    Rule(S, [is_, person, in_, the, doc])
]
gram = Grammar(rules)
gram.compile()

print "Input: Is <person> in the file?"
while True:
    sentence = raw_input().lower()
    words = list(re.findall('\w+',sentence))
    stream = WordStream(words)
    parser = Parser(stream, gram)
    if parser.parse_full():
        print parser.to_parse_tree()
    else:
        print "Not valid."
