from author_ident import ident_author

def generate_sparql(parse_tree):
    bib_req = parse_tree.find_node(lambda n:n.symbol.name=='bibliography_request')
    if bib_req:
        return generate_bibliography_request(bib_req)
    return None

def generate_bibliography_request(parse_tree_node):
    author = parse_tree_node.find_node(lambda n:n.symbol.name=='author')
    name, uri = ident_author(' '.join(author.instance.obj))
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
