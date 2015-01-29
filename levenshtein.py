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

import ngrams
to_compare = [
    'global kirstein investing',
    'kirstein global investing',
    'scherl global investing'
]
to_compare = ['rj smith', 'rj', 'cs smith']
def run_comps(f, to_compare):
    for i,s1 in enumerate(to_compare):
        for s2 in to_compare[i+1:]:
            print f(s1,s2), repr(s1), repr(s2)

print "Levenshtein:"
run_comps(levenshtein, to_compare)

print "\nJaccard w/3-grams:"
jac = lambda a,b:ngrams.jaccard_ngram_dist(a,b,3)
run_comps(jac, to_compare)
