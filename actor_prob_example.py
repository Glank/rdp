#!/usr/bin/env python 
from rdp import *
from ngrams import *
from pybloom import BloomFilter
from edits import *
from distribute import *

#initialize actor probset
with open('probsets/actor_names', 'rb') as f:
    actor_probset1 = NgramProbSet.fromfile(f)
with open('probsets/actor_names_len', 'rb') as f:
    actor_probset2 = LengthProbSet.fromfile(f)
actor_probset = JoinedProbabilitySet([actor_probset1, actor_probset2])

#initialize movie name inclusion set
with open('ngpols/film_titles', 'rb') as f:
    titles_filt = NGClusterFilter.fromfile(f)

#setup the grammar
S = Symbol('S')

is_ = InclusionSetTerminal(
    'IS',
    set(['BE','IS','WAS','WERE','ARE','DOES'])
);
will_ = InclusionSetTerminal(
    'WILL',
    set(['WILL', 'ARE'])
);

actor = ProbabilitySetTerminal('actor', actor_probset, max_words=3)

in_ = InclusionSetTerminal(
    'IN', set(['IN','ACTIN', 'ACTINGIN','PERFORMINGIN', 'PERFORMIN']),
    max_words=2
);
be_in = InclusionSetTerminal(
    'BE_IN',
    set([
        'BEIN','ACTIN','BEACTINGIN',
        'PERFORMIN','BEPERFORMINGIN',
        'GOINGTOBEPERORMINGIN','GOINGTOBEACTINGIN',
        'GOINGTOBEIN',
    ]),
    max_words=5
);

film = InclusionSetTerminal('film', titles_filt, max_words=7)

actor_set = Symbol('actor_set')

are_ = WordTerminal('ARE')
or_ = WordTerminal('OR')
and_ = WordTerminal('AND')
comma = WordTerminal(',')
actor_and = Symbol('actor_and')
actor_or = Symbol('actor_or')

rules = [
    Rule(S, [is_, actor_set, in_, film]),
    Rule(S, [will_, actor_set, be_in, film]),
    Rule(actor_set, [actor]),
    Rule(actor_set, [actor_or]),
    Rule(actor_set, [actor_and]),
    Rule(actor_and, [and_, comma, actor]),
    Rule(actor_and, [and_, actor]),
    Rule(actor_and, [actor, comma, actor_and]),
    Rule(actor_and, [actor, actor_and]),
    Rule(actor_or, [or_, comma, actor]),
    Rule(actor_or, [or_, actor]),
    Rule(actor_or, [actor, comma, actor_or]),
    Rule(actor_or, [actor, actor_or]),
]
gram = Grammar(rules)
gram.compile()

def tokenize(sentence):
    return list(re.findall(r'(?:\w+)|(?:,)', sentence))

#run test
print "Ready."
while True:
    sentence = raw_input().strip().upper()
    if sentence in ["QUIT", "Q", "EXIT"]:
        exit()
    words = tokenize(sentence)
    stream = WordStream(words)
    parser = Parser(stream, gram)
    trees = []
    for interp in parser.parse_all():
        if not stream.finished():
            continue
        trees.append(interp.to_parse_tree())
    if trees:
        trees.sort(key=lambda x:x.get_info_content())
        if len(trees)==1:
            print trees[0]
        else:
            for tree in trees[:3]:
                print "*"*70
                print "Info Content: %f"%tree.get_info_content()
                print tree
            print "*"*70
    else:
        print "No valid interpretations found."
