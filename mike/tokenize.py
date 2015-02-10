import re

class Tokenizer:
    def tokenize(self, string):
        """Returns a list of strings from a given string."""
        raise NotImplementedError()

class SimpleTokenizer(Tokenizer):
    def tokenize(self, sentence):
        sentence = sentence.strip().upper()
        return list(re.findall(r'(?:\w+)|(?:,)', sentence))

def get_tokenizer(name):
    if name=="SimpleTokenizer":
        return SimpleTokenizer()
    else:
        raise Exception("Invalid tokenizer: %r"%name)
