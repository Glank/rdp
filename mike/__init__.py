import named
import question
import tokenize

from rdp import WordStream, Parser

class Mike:
    def __init__(self, configs):
        self.configs = configs
        self.names = named.NamedEntityCollection(
            self.configs['named_entity_types']
        )
        self.questions = question.QuestionCollection(
            self.configs['question_types']
        )
        self.tokenizer = tokenize.get_tokenizer(self.configs['tokenizer'])
    def build(self, rebuild=False):
        self.names.build(rebuild=rebuild)
    def _grammar_(self):
        return self.questions.grammar(self.names)
    def get_sparql(self, sentence, verbose=False):
        words = self.tokenizer.tokenize(sentence)
        stream = WordStream(words)
        parser = Parser(stream, self._grammar_())
        trees = []
        for interp in parser.parse_all():
            if not stream.finished():
                continue
            trees.append(interp.to_parse_tree())
        if not trees:
            return None
        best_interp = min(trees, key=lambda x:x.get_info_content())
        if verbose:
            print "Best Interpretation:"
            print best_interp
        return self.questions.get_sparql(best_interp, self.names)
