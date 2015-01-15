#!/usr/bin/env python 
import json
from pybloom import BloomFilter
from ngrams import *
from distribute import *
import re
import matplotlib.pyplot as plot

def compile():
    names = []
    with open('sample_data/author_names.json', 'r') as f:
        j = json.load(f)
        for b in j['results']['bindings']:
            name = b['name']['value'].upper()
            subnames = name.split()
            name = ''.join(re.findall('[A-Z0-9]+',name))
            names.append(name)
            if len(subnames)>=2:
                for name in [subnames[0], subnames[-1]]:
                    name = ''.join(re.findall('[A-Z0-9]+',name))
                    names.append(name)

    names = list(set(names))

    #create prob sets
    probset = NgramProbSet(3,names)
    probset2 = LengthProbSet(names)
    with open('probsets/author_names', 'wb') as f:
        probset.tofile(f)
    with open('probsets/author_names_len', 'wb') as f:
        probset2.tofile(f)

    print "compiled."

def test():
    with open('probsets/author_names', 'rb') as f:
        probset = NgramProbSet.fromfile(f)
    print "Enter a title:"
    def testname(name, filt):
        if name in filt:
            print "Yup, that is an author's name."
            if isinstance(filt, ProbabilitySet):
                print filt.getProbability(name)
        else:
            print "That wasn't an author's name."
    while True:
        name = ''.join(re.findall('[A-Z0-9]+',raw_input().upper()))
        print "NgramProbSet:"
        testname(name, probset)

if __name__=='__main__':
    compile()
    test()
