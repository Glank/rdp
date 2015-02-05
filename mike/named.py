from SPARQLWrapper import SPARQLWrapper, JSON
from distribute import *
import json
import os.path
import re

def ensure_dirs(fn):
    path = os.path.abspath(fn)
    path = os.path.dirname(path)
    to_make = []
    while not os.path.exists(path):
        to_make.append(path)
        path = os.path.dirname(path)
    for path in reversed(to_make):
        os.mkdir(path)

class NEQuery:
    def __init__(self, configs):
        self.result_fn = configs['result_file']
        self.query_fn = configs['query_file']
        self.endpoint = configs['endpoint']
    def get_sparql(self):
        with open(self.query_fn, 'r') as f:
            return f.read()
    def clean(self):
        if os.path.isfile(self.result_fn):
            os.remove(self.result_fn)
    def build(self, rebuild=False):
        #skip this step if already build and not forced to rebuild
        if os.path.isfile(self.result_fn) and not rebuild:
            return
        sparql_db = SPARQLWrapper(self.endpoint)
        sparql_db.setQuery(self.get_sparql())
        sparql_db.setReturnFormat(JSON)
        results = sparql_db.query().convert()
        ensure_dirs(self.result_fn)
        with open(self.result_fn, 'w') as f:
            json.dump(results, f, indent=4)
    def get_results(self):
        with open(self.result_fn, 'r') as f:
            return json.load(f)

class ResultMapper:
    def stand(self, name):
        """Standardizes a name."""
        raise NotImplementedError()
    def map(self, result_dict):
        """Takes as input the result dict stored in the NEQuery result file.
        This method is an iterator which yields tuples of the form
        (entity uri, given name, standardized name)"""
        raise NotImplementedError()

class PersonNameMapper(ResultMapper):
    def stand(self, name):
        return ''.join(re.findall('[A-Z0-9]+',name.upper()))
    def map(self, result_dict):
        for binding in result_dict['results']['bindings']:
            entity = binding['entity']['value']
            given = binding['name']['value']
            subnames = given.split()
            stand = self.stand(given)
            yield (entity, given, stand)
            if len(subnames)>=2:
                for name in [subnames[0], subnames[-1]]:
                    stand = self.stand(name)
                    yield (entity, given, stand)

class NEModel:
    def __init__(self, entity_type, configs):
        self.entity_type = entity_type
        self.build_folder = configs['build_folder']
        #TODO: make configurable
        self.model_types = ['length', 'ngram']
    def _build_model_(self, model_type, rebuild):
        fn = os.path.join(self.build_folder, model_type)
        #skip this step if already build and not forced to rebuild
        if os.path.isfile(fn) and not rebuild:
            return
        results = self.entity_type.query.get_results()
        names = [n[2] for n in self.entity_type.result_mapper.map(results)]
        if model_type=='length':
            prob_set = LengthProbSet(names)
        elif model_type=='ngram':
            prob_set = NgramProbSet(3, names)
        else:
            raise Exception("Invalid model type: '%s'"%model_type)
        ensure_dirs(fn)
        with open(fn, 'wb') as f:
            prob_set.tofile(f)
    def build(self, rebuild=False):
        for model_type in self.model_types:
            self._build_model_(model_type, rebuild)
    def clean(self):
        for model_type in self.model_types:
            fn = os.path.join(self.build_folder, model_type)
            if os.path.isfile(fn):
                os.remove(fn)
    def get_probset(self):
        probsets = []
        for model_type in self.model_type:
            fn = os.path.join(self.build_folder, model_type)
            with open(fn, 'rb') as f:
                if model_type=='length':
                    prob_set = LengthProbSet.fromfile(f)
                elif model_type=='ngram':
                    prob_set = NgramProbSet.fromfile(f)
                else:
                    raise Exception("Invalid model type: '%s'"%model_type)
            probsets.append(prob_set)
        return JoinedProbabilitySet(probsets)

class NEIdentifier:
    def __init__(self, entity_type, configs):
        self.entity_type = entity_type
        #TODO: make these values configurable
        self.max_matches = 5
        self.max_percent_diff = .1
    def prompt_possibles(self, orig, possibles):
        print "By '%s' did you mean:"%orig
        for i, (name, uri) in enumerate(possibles):
            print "%d)\t%s"%((i+1),name)
        print "%d)\tNone of the above."%(len(possibles)+1)
        valid = False
        n = 0
        while not valid:
            valid = True
            try:
                n = int(raw_input())
            except Exception:
                valid = False
            if not 1<=n<=len(possibles)+1:
                valid = False
        if n-1==len(possibles):
            return None
        return possibles[n-1]
    def ident(self, name):
        orig_name = name
        best_matches = []
        results = self.query.get_results()
        mapper = self.entity_type.result_mapper
        name = mapper.stand(name)
        for uri, given, stand in mapper.map(results):
            dist = jaccard_ngram_dist(stand,name,3)
            best_matches.append(((given,uri),dist))
            if len(best_authors)>100:
                best_matches.sort(key=lambda x:x[1])
                best_matches = best_matches[:self.max_matches]
        best_matches.sort(key=lambda x:x[1])
        best_matches = best_matches[:self.max_matches]
        best_dist = best_matches[0][1]
        possibles = [best_matches[0][0]]
        for match, dist in best_matches[1:]:
            percent_diff = (dist-best_dist)*2/float(dist+best_dist)
            if percent_diff < self.max_percent_diff:
                possibles.append(match)
        if len(possibles)>1:
            identified = self.prompt_possibles(orig_name, possibles)
        else:
            identified = possibles[0]
        return identified

class NamedEntityType:
    def __init__(self, configs):
        self.name = configs['name']
        self.query = NEQuery(configs.get('query',{}))
        self.model = NEModel(self, configs.get('model',{}))
        self.identifier = NEIdentifier(self, configs.get('identifier',{}))
        self.result_mapper = PersonNameMapper()
    def build(self, rebuild=False):
        self.query.build(rebuild=rebuild)
        self.model.build(rebuild=rebuild)
    def clean(self):
        self.query.clean()
        self.model.clean()
