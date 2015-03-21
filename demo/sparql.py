from mike.sparql_gen import *
from mike.sparql import *
import re

#Grammar Definition
who = WordTerminal('WHO')
what = WordTerminal('WHAT')
which = WordTerminal('WHICH')
authors = SHTLTerminal('AUTHOR', pos='n')
books = WordTerminal('BOOKS')
have = InclusionSetTerminal('HAVE', 
    set('HAVE,HAS,WILL,WILL HAVE,DONE'.split(',')), 
    max_words=2
)
has = WordTerminal('HAS')
writen = SHTLTerminal('WROTE', pos='v')

hw = Symbol("_HAVE_WRITEN_")
hw_rules = [
    Rule(hw, [have, writen]),
    Rule(hw, [writen]),
]
hw_gram = Grammar(hw_rules, start=hw)
hw_gram.compile()
have_writen = ComplexTerminalSymbol('HAVE_WRITEN', hw_gram)

_and = WordTerminal('AND')
both = WordTerminal('BOTH')

subject_question = Symbol('subject_question')

book_description = Symbol('BOOK_DESCRIPTION')
genre_description = Symbol('GENRE_DESCRIPTION')
bibliography_request = Symbol('bibliography_request')
author_search = Symbol('author_search')

start = Symbol('S')

class DemoGrammarFactory(GrammarFactory):
    def grammar(self, named_entities):
        rules = [
            Rule(start, [bibliography_request]),
            Rule(start, [author_search]),
            Rule(bibliography_request, [
                what, books, has, named_entities.symbol('author'), writen
            ]),
            Rule(author_search, [who, have_writen, book_description]),
            Rule(author_search, [which, authors, have_writen, book_description]),
            Rule(book_description, [
                both, book_description, _and, book_description
            ]),
            Rule(book_description, [
                book_description, _and, book_description
            ]),
            Rule(book_description, [genre_description]),
            Rule(genre_description, [named_entities['genre'].symbol()]),
            Rule(genre_description, [named_entities['genre'].symbol(), books]),
        ]
        return Grammar(rules)

class BibliographyRequest(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol != bibliography_request:
            return False
        author_symbol = context['named_entities']['author'].symbol()
        author = parse_node.find_node(
            lambda n:n.symbol==author_symbol
        )
        name, full_name, uri = author.instance
        query.addNamespace(Namespace('dbp:','http://dbpedia.org/resource/'))
        query.addNamespace(Namespace('dbpowl:','http://dbpedia.org/ontology/'))
        query.addNamespace(Namespace('rdfs:','http://www.w3.org/2000/01/rdf-schema#'))
        query.addNamespace(Namespace('rdf:','http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
        book_var = Variable('book')
        title_var = Variable('title')
        query.addTriple(Triple(
            book_var, query.getReferent('rdf:type'), query.getReferent('dbpowl:Book')
        ))
        query.addTriple(Triple(
            book_var, query.getReferent('dbpowl:author'), Referent(uri)
        ))
        query.addTriple(Triple(
            book_var, query.getReferent('rdfs:label'), title_var
        ))
        query.addFilter(Filter('FILTER langMatches( lang(?title), "EN" )'))
        query.addOutputs([book_var, title_var])
        return True

class AuthorSearch(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol != author_search:
            return False
        #get the genres
        genre_symbol = context['named_entities']['genre'].symbol()
        genres = []
        for node in parse_node.iter_nodes():
            if node.symbol==genre_symbol:
                genres.append(node)
        #setup the query namespaces
        query.addNamespace(Namespace('dbpprop:','http://dbpedia.org/property/'))
        query.addNamespace(Namespace('dbp:','http://dbpedia.org/resource/'))
        query.addNamespace(Namespace('dbpowl:','http://dbpedia.org/ontology/'))
        query.addNamespace(Namespace('rdfs:','http://www.w3.org/2000/01/rdf-schema#'))
        query.addNamespace(Namespace('rdf:','http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
        author_var = Variable('author')
        name_var = Variable('name')
        query.addOutputs([author_var, name_var])
        query.addGroupCondition(author_var)
        query.addTriple(Triple(
            author_var, query.getReferent('rdf:type'), query.getReferent('dbpowl:Writer')
        ))
        query.addTriple(Triple(
            author_var, query.getReferent('rdfs:label'), name_var
        ))
        query.addFilter(Filter('FILTER langMatches( lang(?name), "EN" )'))
        #add the genres to the queries
        for i,genre in enumerate(genres):
            _,_,uri = genre.instance
            book_i = Variable('book%d'%i)
            query.addTriple(Triple(
                book_i, query.getReferent('rdf:type'), query.getReferent('dbpowl:Book')
            ))
            query.addTriple(Triple(
                book_i, query.getReferent('dbpowl:author'), author_var
            ))
            query.addTriple(Triple(
                book_i, query.getReferent('dbpprop:genre'), Referent(uri)
            ))
        return True
