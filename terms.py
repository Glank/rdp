from grammar import *
from streams import *
from rdparse import *

class StringTerminal(TerminalSymbol):
    def try_consume(self, stream):
        assert(isinstance(stream, StringStream))
        if stream.has(self.name):
            return [len(self.name)]
        return False

class RepeatTerminal(TerminalSymbol):
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
        else:
            code = '{%d,%d}'%(self.minimum,self.maximum)
        if not self.gready:
            code+='?'
        return str(self.term)+code
    def __init__(self, term, minimum=0, maximum=None, gready=True):
        assert(term.is_terminal())
        self.term = term
        self.minimum = minimum
        self.maximum = maximum
        self.gready = gready
        TerminalSymbol.__init__(self, RepeatTerminal.__str__(self))
    def try_consume(self, stream):
        S = Symbol('S')
        rules = [
            Rule(S,[]),
            Rule(S,[self.term, S]),
        ]
        if self.gready:
            rules.reverse()
        subgram = Grammar(rules)
        substream = stream.substream()
        subparser = RDParser(substream, subgram)
        print subparser
        print subgram
        print substream
        print subparser.parse_partial()
        print subparser
        subparser = RDParser(substream, subgram)
        def ret():
            for p in subparser.parse_all():
                if self.minimum<=p.parsed_terminals<=self.maximum:
                    yield p.stream.index
        return ret()
