#!/usr/bin/env python 
from rdp import *
from ngrams import *
from pybloom import BloomFilter
from edits import *

#initialize actor inclusion set
with open('blooms/actor_names', 'rb') as f:
    actor_bloom = BloomFilter.fromfile(f)
with open('ngpols/actor_names', 'rb') as f:
    actor_ngpol = NGPOLFilter.fromfile(f)
actor_fuzzy = BloomFSS(actor_bloom, 1)
actor_filt = OrSet([actor_ngpol, actor_fuzzy])
print "JOHN SMITH" in actor_filt

#initialize movie name inclusion set
with open('ngpols/film_titles', 'rb') as f:
    titles_filt = NGClusterFilter.fromfile(f)

#setup the grammar
S = Symbol('S')
is_ = WordTerminal('IS')
actor = InclusionSetTerminal('actor', actor_filt , max_words=3)
in_ = WordTerminal('IN')
film = InclusionSetTerminal('film', titles_filt, max_words=4)

rules = [
    Rule(S, [is_, actor, in_, film]),
]
gram = Grammar(rules)
gram.compile()

#run test
print "Ready."
while True:
    sentence = raw_input().strip().upper()
    if sentence in ["QUIT", "Q", "EXIT"]:
        exit()
    words = list(re.findall('\w+',sentence))
    stream = WordStream(words)
    parser = Parser(stream, gram)
    def out(x):
        print x
    parser.debug_out = out
    if parser.parse_full():
        print parser.to_parse_tree()
    else:
        print "Not valid."
