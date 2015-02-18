from SPARQLWrapper import SPARQLWrapper, JSON
import json
 
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
PREFIX dbp:<http://dbpedia.org/resource/>
        PREFIX dbpowl:<http://dbpedia.org/ontology/>
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?book ?title
        WHERE{
            ?book a dbpowl:Book;
                dbpowl:author <http://dbpedia.org/resource/Gene_Wolfe>;
                rdfs:label ?title.
            FILTER langMatches( lang(?title), "EN" ).
        }

""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

with open('result.json', 'w') as f:
    json.dump(results, f, indent=4)
