#!/usr/bin/env python 
from rdp import *
from ngrams import NGClusterFilter

#the incusion set comes from the names of people
#in an rdf document which are pre-compiled into
#a bloom filter.
with open('ngpols/uni_names_cluster', 'r') as f:
    uni_names = NGClusterFilter.fromfile(f)

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
    sentence = raw_input().strip().lower()
    if sentence in ["quit", "q", "exit"]:
        exit()
    words = list(re.findall('\w+',sentence))
    stream = WordStream(words)
    parser = Parser(stream, gram)
    if parser.parse_full():
        print parser.to_parse_tree()
    else:
        print "Not valid."
