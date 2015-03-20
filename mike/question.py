from rdp import *

class QueryConstructionRule:
    """A rule used to build a sparql query."""
    def consume(self, parse_node, query, context):
        """Recieves a parse node with pre-identified named entity nodes
        and a SPARQLQuery that is being built. The context dict stores
        additional information that doesn't go into the query but needs
        to be caried through the construction/search procedure. 
        Returns 'true' if the node is a terminal node in the constrction/search
        procedure. Returns 'false' if the procedure should continue."""
        raise NotImplementedError()

class GrammarFactory:
    """Something to plug into the config file which produces the grammar."""
    def grammar(self):
        raise NotImplementedError()

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
    def rules(self, root, context):
        head = self.symbol()
        rulez = [Rule(root, [head])]
        for tail in self.rule_tails(context):
            rulez.append(Rule(head, tail))
        return rulez
    def rule_tails(self, context):
        """Returns a list of parse rule right sides
        which will be used to create the grammar."""
        raise NotImplementedError()
    def get_sparql(self, parse_tree, context):
        """Returns a SPARQL string given a parse tree root
        with pre-identified named entity nodes."""
        raise NotImplementedError()

class HypotheticalObjectType:
    def __init__(self, name):
        self.name = name
        self._symbol_ = None
    def symbol(self):
        if self._symbol_:
            return self._symbol_
        self._symbol_ = Symbol(self.name)
        return self._symbol_
    def rules(self, context):
        """Returns a lsit of grammar rules that are used
        to recognize this hypothetical object within other
        contexts (so no root is needed)."""
        raise NotImplementedError()
    def get_object(self, parse_tree, context):
        """Returns a HypotheticalObject given a parse tree root
        with pre-identified named entity nodes."""
        raise NotImplementedError()

class HypotheticalObject:
    def __init__(self, hotype):
        self._type_ = _type_
        self.predicate_clauses = []
    def add(self, pred, obj):
        self.predicate_clauses.append((pred,obj))
    def get_sparql_part(self, variable_name):
        """Returns a part of a SPARQL string given a parse tree rooted
        at this symbol and with pre-identified named entity nodes.
        Variable name is a string like '?var' which is a SPARQL variable."""
        sparql = [variable_name, " "]
        for i, (pred, obj) in enumerate(self.predicate_clauses):
            sparql.append("%s %s;")
            if i>0:
                sparql.append("\n")
        return "".join(sparql)

def __dynamic_obj_load__(configs):
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
        self.hqtypes = {}
        for config in configs['question_types']:
            question = __dynamic_obj_load__(config)
            self.questions.append(question)
        for config in configs.get('hypothetical_types',[]):
            hqtype = __dynamic_obj_load__(config)
            self.hqtypes[hqtype.name] = hqtype
    def grammar(self, named_entities, verbose=False):
        context = {
            'named_entities':named_entities,
            'hqtypes':self.hqtypes
        }
        root = Symbol('S')
        rules = []
        for question in self.questions:
            rules.extend(question.rules(root, context))
        g = Grammar(rules)
        if verbose:
            print g
        g.compile()
        return g
    def get_sparql(self, parse_tree, named_entities):
        context = {
            'named_entities':named_entities,
            'hqtypes':self.hqtypes
        }
        for question in self.questions:
            sub_tree = parse_tree.find_node(
                lambda n:n.symbol==question.symbol()
            )
            if sub_tree:
                __preidentify_parse_tree__(
                    parse_tree, named_entities
                )
                return question.get_sparql(sub_tree, context)
        raise Exception("Invalid parse tree.")
