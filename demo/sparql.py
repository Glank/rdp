from mike.sparql_gen import *
from mike.sparql import *
from mike.named import *
import re

### Grammar Definition ###

#Simple Terminals
who = WordTerminal('WHO')
what = InclusionSetTerminal('WHAT', set('WHAT WHICH'.split()), max_words=1)
has = InclusionSetTerminal('HAS', 
    set('HAVE,HAS,WILL,WILL HAVE,DONE'.split(',')), max_words=2)
_and = WordTerminal('AND')
_or = WordTerminal('OR')
_a = WordTerminal('A')
both = WordTerminal('BOTH')
that = WordTerminal('THAT')
are = WordTerminal('ARE')
the = WordTerminal('THE')
same = WordTerminal('SAME')
genre = WordTerminal('GENRE')
_as = WordTerminal('AS')

#SHTL Terminals
author = SHTLTerminal('AUTHOR', pos='n')
book = SHTLTerminal('BOOKS', pos='n')
writen = SHTLTerminal('WROTE', pos='v')

#higher level symbols
subject_question = Symbol('subject_question')
books_request = Symbol('books_request')
authors_request = Symbol('authors_request')
genre_request = Symbol('genre_request')
general_books = Symbol('general_books')
general_authors = Symbol('general_authors')
book_info = Symbol('book_info')

start = Symbol('S')

class DemoGrammarFactory(GrammarFactory):
    def grammar(self, named_entities):
        rules = [
            Rule(start, [subject_question]),
            Rule(subject_question, [books_request]),
            Rule(subject_question, [authors_request]),
            Rule(books_request, 
                [what, general_books, has, named_entities.symbol('author'), writen]),
            Rule(books_request, 
                [what, book, has, named_entities.symbol('author'), writen, 
                that, book_info]),
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
            Rule(book_info, [are, the, same, genre, _as, named_entities.symbol('book')]),
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
        ssmods = SolutionSequenceModifiers(limit=100, distinct=True)
        query.setSSMods(ssmods)
        return False #don't stop building, we just set up the query

class BooksRequestRule(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol != books_request:
            return False
        book = Variable('book')
        context['subject'] = book
        title = Variable('title')
        genre = Variable('genre')
        query.addOutputs([book, title, genre])
        query.addTriple(Triple(book, query.getReferent('rdfs:label'), title))
        query.addTriple(Triple(book, query.getReferent('dbpprop:genre'), genre))
        query.addFilter(Filter('FILTER langMatches( lang(?title), "EN" )'))
        #add author
        author_symbol = context['named_entities'].symbol('author')
        author_node = parse_node.find_node(lambda n:n.symbol==author_symbol)
        author = Referent(author_node.instance[-1])
        query.addTriple(Triple(book, query.getReferent('dbpowl:author'), author))
        #inform the general_books node
        gb_node = parse_node.find_node(lambda n:n.symbol==general_books)
        if gb_node is not None:
            gb_node.instance = book
            context['default_or'] = True
        return False 

class GeneralBooksRule(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol != general_books:
            return False
        #get or make the book variable
        book = parse_node.instance
        #link the genres to the book/books
        valid_genre = Variable('valid_genre')
        genre_symbol = context['named_entities'].symbol('genre')
        genre_nodes = list(parse_node.find_nodes(lambda n:n.symbol==genre_symbol))
        #done if no genres
        if not genre_nodes:
            return True
        #'and' and 'or' are the same with one genre
        if len(genre_nodes)==1:
            context['default_or'] = False #so default to 'and' because it's prettier
        union_gps = []
        for genre_node in genre_nodes:
            book_var = book or query.newVariable('book')
            genre = Referent(genre_node.instance[-1])
            triple = Triple(book_var, query.getReferent('dbpprop:genre'), genre)
            #link the author variable if it makes sense in context
            if 'author_var' in context and book is None:
                query.addTriple(Triple(
                    book_var, query.getReferent('dbpowl:author'), context['author_var']
                ))
            #'or' vs 'and' from context
            if context.get('default_or', False):
                genre_pattern = GraphPattern()
                genre_pattern.add(triple)
                union_gps.append(genre_pattern)
            else:
                query.addTriple(triple)
        if context.get('default_or', False):
            query.addUnion(Union(union_gps))
        return True #end dfs

class AuthorsRequestRule(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol != authors_request:
            return False
        author = Variable('author')
        context['author_var'] = author
        name = Variable('name')
        query.addOutputs([author, name])
        query.addTriple(Triple(
            author, query.getReferent('rdfs:label'), name
        ))
        query.addFilter(Filter('FILTER langMatches( lang(?name), "EN" )'))
        #add book
        book_symbol = context['named_entities'].symbol('book')
        book_node = parse_node.find_node(lambda n:n.symbol==book_symbol)
        if book_node is not None:
            book = Referent(book_node.instance[-1])
            query.addTriple(Triple(book, query.getReferent('dbpowl:author'), author))
        return False 

class BookInfoRule(QueryConstructionRule):
    def consume(self, parse_node, query, context):
        if parse_node.symbol != book_info:
            return False
        genre_var = query.newVariable('genre')
        book_symbol = context['named_entities'].symbol('book')
        book_node = parse_node.find_node(lambda n:n.symbol==book_symbol)
        book = Referent(book_node.instance[-1])
        query.addTriple(Triple(book, query.getReferent('dbpprop:genre'), genre_var))
        query.addTriple(Triple(
            context['subject'], query.getReferent('dbpprop:genre'), genre_var
        ))
        return True
