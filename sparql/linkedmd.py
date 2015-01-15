from SPARQLWrapper import SPARQLWrapper, JSON
 
sparql = SPARQLWrapper("http://data.linkedmdb.org/sparql")
sparql.setQuery("""
    PREFIX lmdb:<http://data.linkedmdb.org/page/film/>
    PREFIX movie:<http://data.linkedmdb.org/resource/movie/>
    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dc:<http://purl.org/dc/terms/>
    SELECT ?movie_title
    WHERE {
        {
            ?nathan a movie:actor;
                movie:actor_name "Nathan Fillion".
            ?movie a movie:film;
                dc:title ?movie_title;
                movie:actor ?nathan.    
        }
        UNION
        {
            ?morena a movie:actor;
                movie:actor_name "Morena Baccarin".
            ?movie a movie:film;
                dc:title ?movie_title;
                movie:actor ?morena.    
        }
    }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
 
for result in results["results"]["bindings"]:
    print(result)
