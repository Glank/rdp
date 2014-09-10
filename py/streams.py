from grammar import *

class ParsingStream:
    def reset(self):
        """Resets the stream to the very beginning."""
        raise NotImplementedError()
    def advance(self, amount):
        """Advances the stream. Returns <amount>
        elements that were passed."""
        raise NotImplementedError()
    def backtrack(self, amount):
        """Goes backwards in the stream <amount> elements.
        Calling s.advance(a) then s.backtrack(a) should
        result in the s being exactly the same."""
        raise NotImplementedError()
    def substream(self):
        """Returns a stream that appears to be this stream
        with all elements before the current index cut off."""
        raise NotImplementedError()

class StringStream(ParsingStream):
    def __init__(self, string, off=0):
        self.string = string
        self.index = 0
        self.off = off
    def has(self, word):
        if (self.index+len(word)+self.off)>len(self.string):
            return False
        return self.string[self.off+self.index:].startswith(word)
    def advance(self, amount):
        self.index+=amount
        assert(self.index+self.off<=len(self.string))
        return self.string[self.index+self.off-amount:self.index+self.off]
    def backtrack(self, amount):  
        self.index-=amount
        assert(self.index>=0)
    def finished(self):
        return self.index+self.off==len(self.string)
    def reset(self):
        self.index = 0
    def substream(self):
        return StringStream(self.string, off=self.index)
    def __str__(self):
        return self.string[self.off:]

class WordStream(ParsingStream):
    def __init__(self, words, off=0):
        self.words = words
        self.index = 0
        self.off = off
    def has(self, word):
        if (self.index+self.off+1)>len(self.words):
            return False
        return self.words[self.off+self.index]==word
    def advance(self, amount):
        self.index+=amount
        assert(self.index+self.off<=len(self.words))
        return self.words[self.index+self.off-amount:self.index+self.off]
    def backtrack(self, amount):  
        self.index-=amount
        assert(self.index>=0)
    def finished(self):
        return self.index+self.off==len(self.words)
    def reset(self):
        self.index = 0
    def substream(self):
        return StringStream(self.words, off=self.index)
    def __str__(self):
        return str(self.words[self.off:])
