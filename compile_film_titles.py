#!/usr/bin/env python 
import json
from ngrams import *
import re

def compile():
    with open('clusters/film_titles', 'r') as f:
        cl = pickle.load(f)
    clusters = cl.getlevel(.895)

    names = []
    with open('sample_data/film_titles.json', 'r') as f:
        j = json.load(f)
        for b in j['results']['bindings']:
            name = b['title']['value'].upper()
            name = ''.join(re.findall('[A-Z0-9]+',name))
            names.append(name)

    filt = NGClusterFilter(3, clusters)   
    for name in names:
        if name not in cl._input:
            filt.add(name)
    filt.update_bounds()
    filt.add_allowance(.05)
    filt.clean()
    with open('ngpols/film_titles','wb') as f:
        filt.tofile(f)
    print "compiled."

def test():
    with open('ngpols/film_titles', 'rb') as f:
        titles = NGClusterFilter.fromfile(f)
    print "Enter a title:"
    def testname(name, filt):
        if name in filt:
            print "Yup, that is a film title."
        else:
            print "That wasn't a film title."
    while True:
        name = ''.join(re.findall('[A-Z0-9]+',raw_input().upper()))
        testname(name, titles)

if __name__=='__main__':
    compile()
    test()
