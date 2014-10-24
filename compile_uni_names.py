#!/usr/bin/env python 
import csv
from pybloom import BloomFilter
import re

def compile():
    uni_names = BloomFilter(capacity=719)
    with open('sample_data/uni_names.out', 'r') as f:
        for line in f:
            m = re.search(r'\| "(.*)"$', line.strip())
            if m:
                uni_names.add(m.group(1).strip().lower())
    with open('blooms/uni_names','w') as f:
        uni_names.tofile(f)
    print len(uni_names)

def test():
    with open('blooms/uni_names', 'r') as f:
        uni_names = BloomFilter.fromfile(f)

    print "Enter a name:"
    while True:
        name = raw_input().strip().lower()
        if name in uni_names:
            print "Yup, that name was in the owl doc."
        else:
            print "That name wasn't in the owl doc."

if __name__=="__main__":
    compile()
