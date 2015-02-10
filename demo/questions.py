from mike.question import *


what = WordTerminal('WHAT')
books = WordTerminal('BOOKS')
has = WordTerminal('HAS')
writen = WordTerminal('WRITEN')

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
