class DirectedGraph():
    def __init__(self):
        self.vertices = set()
        self.edges = set()
        self.forward = {}
        self.backward = {}
    def add_vertex(self, vertex):
        if self.has_vertex(vertex):
            return
        self.vertices.add(vertex)
        self.forward[vertex] = set()
        self.backward[vertex] = set()
    def has_vertex(self, vertex):
        return vertex in self.vertices 
    def add_edge(self, a, b):
        edge = (a,b)
        assert(a in self.vertices)
        assert(b in self.vertices)
        self.edges.add(edge)
        self.forward[a].add(b)
        self.backward[b].add(a)
    def reverse(self):
        self.forward, self.backward = self.backward, self.forward
    def dfs(self, start, end):
        """Returns either the path from start to end,
        the path of the first cycle found, or None if the end
        is not found."""
        visited = set()
        path = []
        PATH_POP = object()
        to_search = [start]
        while to_search:
            cur = to_search.pop()
            while cur is PATH_POP:
                path.pop()
                if not to_search:
                    return None
                cur = to_search.pop()
            if cur==end and path:
                path.append(cur)
                return path
            if cur in path:
                del path[:path.index(cur)]
                path.append(cur)
                return path
            path.append(cur)
            visited.add(cur)
            to_search.append(PATH_POP)
            to_search.extend(self.forward[cur])
        return None
    def is_cyclic(self):
        if not self.vertices:
            return False
        v = iter(self.vertices).next()
        cycle = self.dfs(v,v)
        if cycle:
            return True
        self.reverse()
        cycle = self.dfs(v,v)
        self.reverse()
        return bool(cycle)
    def is_leaf(self, v):
        return not bool(self.forward[v])
    def leaves(self):
        return set(v for v in self.vertices if self.is_leaf(v))

if __name__=='__main__':
    g = DirectedGraph()
    for v in 'abcdefg':
        g.add_vertex(v)
    edges = [
        ('a','b'),  
        ('b','c'),
        ('b','d'),
        ('d','e'),
        ('d','f'),
        ('f','g'),
        ('g','b'),
    ]
    for e in edges:
        g.add_edge(*e)
    print g.dfs('a','g')
    print g.is_cyclic()
    print g.leaves()
