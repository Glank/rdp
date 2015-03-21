from mike.sparql_gen import *
from mike.sparql import *
from mike.named import *
import re

### Grammar Definition ###

#Simple Terminals
who = WordTerminal('WHO')
what = InclusionSetTerminal('WHAT', set('WHAT WHICH'.split()), max_words=1)
has = InclusionSetTerminal('HAS', 
    set('HAVE,HAS,WILL,WILL HAVE,DONE'.split(',')), 
    max_words=2
)
_and = WordTerminal('AND')
_or = WordTerminal('OR')
_a = WordTerminal('A')
both = WordTerminal('BOTH')

#SHTL Terminals
author = SHTLTerminal('AUTHOR', pos='n')
book = SHTLTerminal('BOOKS', pos='n')
writen = SHTLTerminal('WROTE', pos='v')

subject_question = Symbol('subject_question')
abstract_noun_phrase = Symbol('np')
author_noun_phrase = Symbol('author_np')
book_noun_phrase = Symbol('book_np')
proper_noun_phrase = Symbol('NP')

start = Symbol('S')

class DemoGrammarFactory(GrammarFactory):
    def grammar(self, named_entities):
        rules = [
            Rule(start, [subject_question]),
            Rule(subject_question, [what, abstract_noun_phrase, verb_phrase]),
            Rule(subject_question, [what, verb_phrase]),
            Rule(subject_question, [who, verb_phrase]),
            
            Rule(noun_phrase, []),
            Rule(noun_phrase, [noun, _or, noun]),
            Rule(noun_phrase, [noun, _and, noun]),
            Rule(noun_phrase, [both, noun, _and, noun]),
            Rule(noun_phrase, [noun]),
            Rule(verb_phrase, [has, noun_phrase, verb]),
            Rule(verb_phrase, [verb, noun_phrase]),
            Rule(adjective, [named_entities.symbol('genre')]),
            Rule(noun, [named_entities.symbol('genre')]),
            Rule(noun, [named_entities.symbol('author')]),
            Rule(noun, [named_entities.symbol('book')]),
            Rule(noun, [author]),
            Rule(noun, [book]),
            Rule(verb, [writen]),
        ]
        return Grammar(rules)

class SubjectQuestionSetup(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol != subject_question:
            return False
        query.addNamespace(Namespace('dbpprop:','http://dbpedia.org/property/'))
        query.addNamespace(Namespace('dbp:','http://dbpedia.org/resource/'))
        query.addNamespace(Namespace('dbpowl:','http://dbpedia.org/ontology/'))
        query.addNamespace(Namespace('rdfs:','http://www.w3.org/2000/01/rdf-schema#'))
        query.addNamespace(Namespace('rdf:','http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
        context['subject'] = Variable('subject')
        context['subject_name'] = Variable('subject_name')
        context['name_predicate'] = query.getReferent('rdfs:label')
        if any(c.symbol==noun_phrase for c in parse_node.children):
            np = (c for c in parse_node.children if c.symbol==noun_phrase).next()
            subject = np.find_node(lambda x:x.symbol==noun)
            assert(len(subject.children)==1)
            if subject.children[0].symbol == book:
                context['subject'] = Variable('book')
                context['subject_name'] = Variable('title')
            elif subject.children[0].symbol == author:
                context['subject'] = Variable('author')
                context['subject_name'] = Variable('name')
            else:
                raise SPARQLGenerationException(
                    "Invalid Subject Noun: %r"%subject.children[0].symbol
                )
            subject.instance = context['subject']
        query.addOutputs([context['subject'], context['subject_name']])
        query.addTriple(Triple(
            context['subject'], context['name_predicate'], context['subject_name']
        ))
        query.addFilter(Filter(
            'FILTER langMatches( lang(%r), "EN" )'%context['subject_name']
        ))
        return False #don't stop building, we just set up the query

def isImproperNoun(parse_node):
    if not parse_node.symbol == noun:
        return False
    return not isinstance(parse_node.children[0].symbol, NamedEntityTerminal)

class AdjectiveApplicator(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol!=adjective:
            return False
        assert(isinstance(parse_node.children[0].symbol, NamedEntityTerminal))
        if parse_node.children[0].symbol == context['named_entities'].symbol('genre'):
            predicate = query.getReferent('dbpprop:genre')
        else:
            raise SPARQLGenerationException(
                "Invalid adjective: %r"%parse_node.children[0].symbol
            )
        #apply to all improper nouns in this noun phrase
        for noun_node in parse_node.parent.find_nodes(isImproperNoun):
            if noun_node.instance is None:
                noun_node.instance = query.newVariable(noun_node.children[0].symbol.name)
            query.addTriple(Triple(
                noun_node.instance,
                predicate,
                Referent(parse_node.children[0].instance[-1])
            ))
        return False #by all means, please continue

class VerbPhraseRule(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol != verb_phrase:
            return False
        verb_node = parse_node.find_node(lambda x:x.symbol==verb)
        if verb_node.children[0].symbol == writen:
            predicate = query.getReferent('dbpowl:author')
        else:
            raise SPARQLGenerationException(
                "Invalid verb: %r"%verb_node.children[0].symbol
            )
        for noun_node in parse_node.find_nodes(lambda x:x.symbol==noun):
            #instanciate noun nodes with variables or referents
            if noun_node.instance is None:
                if isImproperNoun(noun_node):
                    noun_node.instance = query.newVariable(
                        noun_node.children[0].symbol.name
                    )
                else:
                    noun_node.instance = Referent(noun_node.children[0].instance[-1])
            query.addTriple(Triple(
                context['subject'],
                predicate,
                noun_node.instance
            ))
        return False
