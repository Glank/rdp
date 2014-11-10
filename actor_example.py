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

#initialize movie name inclusion set
with open('ngpols/film_titles', 'rb') as f:
    titles_filt = NGClusterFilter.fromfile(f)

#setup the grammar
S = Symbol('S')
is_ = WordTerminal('IS')
actor = InclusionSetTerminal('actor', actor_filt , max_words=3)
in_ = WordTerminal('IN')
film = InclusionSetTerminal('film', titles_filt, max_words=7)
are_ = WordTerminal('ARE')
or_ = WordTerminal('OR')
and_ = WordTerminal('AND')
actor_and = Symbol('actor_and')
actor_or = Symbol('actor_or')

rules = [
    Rule(S, [is_, actor, in_, film]),
    Rule(S, [is_, actor_or, in_, film]),
    Rule(S, [are_, actor_and, in_, film]),
    Rule(S, [are_, actor_or, in_, film]),
    Rule(actor_and, [and_, actor]),
    Rule(actor_and, [actor, actor_and]),
    Rule(actor_or, [or_, actor]),
    Rule(actor_or, [actor, actor_or]),
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
    valid = False
    for interp in parser.parse_all():
        if not stream.finished():
            continue
        print '*'*70
        print interp.to_parse_tree()
        valid = True
    if valid:
        print '*'*70
    else:
        print "No valid interpretations found."
