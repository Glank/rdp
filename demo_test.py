import mike.named as named
import json

with open('demo/configs.json', 'r') as f:
    configs = json.load(f)

author = named.NamedEntityType(configs['named_entity_types'][0])
author.build()
