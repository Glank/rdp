import mike
import json

with open('demo/configs.json', 'r') as f:
    configs = json.load(f)

ai = mike.Mike(configs)
print ai.get_sparql('what books has paolini writen?')
