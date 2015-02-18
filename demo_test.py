from mike import Mike
import json
from rdp import *

with open('demo/configs.json', 'r') as f:
    configs = json.load(f)
mike = Mike(configs)
mike.build()

print "Grammar:"
print mike._grammar_()
print

question = 'Which writers have published both high fantasy and science fiction?'
#question = 'Who done wrote low fantasy?'
print "Question:"
print question
print

sparql = mike.get_sparql(
     question,
     verbose=True
)

print "\nSPARQL:"
print sparql
