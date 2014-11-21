from ngrams import NGramPOL
from rdp.terms import ProbabilitySet
import pickle

class SampleDistribution:
    def __init__(self, sample, granularity=None, max_size=5000):
        assert(len(sample)>=2)
        sample.sort()
        min_val, max_val = sample[0], sample[-1]
        #figure out granularity
        if granularity is None:
            granularity = float('inf')
            for i in xrange(1, len(sample)):
                delta = sample[i]-sample[i-1]
                if delta!=0 and delta<granularity:
                    granularity = delta
        #reduce granularity if exceeds max size
        buckets = int((max_val-min_val)/granularity)
        if buckets>max_size:
            granularity = (max_val-min_val)/max_size
            buckets = max_size
        self.buckets = buckets
        #create distribution table
        self.min_val = min_val
        self.max_val = max_val
        self.dist_table = [0]*self.buckets
        self.granularity = granularity
        last_bucket = 0
        for i in xrange(len(sample)):
            v = sample[i]
            bucket = int((v-min_val)/granularity)
            if bucket==self.buckets:
                bucket = self.buckets-1
            #fill skipped buckets
            while last_bucket<bucket:
                last_bucket+=1
                self.dist_table[last_bucket] = float(i)/len(sample)
            self.dist_table[bucket] = float(i+1)/len(sample)
    def cdf(self, x):
        if x<self.min_val:
            return 0.0
        if x>=self.max_val:
            return 1.0
        b = (x-self.min_val)/self.granularity
        left_b = int(b)
        if left_b>=len(self.dist_table)-1:
            return 1.0
        #linear interpolation
        #http://en.wikipedia.org/wiki/Linear_interpolation
        x_0 = float(left_b)
        x_1 = float(left_b+1)
        y_0 = float(self.dist_table[left_b])
        y_1 = float(self.dist_table[left_b+1])
        return y_0+(y_1-y_0)*(b-x_0)/(x_1-x_0)

class NgramProbSet(ProbabilitySet):
    def __init__(self, n, strings):
        if n is None:
            assert(strings is None)
            return
        ngpol = NGramPOL(n)
        for s in strings:
            ngpol.add(s)
        sample = [ngpol.rate(s) for s in strings]
        dist = SampleDistribution(sample)
        self.ngpol = ngpol
        self.dist = dist
    def getProbability(self, string):
        r = self.ngpol.rate(string)
        return self.dist.cdf(r)   
    def tofile(self, f):
        pickle.dump(self.dist, f)
        self.ngpol.tofile(f)
    @staticmethod
    def fromfile(f):
        s = NgramProbSet(None,None)
        s.dist = pickle.load(f)
        s.ngpol = NGramPOL.fromfile(f)
        return s

class LengthProbSet(ProbabilitySet):
    def __init__(self, strings):
        if strings is None:
            return
        sample = [len(s) for s in strings]
        dist = SampleDistribution(sample)
        self.dist = dist
    def getProbability(self, string):
        return self.dist.cdf(len(string))
    def tofile(self, f):
        pickle.dump(self.dist, f)
    @staticmethod
    def fromfile(f):
        s = LengthProbSet(None)
        s.dist = pickle.load(f)
        return s
