from rdp import *

class QuestionType:
    """You must define a constructor which takes 
    no arguments and calls this constructor with 
    a hard-coded name."""
    def __init__(self, name):
        self.name = name
        self._symbol_ = None
    def symbol(self):
        if self._symbol_:
            return self._symbol_
        self._symbol_ = Symbol(self.name)
        return self._symbol_
    def rules(self, root, named_entities):
        head = self.symbol()
        rulez = [Rule(root, [head])]
        for tail in self.rule_tails(named_entities):
            rulez.append(Rule(head, tail))
        return rulez
    def rule_tails(self, named_entities):
        """Returns a list of parse rule right sides
        which will be used to create the grammar."""
        raise NotImplementedError()
    def get_sparql(self, parse_tree, named_entities):
        """Returns a SPARQL string given a parse tree root
        with pre-identified named entity nodes."""
        raise NotImplementedError()

def __get_question_type__(configs):
    mod_name = configs['module']
    class_name = configs['class']
    mod = __import__(mod_name, globals(), locals(), [class_name], -1)
    clazz = getattr(mod, class_name)
    return clazz()

def __preidentify_parse_tree__(parse_tree, named_entities):
    class NextNode(Exception):
        pass
    for node in parse_tree.iter_nodes():
        try:
            for entity in named_entities:
                if node.symbol==entity.symbol():
                    name = ' '.join(node.instance.obj)
                    full_name, uri = entity.identifier.ident(name)
                    node.instance = (name, full_name, uri)
                    raise NextNode()
        except NextNode:
            pass

class QuestionCollection:
    def __init__(self, configs):
        self.questions = []
        for config in configs:
            question = __get_question_type__(config)
            self.questions.append(question)
    def grammar(self, named_entities):
        root = Symbol('S')
        rules = []
        for question in self.questions:
            rules.extend(question.rules(root, named_entities))
        g = Grammar(rules)
        g.compile()
        return g
    def get_sparql(self, parse_tree, named_entities):
        for question in self.questions:
            sub_tree = parse_tree.find_node(
                lambda n:n.symbol==question.symbol()
            )
            if sub_tree:
                __preidentify_parse_tree__(
                    parse_tree, named_entities
                )
                return question.get_sparql(sub_tree, named_entities)
        raise Exception("Invalid parse tree.")
