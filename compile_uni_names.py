#!/usr/bin/env python 
import csv
from pybloom import BloomFilter
from ngrams import *
import re

def compile():
    uni_names = BloomFilter(capacity=719)
    name_strings = []
    with open('sample_data/uni_names.out', 'r') as f:
        for line in f:
            m = re.search(r'\| "(.*)"$', line.strip())
            if m:
                name = m.group(1).strip().lower()
                name_strings.append(name)
                uni_names.add(name)
    ngpol_filt = NGPOLFilter(4, name_strings)
    for name in name_strings:
        if name not in ngpol_filt:
            print name
    print ngpol_filt.min_rating
    print ngpol_filt.deviation
    ngpol_filt.clean()
    with open('blooms/uni_names','w') as f:
        uni_names.tofile(f)
    with open('ngpols/uni_names','w') as f:
        ngpol_filt.tofile(f)
    print len(uni_names)

def compile_clusters():
    with open('clusters/uni_names_200', 'r') as f:
        cl = pickle.load(f)
    clusters = cl.getlevel(.33)
    names = []
    with open('sample_data/uni_names.out', 'r') as f:
        for line in f:
            m = re.search(r'\| "(.*)"$', line.strip())
            if m:
                name = m.group(1).strip().lower()
                names.append(name)
    filt = NGClusterFilter(3, clusters)   
    for name in names:
        if name not in filt:
            filt.add(name)
    filt.update_bounds()
    filt.add_allowance(.33)
    filt.print_stats()
    filt.clean()
    with open('ngpols/uni_names_cluster','w') as f:
        filt.tofile(f)

def test():
    with open('blooms/uni_names', 'r') as f:
        uni_names = BloomFilter.fromfile(f)
    with open('ngpols/uni_names', 'r') as f:
        uni_names_2 = NGPOLFilter.fromfile(f)
    with open('ngpols/uni_names_cluster', 'r') as f:
        uni_names_3 = NGClusterFilter.fromfile(f)
    print "Enter a name:"
    def testname(name, filt):
        if name in filt:
            print "Yup, that name was in the owl doc."
        else:
            print "That name wasn't in the owl doc."
    while True:
        name = raw_input().strip().lower()
        print "Bloom:"
        testname(name, uni_names)
        print "NGOPL:"
        testname(name, uni_names_2)
        print "NGCluster:"
        testname(name, uni_names_3)
        print

if __name__=="__main__":
    compile()
    compile_clusters()
    test()
