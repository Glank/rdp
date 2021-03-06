from mike import Mike
import json
from rdp import *
from SPARQLWrapper import SPARQLWrapper, JSON
from tabulate import tabulate

with open('demo/configs.json', 'r') as f:
    configs = json.load(f)
mike = Mike(configs)
mike.build()

#print "Grammar:"
grammar = mike._grammar_(verbose=False)
#print

#print "Compiled Grammar:"
#print grammar
#print

#question = 'What science fiction books has E. A. Poe written?'
#question = 'Which writers have published both high fantasy and science fiction?'
#question = "Which authors have writen science fiction?"
#question = 'What books has Heinline written?'
#question = 'What science fiction and high fantasy books has George Martin written?'
#question = 'What science fiction books has George Martin written?'
#question = 'Who wrote Ferinheit 450?'
question = 'What books has Dave Wolverton written that are the same genre as Game of Thrones?'
#question = 'What books has Dave Wolverton written that are the same genre as Revolt in 2100?'
#question = 'What science fiction author has written high fantasy novels?'
#question = 'Who scrawled Ferinheit 451?'
print "Question:"
print question
print

query = mike.get_sparql(
     question,
     verbose=True
)

print "\nSPARQL:"
print query

print "\nExecute (N/y)?"
execute = raw_input()
if execute.lower()!='y':
    exit()

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
table = []
for binding in results['results']['bindings']:
    row = []
    for var in results['head']['vars']:
        row.append(binding[var]['value'])
    table.append(row)

print "\nResults:"
print tabulate(table, headers=results['head']['vars'])
