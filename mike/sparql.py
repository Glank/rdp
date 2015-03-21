class RawSPARQL:
    def __init__(self, repr_):
        self._repr_ = repr_
    def __repr__(self):
        return self._repr_

class TripleElement:
    def __cmp__(self, other):
        return cmp(repr(self),repr(other))
    def getRepr(self, namespaces=None):
        return repr(self)

class Variable(TripleElement):
    def __init__(self, name):
        self.name = name 
    def __hash__(self):
        return hash(self.name)
    def __repr__(self):
        return "?%s"%self.name

class Referent(TripleElement):
    def __init__(self, iri):
        self.iri = iri
    def __repr__(self):
        return u"<%u>"%self.iri
    def getRepr(self, namespaces=None):
        if namespaces is None:
            return repr(self)
        return namespaces.minimize(self.iri)

class Literal(TripleElement, RawSPARQL):
    pass

class Triple:
    def __init__(self, s, p, o):
        self.sub = s
        self.pred = p
        self.obj = o
        assert all(isinstance(e,TripleElement) for e in self)
    def __iter__(self):
        yield self.sub
        yield self.pred
        yield self.obj
    def __repr__(self):
        return self.getRepr()
    def getRepr(self, namespaces=None):
        return "%s %s %s"%tuple(part.getRepr(namespaces) for part in self)
    def predObjOnly(self, namespaces=None):
        return "%s %s"%(self.pred.getRepr(namespaces), self.obj.getRepr(namespaces))

class Filter(RawSPARQL):
    pass

class Binding:
    def __init__(self, expression, asVar):
        self.expression = expression
        self.asVar = asVar
        assert(isinstance(expression, RawSPARQL))
        assert(isinstance(asVar, Variable))
    def __repr__(self):
        return "BIND (%s AS %r)"%(self.expression, self.asVar)
    def inline(self):
        return "(%s AS %r)"%(self.expression, self.asVar)

class GraphPattern:
    def __init__(self):
        self._filters_ = []
        self._variables_ = set()
        self._triples_ = []
        self._optionals_ = []
        self._bindings_ = []
    def _add_triple_(self, triple):
        for e in triple:
            if isinstance(e,Variable):
                self._variables_.add(e)
        self._triples_.append(triple)
    def _add_optional_(self, optional):
        self._optionals_.append(optional)
        self._varaibles_.update(optional.variables)
    def _add_binding_(self, binding):
        self._bindings_.append(binding)
        self._variables_.add(binding.asVar)
    def add(self, value):
        if isinstance(value, Triple):
            self._add_triple_(value)
        elif isinstance(value, Filter):
            self._filters_.append(value)
        elif isinstance(value, GraphPattern):
            self._add_optional_(value)
        elif isinstance(value, Binding):
            self._add_binding_(value)
        elif isinstance(value, Variable):
            self._variables_.add(value)
        else:
            raise Exception("Invalid Type: %r"%type(value))
    def build(self, context):
        lines = []
        tab = context.get('tab','    ')
        tab_offset = context.get('tab_offset',0)+1
        namespaces = context.get('namespaces',None)
        if namespaces is None:
            namespaces = NamespaceTable()
        #add bindings
        for binding in self._bindings_:
            lines.append(tab*tab_offset+repr(binding)+'.')
        #add triples
        triples_by_sub = {}
        for triple in self._triples_:
            triples = triples_by_sub.get(triple.sub, [])
            triples.append(triple)
            triples_by_sub[triple.sub] = triples
        for sub, triples in triples_by_sub.items():
            if len(triples)==1:
                lines.append(tab*tab_offset+triples[0].getRepr(namespaces)+'.')
            else:
                assert(len(triples)>1)
                lines.append(tab*tab_offset+triples[0].getRepr(namespaces)+';')
                for triple in triples[1:-1]:
                    lines.append(tab*(tab_offset+1)+triple.predObjOnly(namespaces)+';')
                lines.append(tab*(tab_offset+1)+triples[-1].predObjOnly(namespaces)+'.')
        #add optionals
        subcontext = context.copy()
        subcontext['tab_offset'] = tab_offset
        for optional in self._optionals_:
            lines.append(tab*tab_offset+'OPTIONAL {')
            lines.append(optional.build(subcontext))
            lines.append(tab*tab_offset+'}.')
        #add filters
        for filt in self._filters_:
            lines.append(tab*tab_offset+repr(filt)+'.')
        return '\n'.join(lines)

class SelectGrouping:
    def __init__(self, pattern=None):
        self.pattern = pattern or GraphPattern()
        self._aggregateBindings_ = {} #by variable
        self._groupBy_ = []
        self._having_ = None
        assert(isinstance(self.pattern, GraphPattern))
    def addBinding(self, binding):
        self._aggregateBindings_[binding.asVar] = binding
        assert(isinstance(binding, Binding))
    def getVarDeclaration(self, variable):
        if variable in self._aggregateBindings_:
            return self._aggregateBindings_[variable].inline()
        return repr(variable)
    def addGroupCondition(self, condition):
        assert(isinstance(condition, (Variable, RawSPARQL)))
        self._groupBy_.append(condition)
    def setHaving(self, having):
        assert(isinstance(having, RawSPARQL))
        self._having_ = having
    def build(self, context):
        build_str = '{\n'+self.pattern.build(context)+'\n}'
        if self._groupBy_:
            groupby_str = "GROUP BY "+" ".join(repr(c) for c in self._groupBy_)
            build_str+= "\n"+groupby_str
        if self._having_:
            build_str+= "\nHAVING "+repr(self._having_)
        return build_str

class SolutionSequenceModifiers:
    def __init__(self, order=None, limit=None, offset=None, distinct=False, reduced=False):
        self.order = order
        self.limit = limit
        self.offset = offset
        self.distinct = distinct
        self.reduced = reduced
        assert not (distinct and reduced)
        assert order is None or isinstance(order, RawSPARQL)
        assert limit is None or isinstance(limit, int)
        assert offset is None or isinstance(offset, int)
    def getLimitOffsetClause(self):
        if self.limit is None and self.offset is None:
            return None
        if self.limit is None:
            clause = ""
        else:
            clause = "LIMIT %d"%self.limit
        if self.offset is not None:
            if clause:
                clause+= " OFFSET %d"%self.offset
            else:
                clause = "OFFSET %d"%self.offset
        return clause

class SelectClause:
    def __init__(self, where=None):
        self._outputs_ = []
        self.where = where or SelectGrouping()
        self._ssmods_ = SolutionSequenceModifiers()
        assert(isinstance(self.where, SelectGrouping))
    def setSSMods(self, ssmods):
        assert(isinstance(ssmods, SolutionSequenceModifiers))
        self._ssmods_ = ssmods
    def addOutput(self, variable):
        assert(isinstance(variable, Variable))
        self._outputs_.append(variable)
    def build(self, context):
        outputs_mod = ""        
        if self._ssmods_.distinct:
            outputs_mod = " DISTINCT"
        elif self._ssmods_.reduced:
            outputs_mod = " REDUCED"
        outputs_str = " ".join(self.where.getVarDeclaration(v) for v in self._outputs_)
        where_str = self.where.build(context)
        build_str = "SELECT%s %s\nWHERE %s"%(outputs_mod, outputs_str, where_str)
        if self._ssmods_.order:
            build_str+= "\nORDER BY "+repr(self._ssmods_.order)
        limitOffset_str = self._ssmods_.getLimitOffsetClause()
        if limitOffset_str:
            build_str+= "\n"+limitOffset_str
        return build_str

class Namespace:
    def __init__(self, prefix, expansion):
        assert prefix.endswith(':')
        self.prefix = prefix
        self.expansion = expansion
    def __repr__(self):
        return "PREFIX %s <%s>"%(self.prefix, self.expansion)
    def __cmp__(self, other):
        return cmp(repr(self),repr(other))

class NamespaceTable:
    def __init__(self):
        self._namespaces_ = []
    def add(self, namespace):
        assert(isinstance(namespace, Namespace))
        if namespace not in self._namespaces_:
            self._namespaces_.append(namespace)
    def minimize(self, uri):
        minimized = "<%s>"%uri
        for namespace in self._namespaces_:
            if uri.startswith(namespace.expansion):
                shorter = namespace.prefix+uri[len(namespace.expansion):]
                if len(shorter)<len(minimized):
                    minimized = shorter
        return minimized
    def maximize(self, referentStr):
        for namespace in self._namespaces_:
            if referentStr.startswith(namespace.prefix):
                longer = namespace.expansion+referentStr[len(namespace.prefix):]
                return Referent(longer)
        raise Exception("ReferentStr not prefixed: %r"%referentStr)
    def build(self, context):
        return '\n'.join(repr(n) for n in self._namespaces_)

class SPARQLQuery:
    def __init__(self, clause=None, namespaces=None):
        self.namespaces = namespaces or NamespaceTable()
        self.clause = clause or SelectClause()
        assert(isinstance(self.clause, SelectClause))
        assert(isinstance(self.namespaces, NamespaceTable))
    def build(self):
        context = {'query':self, 'namespaces':self.namespaces, 'tab_depth':0, 'tab':'    '}
        namespaces_str = self.namespaces.build(context=context)
        clause_str = self.clause.build(context=context)
        return '\n'.join([namespaces_str,clause_str])
    def addNamespace(self, namespace):
        assert isinstance(namespace, Namespace)
        self.namespaces.add(namespace)
    def addTriple(self, triple):
        assert isinstance(triple, Triple)
        self.clause.where.pattern.add(triple)
    def addFilter(self, filt):
        assert isinstance(filt, Filter)
        self.clause.where.pattern.add(filt)
    def addAggregateBinding(self, binding):
        assert isinstance(binding, Binding)
        self.clause.where.addBinding(binding)
    def addBinding(self, binding):
        assert isinstance(binding, Binding)
        self.clause.where.pattern.add(binding)
    def addOutput(self, variable):
        assert isinstance(variable, Variable)
        self.clause.addOutput(variable)
    def addOutputs(self, variables):
        for variable in variables:
            self.addOutput(variable)
    def addGroupCondition(self, condition):
        self.clause.where.addGroupCondition(condition)
    def addGroupConditions(self, conditions):
        for condition in conditions:
            self.addGroupCondition(condition)
    def setHaving(self, having):
        self.clause.where.setHaving(having)
    def setSSMods(self, ssmods):
        self.clause.setSSMods(ssmods)
    def getReferent(self, referentStr):
        return self.namespaces.maximize(referentStr)
    def __str__(self):
        return self.build()

if __name__=='__main__':
    query = SPARQLQuery()
    query.addNamespace(Namespace('rdfs:', 'http://www.w3.org/2000/01/rdf-schema#'))
    query.addNamespace(Namespace('dbpprop:', 'http://dbpedia.org/property/'))
    entity = Variable('entity')
    name = Variable('name')
    book = Variable('book')
    books = Variable('books')
    query.addTriple(Triple(book, query.getReferent('dbpprop:author'), entity))
    query.addTriple(Triple(entity, query.getReferent('rdfs:label'), name))
    query.addFilter(Filter('FILTER langMatches( lang(?name), "EN" )'))
    query.addAggregateBinding(Binding(RawSPARQL('COUNT(?book)'), books))
    query.addGroupConditions([entity, name, books])
    query.setHaving(RawSPARQL('(COUNT(?book)>1)'))
    ssmods = SolutionSequenceModifiers(order=RawSPARQL('DESC(?books)'), limit=5000)
    query.setSSMods(ssmods)
    query.addOutputs([entity, name, books])
    print query.build()
