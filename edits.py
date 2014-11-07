from pybloom import BloomFilter

alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
#http://norvig.com/spell-correct.html
def edits1(word, alphabet=alphabet):
   splits     = [(word[:i], word[i:]) for i in xrange(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def edits(n, word, alphabet=alphabet):
    assert(n>=1)
    edit_set = set(word)
    fringe = [(w,1) for w in edits1(word, alphabet=alphabet) if w not in edit_set]
    while fringe:
        w,d = fringe.pop()
        edit_set.add(w)
        if d<n:
            for e in edits1(w, alphabet=alphabet):
                if e not in edit_set:
                    fringe.append((e,d+1))
    return edit_set

class FuzzySpellingSet:
    def __init__(self, max_edits, alphabet=alphabet):
        self.max_edits = max_edits
        self.alphabet = alphabet
    def _has_exact_word_(self, word):
        """Returns true if the exact word 'word' is in
        this set."""
        raise NotImplementedException
    def __contains__(self, word):
        for e in edits(self.max_edits, word, alphabet=self.alphabet):
            if self._has_exact_word_(e):
                return True
        return False

class BloomFSS(FuzzySpellingSet):
    def __init__(self, bloom, max_edits, alphabet=alphabet):
        self.bloom = bloom
        FuzzySpellingSet.__init__(self, max_edits, alphabet)
    def _has_exact_word_(self, word):
        return word in self.bloom
    def tofile(self, f):
        pickle.dump(self.max_edits, f)
        pickle.dump(self.alphabet, f)
        self.bloom.tofile(f)
    @staticmethod
    def fromfile(f):
        inst = BloomFFS(None, 0)
        inst.max_edits = pickle.load(f)
        inst.alphabet = pickle.load(f)
        inst.bloom = BloomFilter.fromfile(f)

class OrSet:
    def __init__(self, sets):
        self.sets = sets
    def __contains__(self, obj):
        return any((obj in s) for s in self.sets)
