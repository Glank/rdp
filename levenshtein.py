import math

def levenshtein(str1, str2):
    str1 = list(str1)
    str2 = list(str2)
    d = [[0 for j in xrange(len(str2)+1)] for i in xrange(len(str1)+1)]
    for i in xrange(1, len(str1)+1):
        d[i][0] = i
    for j in xrange(1, len(str2)+1):
        d[0][j] = j
    for j in xrange(1, len(str2)+1):
        for i in xrange(1, len(str1)+1):
            if str1[i-1] == str2[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = min(d[i-1][j], d[i][j-1], d[i-1][j-1])+1
    return d[-1][-1]

def __iter_ngrams__(string, n):
    full = '\x02'*(n-1)
    full+= string
    full+= '\x03'*(n-1)
    for i in xrange(0,len(full)-n+1):
        yield full[i:i+n]

def ngram_model(strings, n):
    ngram_counts = {}
    total = 0
    for string in strings:
        for gram in __iter_ngrams__(string, n):
            count = ngram_counts.get(gram, 0)
            ngram_counts[gram] = count+1
            total+=1
    return (ngram_counts, total)

def prob(gram, ngram_model):
    count = ngram_model[0].get(gram, 0)
    total = ngram_model[1]
    return (count+1.)/(total+2.)

def info(gram, ngram_model):
    p = prob(gram,ngram_model)
    return -math.log(p)

def info_ngram_dist(n, str1, str2, model):
    counts_1 = {}
    counts_2 = {}
    all_set = set()
    for gram in __iter_ngrams__(str1, n):
        all_set.add(gram)
        counts_1[gram] = counts_1.get(gram, 0)+1
    for gram in __iter_ngrams__(str2, n):
        all_set.add(gram)
        counts_2[gram] = counts_2.get(gram, 0)+1
    num, denom = 0.0, 0.0
    for gram in all_set:
        i = info(gram,model)
        num+= min(counts_1.get(gram,0), counts_2.get(gram,0))*i
        denom+= max(counts_1.get(gram,0), counts_2.get(gram,0))*i
    return 1.0-(num/denom)

names = [
    'adam smith',
    'bob smith',
    'carl smith',
    'dale jones',
    'ernest kirstein'
]

import ngrams
to_compare = [
    'tom smith',
    'john smith',
    'tom'
]
#to_compare = ['rj smith', 'rj', 'cs smith']
def run_comps(f, to_compare):
    for i,s1 in enumerate(to_compare):
        for s2 in to_compare[i+1:]:
            print f(s1,s2), repr(s1), repr(s2)

print "Without Info:"
d = lambda a,b: ngrams.jaccard_ngram_dist(a,b,3)
run_comps(d, to_compare)

print "\nSample Set:"
print '\t'+'\n\t'.join(names)
model = ngram_model(names, 3)

print "\nWith Info:"
d = lambda a,b: info_ngram_dist(3,a,b,model)
run_comps(d, to_compare)
