import named
import sparql_gen
import tokenize
import copy

from rdp import WordStream, Parser

class Mike:
    def __init__(self, configs):
        self.configs = configs
        self.names = named.NamedEntityCollection(
            self.configs['named_entity_types']
        )
        self.sparql_generator= sparql_gen.SPARQLGenerator(
            self.configs['sparql_generator']
        )
        self.tokenizer = tokenize.get_tokenizer(self.configs['tokenizer'])
    def build(self, rebuild=False):
        self.names.build(rebuild=rebuild)
    def _grammar_(self, verbose=False):
        return self.sparql_generator.grammar(self.names, verbose=verbose)
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
        trees.sort(key=lambda x:x.get_info_content())
        found = False
        for best_interp in trees:
            try:
                self.sparql_generator.get_sparql(
                    copy.deepcopy(best_interp), self.names, True
                )
                found = True
                break
            except sparql_gen.SPARQLGenerationException:
                pass
        if not found:
            return None
        if verbose:
            print "Best Interpretation:"
            print best_interp
        return self.sparql_generator.get_sparql(best_interp, self.names)
