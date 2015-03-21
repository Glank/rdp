from rdp import *
import sparql as s

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
    """Something to plug into the config file which produces an uncompiled grammar."""
    def grammar(self, named_entities):
        raise NotImplementedError()

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

class SPARQLGenerator:
    def __init__(self, configs):
        self.grammar_factory = __dynamic_obj_load__(configs['grammar_factory'])
        self.construction_rules = []
        for config in configs['construction_rules']:
            construction_rule = __dynamic_obj_load__(config)
            #assert isinstance(construction_rule, QueryConstructionRule)
            self.construction_rules.append(construction_rule)
        #assert isinstance(self.grammar_factory, GrammarFactory)
    def grammar(self, named_entities, verbose=False):
        g = self.grammar_factory.grammar(named_entities)
        if verbose:
            print g
        g.compile()
        return g
    def get_sparql(self, parse_tree, named_entities):
        __preidentify_parse_tree__(parse_tree, named_entities)
        cur_node = parse_tree
        iter_path = []
        context = {'named_entities':named_entities}
        query = s.SPARQLQuery()
        def consume(node):
            for rule in self.construction_rules:
                if rule.consume(node, query, context):
                    return True
            return False
        forceTerm = False
        while True:
            forceTerm = False
            if consume(cur_node):
                forceTerm = True
            #GOTO Next
            if cur_node.children and not forceTerm:
                iter_path.append(cur_node.children[:])
                cur_node = iter_path[-1].pop(0)
            else:
                while iter_path and not iter_path[-1]:
                    iter_path.pop()
                if iter_path:
                    cur_node = iter_path[-1].pop()
                else:
                    cur_node = None
                    break
        return str(query)
