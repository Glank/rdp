#!/usr/bin/env python 
from ngrams import *
import re

__CUTOFF__ = .1

def prompt_possibles(orig, possibles):
    print "By '%s' did you mean:"%orig
    for i, (name, uri) in enumerate(possibles):
        print "%d)\t%s"%((i+1),name)
    print "%d)\tNone of the above."%(len(possibles)+1)
    valid = False
    n = 0
    while not valid:
        valid = True
        try:
            n = int(raw_input())
        except Exception:
            valid = False
        if not 1<=n<=len(possibles)+1:
            valid = False
    if n-1==len(possibles):
        return None
    return possibles[n-1]

def ident_actor(name, pp=prompt_possibles):
    orig_name = name
    name = ''.join(re.findall('[A-Z0-9]+',name.upper()))
    best_actors = []
    with open('sample_data/actor_names.json', 'r') as f:
        j = json.load(f)
        for b in j['results']['bindings']:
            actor_orig = b['name']['value']
            uri = b['actor']['value']
            actor = b['name']['value'].upper()
            actor = ''.join(re.findall('[A-Z0-9]+',actor))
            dist = jaccard_ngram_dist(name,actor,3)
            best_actors.append(((actor_orig,uri),dist))
            if len(best_actors)>20:
                best_actors.sort(key=lambda x:x[1])
                best_actors = best_actors[:5]
    best_actors.sort(key=lambda x:x[1])
    best_actors = best_actors[:5]
    best_dist = best_actors[0][1]
    possibles = [best_actors[0][0]]
    for actor, dist in best_actors[1:]:
        percent_diff = (dist-best_dist)*2/float(dist+best_dist)
        if percent_diff < __CUTOFF__:
            possibles.append(actor)
    if len(possibles)>1:
        identified = pp(orig_name, possibles)
    else:
        identified = possibles[0]
    return identified

def test():
    test_values = [
        "David Blane", "Swartzeneger", 
        "Jacky Chan", "Notaname"
    ]
    for test in test_values:
        print "\nIdentifying '%s'..."%test
        print ident_actor(test)
    while True:
        print "\nTry inputing a name. (or 'q' to exit)"
        name = raw_input()
        if name=='q':
            break
        print ident_actor(name)

if __name__=='__main__':
    test()
