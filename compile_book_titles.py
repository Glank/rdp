#!/usr/bin/env python 
import json
from ngrams import *
from distribute import *
import re

def compile():
    with open('clusters/book_titles', 'r') as f:
        cl = pickle.load(f)
    clusters = cl.getlevel(.895)

    names = []
    with open('sample_data/dbpedia_books.json', 'r') as f:
        j = json.load(f)
        for b in j['results']['bindings']:
            name = b['name']['value'].upper()
            name = ''.join(re.findall('[A-Z0-9]+',name))
            names.append(name)

    filt = NGClusterFilter(3, clusters)   
    for name in names:
        if name not in cl._input:
            filt.add(name)
    filt.update_bounds()
    filt.add_allowance(.05)
    filt.clean()
    with open('ngpols/book_titles','wb') as f:
        filt.tofile(f)

    #create prob sets
    probset = NgramProbSet(3,names)
    probset2 = LengthProbSet(names)
    with open('probsets/book_titles', 'wb') as f:
        probset.tofile(f)
    with open('probsets/book_titles_len', 'wb') as f:
        probset2.tofile(f)

    print "compiled."

def test():
    with open('ngpols/book_titles', 'rb') as f:
        titles = NGClusterFilter.fromfile(f)
    with open('probsets/book_titles', 'rb') as f:
        probset = NgramProbSet.fromfile(f)
    print "Enter a title:"
    def testname(name, filt):
        if name in filt:
            print "Yup, that is a book title."
            if isinstance(filt, ProbabilitySet):
                print filt.getProbability(name)
        else:
            print "That wasn't a book title."
    while True:
        name = ''.join(re.findall('[A-Z0-9]+',raw_input().upper()))
        print "Cluster:"
        testname(name, titles)
        print "Probset:"
        testname(name, probset)

if __name__=='__main__':
    compile()
    test()
