from SPARQLWrapper import SPARQLWrapper, JSON
import json
 
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
    PREFIX dbpprop:<http://dbpedia.org/property/>
    PREFIX dbpowl:<http://dbpedia.org/ontology/>
    PREFIX dbpresource:<http://dbpedia.org/resource/>
    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?author ?name
    WHERE{
        ?author a dbpowl:Writer;
            dbpowl:birthName ?name.
    }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

with open('result.json', 'w') as f:
    json.dump(results, f, indent=4)
