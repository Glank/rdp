from grammar import *
from streams import *
from parser import *

class StringTerminal(TerminalSymbol):
    def try_consume(self, stream):
        assert(isinstance(stream, StringStream))
        if stream.has(self.name):
            return [(len(self.name),self.name)]
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
        TerminalSymbol.__init__(self, str(self))
    def subgrammar(self):
        return self.subgram
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
        else:
            code = '{%d,%d}'%(self.minimum,self.maximum)
        if not self.gready:
            code+='?'
        return str(self.term)+code
