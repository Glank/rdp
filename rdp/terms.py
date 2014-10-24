from grammar import *
from streams import *
from parser import *
import re
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Synset

class InclusionSetTerminal(TerminalSymbol):
    def __init__(self, name, inc_set, max_words=1):
        self.inc_set = inc_set
        self.max_words = max_words
        TerminalSymbol.__init__(self, name)
    def try_consume(self, stream):
        assert(isinstance(stream, WordStream))
        for n in xrange(1,self.max_words+1):
            words = stream.peek_many(n)
            if words is None:
                return False
            w = ''.join(w.lower() for w in words)
            if w in self.inc_set:
                return [(n,words)]
        return False

#SHTL = Synset Hyponym Tree Lemmas
class SHTLTerminal(TerminalSymbol):
    def __init__(self, word, pos=None):
        morphy = wn.morphy(word)
        synsets = wn.synsets(morphy, pos=pos)
        hypo = lambda x: x.hyponyms()
        def iter_flatten(tree):
            if isinstance(tree, list):
                for branch in tree:
                    for item in iter_flatten(branch):
                        yield item
            else:
                yield tree
        def lemma_hypo_tree(synset):
            for t in synset.tree(hypo):
                for s in iter_flatten(t):
                    for l in s.lemmas():
                        yield l.name().lower()
        self.lemmas = set()
        self.max_words = 1
        for synset in synsets:
            for l in lemma_hypo_tree(synset):
                if l not in self.lemmas:
                    self.lemmas.add(l)
                    words = l.count('_')+1
                    if words > self.max_words:
                        self.max_words=words
        TerminalSymbol.__init__(self, word)
    def try_consume(self, stream):
        assert(isinstance(stream, WordStream))
        for n in xrange(1,self.max_words+1):
            words = stream.peek_many(n)
            if words is None:
                return False
            w = '_'.join(w.lower() for w in words)
            if w in self.lemmas:
                return [(n,w)]
            morphy = wn.morphy(w)
            if morphy in self.lemmas:
                return [(n,w)]
        return False

class StringTerminal(TerminalSymbol):
    def try_consume(self, stream):
        assert(isinstance(stream, StringStream))
        if stream.has(self.name):
            return [(len(self.name),self.name)]
        return False
    def __str__(self):
        return repr(self.name)

class RegexTerminal(TerminalSymbol):
    def __init__(self, regex, flags=0, name=None):
        self.regex_string = regex
        self.flags = flags
        self.regex = re.compile(regex, flags=flags)
        if name is None:
            name = "/%s/"%(regex.replace('\n','\\n'))
            if self.flags&re.M:
                name+='m'
            if self.flags&re.I:
                name+='i'
            if self.flags&re.S:
                name+='s'
        TerminalSymbol.__init__(self, name)
    def try_consume(self, stream):
        assert(isinstance(stream, StringStream))
        m = self.regex.match(stream.get_buffer())
        if not m:
            return False
        match = m.groups()
        return [(len(m.group(0)), match)]
    def __str__(self):
        return self.name
    def __deepcopy__(self, memo):
        return RegexTerminal(
            deepcopy(self.regex_string,memo),
            flags=deepcopy(self.flags,memo),
            name=deepcopy(self.name,memo)
        )

class KeywordTerminal(RegexTerminal):
    def __init__(self, keyword, case_sensitive=False):
        RegexTerminal.__init__(
            self,
            r'(\w+)',
            name = keyword
        )
        self.case_sensitive = case_sensitive
    def try_consume(self, stream):
        potential_ret = RegexTerminal.try_consume(self, stream)
        if potential_ret is False:
            return False
        assert(len(potential_ret)==1)
        length, match = potential_ret[0]
        assert(len(match)==1)
        if self.case_sensitive:
            if match[0]==self.name:
                return [(length, match[0])]
        else:
            if match[0].lower()==self.name.lower():
                return [(length, match[0])]
        return False
    def __deepcopy__(self, memo):
        return KeywordTerminal(
            deepcopy(self.name,memo),
            case_sensitive=deepcopy(self.case_sensitive,memo)
        )

class WordTerminal(TerminalSymbol):
    def try_consume(self, stream):
        assert(isinstance(stream, WordStream))
        if stream.has(self.name):
            return [(1,[self.name])]
        return False

class RepeatTerminal(ComplexTerminalSymbol):
    def __init__(self, term, minimum=0, maximum=None, gready=True):
        assert(term.is_terminal())
        self.term = term
        self.minimum = minimum
        self.maximum = maximum
        self.gready = gready
        S = Symbol(str(self))
        rules = [
            Rule(S,[]),
            Rule(S,[self.term, S]),
        ]
        if self.gready:
            rules.reverse()
        self.subgram = Grammar(rules, start=S)
        ComplexTerminalSymbol.__init__(self, str(self), self.subgram)
    def try_consume(self, stream):
        substream = stream.substream()
        subparser = Parser(substream, self.subgram)
        def ret():
            for p in subparser.parse_all():
                n = p.parsed_terminals-1
                if self.minimum<=n<=self.maximum:
                    yield p.stream.index,p
        return ret()
    def __str__(self):
        if self.maximum is None:
            if self.minimum==0:
                code = '*'
            elif self.minimum==1:
                code = '+'
            else:
                code = '{%d,}'%self.minimum
        elif self.maximum==1 and self.minimum==0:
            code = '?'
        elif self.minimum==self.maximum:
            code = '{%d}'%self.minimum
        else:
            code = '{%d,%d}'%(self.minimum,self.maximum)
        if not self.gready:
            code+='?'
        return str(self.term)+code
