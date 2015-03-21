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
books_request = Symbol('books_request')
authors_request = Symbol('authors_request')
general_books = Symbol('general_books')
general_authors = Symbol('general_authors')

start = Symbol('S')

class DemoGrammarFactory(GrammarFactory):
    def grammar(self, named_entities):
        rules = [
            Rule(start, [subject_question]),
            Rule(subject_question, [books_request]),
            Rule(subject_question, [authors_request]),
            Rule(books_request, 
                [what, general_books, has, named_entities.symbol('author'), writen]),
            Rule(authors_request, [what, general_authors, has, writen, general_books]),
            Rule(authors_request, [who, has, writen, general_books]),
            Rule(authors_request, [what, author, writen, named_entities.symbol('book')]),
            Rule(authors_request, [who, writen, named_entities.symbol('book')]),
            Rule(general_books, [book]),
            Rule(general_books, [named_entities.symbol('genre')]),
            Rule(general_books, [named_entities.symbol('genre'), book]),
            Rule(general_books, 
                [named_entities.symbol('genre'), _and, named_entities.symbol('genre')]),
            Rule(general_books, 
                [named_entities.symbol('genre'), _and, 
                named_entities.symbol('genre'), book]),
            Rule(general_authors, [author]),
            Rule(general_authors, [named_entities.symbol('genre'), author]),
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
        return False #don't stop building, we just set up the query

class BooksRequestRule(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol != books_request:
            return False
        book = Variable('book')
        title = Variable('title')
        query.addOutputs([book, title])
        query.addTriple(Triple(book, query.getReferent('rdfs:label'), title))
        query.addFilter(Filter('FILTER langMatches( lang(?title), "EN" )'))
        #add author
        author_symbol = context['named_entities'].symbol('author')
        author_node = parse_node.find_node(lambda n:n.symbol==author_symbol)
        author = Referent(author_node.instance[-1])
        query.addTriple(Triple(book, query.getReferent('dbpowl:author'), author))
        #inform the general_books node
        gb_node = parse_node.find_node(lambda n:n.symbol==general_books)
        gb_node.instance = book
        return False 

class GeneralBooksRule(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol != general_books:
            return False
        #get or make the book variable
        book = parse_node.instance or query.newVariable('book')
        parse_node.instance = book
        #link it to the genres
        genre_symbol = context['named_entities'].symbol('genre')
        for genre_node in parse_node.find_nodes(lambda n:n.symbol==genre_symbol):
            genre = Referent(genre_node.instance[-1])
            query.addTriple(Triple(book, query.getReferent('dbpprop:genre'), genre))
        return True #end dfs

class AuthorsRequestSetup(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol != authors_request:
            return False
        context['subject'] = Variable('author')
        name = Variable('name')
        query.addOutput([context['subject'], name])
        query.addTriple(Triple(
            context['subject'], query.getReferent('rdfs:label'), name
        ))
        query.addFilter(Filter('FILTER langMatches( lang(?name), "EN" )'))
        return False 

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
