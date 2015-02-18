from mike.question import *
import re

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

book_description = Symbol('BOOK_DESCRIPTION')
genre_description = Symbol('GENRE_DESCRIPTION')

def remove_indent(long_str):
    lines = long_str.split('\n')
    min_indent = float('inf')
    for line in lines:
        if line.strip():
            indent = len(re.match(r'(\s*)', line).group(1))
            if indent<min_indent:
                min_indent = indent
    long_str = '\n'.join(line[min_indent:] for line in lines)
    return long_str

class BibliographyRequest(QuestionType):
    def __init__(self):
        QuestionType.__init__(self, 'bibliography_request')
    def rule_tails(self, named_entities):
        yield [
            what, books, has,
            named_entities.symbol('author'),
            writen
        ]
    def get_sparql(self, parse_tree, named_entities):
        author_symbol = named_entities['author'].symbol()
        author = parse_tree.find_node(
            lambda n:n.symbol==author_symbol
        )
        name, full_name, uri = author.instance
        sparql = """
        PREFIX dbp:<http://dbpedia.org/resource/>
        PREFIX dbpowl:<http://dbpedia.org/ontology/>
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?book ?title
        WHERE{{
            ?book a dbpowl:Book;
                dbpowl:author <{author_uri}>;
                rdfs:label ?title.
            FILTER langMatches( lang(?title), "EN" ).
        }}
        """.format(author_uri = uri)
        return sparql

class AuthorSearch(QuestionType):
    def __init__(self):
        QuestionType.__init__(self, 'author_search')
    def rules(self, root, named_entities):
        yield Rule(root, [self.symbol()])
        yield Rule(self.symbol(), [who, have_writen, book_description])
        yield Rule(self.symbol(), [which, authors, have_writen, book_description])
        yield Rule(book_description, [
            both, book_description, _and, book_description
        ])
        yield Rule(book_description, [
            book_description, _and, book_description
        ])
        yield Rule(book_description, [genre_description])
        yield Rule(genre_description, [named_entities['genre'].symbol()])
        yield Rule(genre_description, [named_entities['genre'].symbol(), books])
    def get_sparql(self, parse_tree, named_entities):
        genre_symbol = named_entities['genre'].symbol()
        genres = []
        for node in parse_tree.iter_nodes():
            if node.symbol==genre_symbol:
                genres.append(node)
        book_type_filters = []
        for i,genre in enumerate(genres):
            _,_,uri = genre.instance
            filt = """
            ?book{i} a dbpowl:Book;
                dbpowl:author ?author;
                dbpprop:genre <{genre}>.
            """.format(i=i, genre=uri)
            book_type_filters.append(filt)
        sparql = """
        PREFIX dbpprop:<http://dbpedia.org/property/>
        PREFIX dbp:<http://dbpedia.org/resource/>
        PREFIX dbpowl:<http://dbpedia.org/ontology/>
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?author ?name
        WHERE{{
            ?author a dbpowl:Writer;
                rdfs:label ?name.
            {filts}
            FILTER langMatches( lang(?name), "EN" ).
        }}
        GROUP BY ?author
        """.format(filts = '\n'.join(book_type_filters))
        return remove_indent(sparql).strip()
