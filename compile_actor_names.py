#!/usr/bin/env python 
import json
from pybloom import BloomFilter
from ngrams import *
import re

def compile():
    names = []
    bloom = BloomFilter(capacity=2494)
    with open('sample_data/actor_names.json', 'r') as f:
        j = json.load(f)
        for b in j['results']['bindings']:
            name = b['name']['value'].upper()
            name = ''.join(re.findall('[A-Z0-9]+',name))
            names.append(name)
            bloom.add(name)

    names = list(set(names))
    filt = NGPOLFilter(3, names, false_neg_rate=.4)
    filt.update_bounds()
    filt.clean()
    with open('blooms/actor_names','wb') as f:
        bloom.tofile(f)
    with open('ngpols/actor_names','wb') as f:
        filt.tofile(f)
    print "compiled."

def test():
    with open('blooms/actor_names', 'rb') as f:
        bloom = BloomFilter.fromfile(f)
    with open('ngpols/actor_names', 'rb') as f:
        ngpol = NGPOLFilter.fromfile(f)
    print "Enter a title:"
    def testname(name, filt):
        if name in filt:
            print "Yup, that is an actor's name."
        else:
            print "That wasn't an actor's name."
    while True:
        name = ''.join(re.findall('[A-Z0-9]+',raw_input().upper()))
        print "Bloom:"
        testname(name, bloom)
        print "NGOPL:"
        testname(name, ngpol)

if __name__=='__main__':
    compile()
    test()
