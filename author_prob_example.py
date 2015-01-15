#!/usr/bin/env python 
from rdp import *
from ngrams import *
from edits import *
from distribute import *
from author_query import generate_sparql
from SPARQLWrapper import SPARQLWrapper, JSON
import json

#initialize author probset
with open('probsets/author_names', 'rb') as f:
    author_probset1 = NgramProbSet.fromfile(f)
with open('probsets/author_names_len', 'rb') as f:
    author_probset2 = LengthProbSet.fromfile(f)
author_probset = JoinedProbabilitySet([author_probset1, author_probset2])

#setup the grammar
S = Symbol('S')

bibliography_request = Symbol('bibliography_request')

what = WordTerminal('WHAT')
books = WordTerminal('BOOKS')
has = WordTerminal('HAS')

author = ProbabilitySetTerminal('author', author_probset, max_words=3)

writen = WordTerminal('WRITEN')

rules = [
    Rule(S, [bibliography_request]),
    Rule(bibliography_request, [what, books, has, author, writen]),
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
            query = generate_sparql(trees[0])
            print query
            if query:
                sparql = SPARQLWrapper("http://dbpedia.org/sparql")
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                for binding in results['results']['bindings']:
                    print binding
        else:
            for tree in trees[:3]:
                print "*"*70
                print "Info Content: %f"%tree.get_info_content()
                print tree
            print "*"*70
    else:
        print "No valid interpretations found."
