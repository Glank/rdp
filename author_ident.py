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

def ident_author(name, pp=prompt_possibles):
    orig_name = name
    name = ''.join(re.findall('[A-Z0-9]+',name.upper()))
    best_authors = []
    with open('sample_data/author_names.json', 'r') as f:
        j = json.load(f)
        for b in j['results']['bindings']:
            author_orig = b['name']['value']
            uri = b['author']['value']
            author = b['name']['value'].upper()
            subnames = author_orig.split()
            author = ''.join(re.findall('[A-Z0-9]+',author))
            dist = jaccard_ngram_dist(name,author,3)
            best_authors.append(((author_orig,uri),dist))
            if len(subnames)>=2:
                for sname in [subnames[0], subnames[-1]]:
                    sname = ''.join(re.findall('[A-Z0-9]+',sname))
                    dist = jaccard_ngram_dist(name,sname,3)
                    best_authors.append(((author_orig,uri),dist))
            if len(best_authors)>20:
                best_authors.sort(key=lambda x:x[1])
                best_authors = best_authors[:5]
    best_authors.sort(key=lambda x:x[1])
    best_authors = best_authors[:5]
    best_dist = best_authors[0][1]
    possibles = [best_authors[0][0]]
    for author, dist in best_authors[1:]:
        percent_diff = (dist-best_dist)*2/float(dist+best_dist)
        if percent_diff < __CUTOFF__:
            possibles.append(author)
    if len(possibles)>1:
        identified = pp(orig_name, possibles)
    else:
        identified = possibles[0]
    return identified

def test():
    test_values = [
        "Paolini", "JK Rowling", 
        "Cristopher Paolini",
        "Robert Heinline"
    ]
    for test in test_values:
        print "\nIdentifying '%s'..."%test
        print ident_author(test)
    while True:
        print "\nTry inputing a name. (or 'q' to exit)"
        name = raw_input()
        if name=='q':
            break
        print ident_author(name)

if __name__=='__main__':
    test()
