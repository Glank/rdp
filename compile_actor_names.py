#!/usr/bin/env python 
import json
from pybloom import BloomFilter
from ngrams import *
from distribute import *
import re
import matplotlib.pyplot as plot

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
    filt = NGPOLFilter(3, names, false_neg_rate=.01)
    filt.update_bounds()
    filt.clean()
    #create rating histogram
    ratings = [filt.ngpol.rate(n) for n in names]
    plot.hist(ratings, bins=50)
    plot.xlabel("NGram Rating")
    plot.ylabel("Names")
    plot.savefig("imgs/actor_names.png")
    plot.show()
    with open('blooms/actor_names','wb') as f:
        bloom.tofile(f)
    with open('ngpols/actor_names','wb') as f:
        filt.tofile(f)

    #create prob sets
    probset = NgramProbSet(3,names)
    probset2 = LengthProbSet(names)
    with open('probsets/actor_names', 'wb') as f:
        probset.tofile(f)
    with open('probsets/actor_names_len', 'wb') as f:
        probset2.tofile(f)

    print "compiled."

def test():
    with open('blooms/actor_names', 'rb') as f:
        bloom = BloomFilter.fromfile(f)
    with open('ngpols/actor_names', 'rb') as f:
        ngpol = NGPOLFilter.fromfile(f)
    with open('probsets/actor_names', 'rb') as f:
        probset = NgramProbSet.fromfile(f)
    print "Enter a title:"
    def testname(name, filt):
        if name in filt:
            print "Yup, that is an actor's name."
            if isinstance(filt, ProbabilitySet):
                print filt.getProbability(name)
        else:
            print "That wasn't an actor's name."
    while True:
        name = ''.join(re.findall('[A-Z0-9]+',raw_input().upper()))
        print "Bloom:"
        testname(name, bloom)
        print "NGOPL:"
        testname(name, ngpol)
        print "NgramProbSet:"
        testname(name, probset)

if __name__=='__main__':
    compile()
    test()
