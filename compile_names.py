#!/usr/bin/env python 
import csv
from pybloom import BloomFilter
import pickle

def compile():
    boys = BloomFilter(capacity=703)
    girls = BloomFilter(capacity=1003)

    with open('sample_data/names.csv', 'r') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            if float(row[2])<.0005:
                continue
            if row[3].lower() == 'boy':
                boys.add(row[1].lower())
            elif row[3].lower() == 'girl':
                girls.add(row[1].lower())

    with open('blooms/boys', 'w') as f:
        boys.tofile(f)
    with open('blooms/girls', 'w') as f:
        girls.tofile(f)
    print len(boys), len(girls)

def test():
    with open('blooms/boys', 'r') as f:
        boys = BloomFilter.fromfile(f)
    with open('blooms/girls', 'r') as f:
        girls = BloomFilter.fromfile(f)

    print "Enter a name:"
    while True:
        name = raw_input().strip().lower()
        if name in boys and name not in girls:
            print "That is a boy's name."
        elif name not in boys and name in girls:
            print "That is a girl's name."
        elif name in boys and name in girls:
            print "That could be either a boy's or a girl's name."
        else:
            print "That doesn't look like a boy's or a girl's name."

if __name__=="__main__":
    compile()
