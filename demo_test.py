import mike.named as named
import json

with open('demo/configs.json', 'r') as f:
    configs = json.load(f)

names = named.NamedEntityCollection(
    configs['named_entity_types']
)
names.build()

ident = names['book'].identifier
print ident.ident("Wotherin High")
