#N-Gram Positive Only Learner
import json
import pickle
import hashlib
import numpy as np
import cluster
import zlib

__PRE__ = hashlib.md5('__PRE__').hexdigest()
__POST__ = hashlib.md5('__POST__').hexdigest()

def __iter_ngrams__(n, lst):
    full = [__PRE__]*(n-1)
    full+= list(lst)
    full+= [__POST__]*(n-1)
    for i in xrange(0,len(full)-n+1):
        yield full[i:i+n]

def jaccard_ngram_dist(a,b,n):
    a_counts = {}
    b_counts = {}
    all_set = set()
    for gram in __iter_ngrams__(n, a):
        gram = tuple(gram)
        all_set.add(gram)
        a_counts[gram] = a_counts.get(gram,0)+1
    for gram in __iter_ngrams__(n, b):
        gram = tuple(gram)
        all_set.add(gram)
        b_counts[gram] = b_counts.get(gram,0)+1
    num, denom = 0.0, 0.0
    for gram in all_set:
        num+= min(a_counts.get(gram,0), b_counts.get(gram,0))
        denom+= max(a_counts.get(gram,0), b_counts.get(gram,0))
    return 1.0-(num/denom)

def jaccard_ngram_cluster(input_data, n):
    dist_memo = {}
    def dist_alg(a,b):
        tup = (a,b) if a<b else (b,a)
        if tup not in dist_memo:
            dist = jaccard_ngram_dist(a,b,n)
            dist_memo[tup] = dist
        return dist_memo[tup]
    cl = cluster.HierarchicalClustering(
        input_data, dist_alg
    )
    cl.cluster()
    cl.distance = None
    cl.linkage = None
    return cl

class NGramPOL:
    def __init__(self, n):
        assert(n>=2)
        self.n = n
        self.root = {}
        self.tokens = set([__PRE__, __POST__])
        self.size = 0
    def __get_ngrams__(self, lst):
        for gram in __iter_ngrams__(self.n, lst):
            yield gram
    def add(self, lst):
        self.tokens.update(lst)
        for gram in self.__get_ngrams__(lst):
            self.__add_gram__(gram)
    def rate(self, lst):
        total = 0
        for gram in self.__get_ngrams__(lst):
            total+= self.__count_grams__(gram)
        return (float(total+1)/(len(lst)+self.n+2))/self.size
    def __len__(elf):
        return self.size
    def __add_gram__(self, gram):
        assert(len(gram)==self.n)
        self.size+=1
        node = self.root
        for token in gram[:-1]:
            if token not in node:
                node[token] = {}
            node = node[token]
        node[gram[-1]] = node.get(gram[-1],0)+1
    def __count_grams__(self, gram):
        assert(len(gram)==self.n)
        node = self.root
        for token in gram:
            if token not in node:
                return 0
            node = node[token]
        return node
    def tofile(self, f):
        tpl = (self.tokens, self.n, self.size)
        pickle.dump(tpl, f)
        tree = json.dumps(self.root,f)
        tree = zlib.compress(tree)
        pickle.dump(tree, f)
    @staticmethod
    def fromfile(f):
        ngpol = NGramPOL(2)
        tpl = pickle.load(f)
        ngpol.tokens, ngpol.n, ngpol.size = tpl
        tree = pickle.load(f)
        tree = zlib.decompress(tree)
        ngpol.root = json.loads(tree)
        return ngpol

class NGPOLFilter:
    def __init__(self, n, training_set, false_neg_rate=0.0):
        if n==None:
            return
        self.ngpol = NGramPOL(n)
        for item in training_set:
            self.ngpol.add(item)
        self.training_set = training_set
        self.false_neg_rate = false_neg_rate
        self.update_bounds()
    def update_bounds(self):
        ratings = [self.ngpol.rate(item) for item in self.training_set]
        ratings.sort()
        self.deviation = np.std(ratings)
        min_index = int(self.false_neg_rate*len(self.training_set))
        self.min_rating = ratings[min_index]
    def add_allowance(self, k=0.1):
        assert(0<=k<=1)
        self.min_rating = (1.0-k)*self.min_rating
    def add(self, sample):
        self.ngpol.add(sample)
    def __contains__(self, item):
        return self.ngpol.rate(item)>=self.min_rating
    def clean(self):
        """Removes Unnecessary Build Data"""
        self.training_set = None
    def tofile(self, f):
        pickle.dump(self.min_rating,f)
        pickle.dump(self.deviation,f)
        pickle.dump(self.training_set,f)
        pickle.dump(self.false_neg_rate,f)
        self.ngpol.tofile(f)
    @staticmethod
    def fromfile(f):
        filt = NGPOLFilter(2,[''])
        filt.min_rating = pickle.load(f)
        filt.deviation = pickle.load(f)
        filt.training_set = pickle.load(f)
        filt.false_neg_rate = pickle.load(f)
        filt.ngpol = NGramPOL.fromfile(f)
        return filt

class NGClusterFilter:
    def __init__(self, n, clusters, false_neg_rate=0.0):
        if n==None:
            return
        self.sub_filters = []
        for cluster in clusters:
            sf = NGPOLFilter(n, cluster, false_neg_rate=false_neg_rate)
            self.sub_filters.append(sf)
        self.clusters = clusters
    def add(self, sample):
        best_filter = self.get_best_subfilter(sample)
        best_filter.add(sample)
    def rate(self, sample):
        best_rating = 0
        for sf in self.sub_filters:
            rate = sf.ngpol.rate(sample)
            if rate>best_rating:
                best_rating = rate
        return best_rating
    def get_best_subfilter(self, sample):
        best_filter = None
        best_rateing = 0
        for sf in self.sub_filters:
            rate = sf.ngpol.rate(sample)
            if rate>best_rateing:
                best_rateing = rate
                best_filter = sf
        return best_filter
    def stretch_for(self, sample, delta=.1):
        best_filter = self.get_best_subfilter(sample)
        while sample not in best_filter:
            best_filter.add_allowance(k=delta)
    def update_bounds(self):
        for sf in self.sub_filters:
            sf.update_bounds()
    def add_allowance(self, k=0.1):
        for sf in self.sub_filters:
            sf.add_allowance(k=k)
    def __contains__(self, obj):
        for sf in self.sub_filters:
            if obj in sf:
                return True
        return False
    def print_stats(self):
        if self.clusters:
            print "Clusters:",[c[0] for c in self.clusters]
        mins = []
        devs = []
        for sf in self.sub_filters:
            mins.append(sf.min_rating)
            devs.append(sf.deviation)
        print "Minimum Ratings:",mins
        print "Standard Deviations:",devs
    def clean(self):
        self.clusters = None
        for sf in self.sub_filters:
            sf.clean()
    def tofile(self, f):
        pickle.dump(self.clusters, f)
        pickle.dump(len(self.sub_filters), f)
        for sf in self.sub_filters:
            sf.tofile(f)
    @staticmethod
    def fromfile(f):
        filt = NGClusterFilter(None,None)
        filt.clusters = pickle.load(f)
        subs = pickle.load(f)
        filt.sub_filters = []
        for i in xrange(subs):
            filt.sub_filters.append(NGPOLFilter.fromfile(f))
        return filt

def test():
    import re
    import random
    import traceback
    import json
    names = []
    with open('sample_data/actor_names.json', 'r') as f:
        j = json.load(f)
        for b in j['results']['bindings']:
            name = b['name']['value'].upper()
            name = ''.join(re.findall('[A-Z0-9]+',name))
            names.append(name)
    random.shuffle(names)
    names = list(set(names))[:300]
    cl = jaccard_ngram_cluster(names, 3)
    with open('clusters/actor_names', 'w') as f:
        pickle.dump(cl, f)

def test2():
    import random
    with open('clusters/actor_names', 'r') as f:
        cl = pickle.load(f)
    while True:
        print "Level: ",
        lvl = float(raw_input())
        lvl = cl.getlevel(lvl)
        print len(lvl)
        for c in lvl:
            print random.sample(c,min(len(c),4))

def test3():
    with open('clusters/actor_names', 'r') as f:
        cl = pickle.load(f)
    clusters = cl.getlevel(1)
    import re
    import random
    import traceback
    import json
    names = []
    with open('sample_data/actor_names.json', 'r') as f:
        j = json.load(f)
        for b in j['results']['bindings']:
            name = b['name']['value'].upper()
            name = ''.join(re.findall('[A-Z0-9]+',name))
            names.append(name)
    filt = NGClusterFilter(3, clusters, false_neg_rate=.4)
    for name in names:
        if name not in cl._input:
            filt.add(name)
    filt.update_bounds()
    filt.print_stats()
    while True:
        test = ''.join(re.findall('[A-Z0-9]+',raw_input().upper()))
        print test in filt
        print filt.rate(test)

if __name__=="__main__":
    import sys
    sys.setrecursionlimit(1500)
    test3()
