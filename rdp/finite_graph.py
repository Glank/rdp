class DirectedGraph():
    def __init__(self):
        self.vertices = set()
        self.edges = set()
        self.forward = {}
        self.backward = {}
    def __len__(self):
        return len(self.vertices)
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
        if edge in self.edges:
            return
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
        path_set = set()
        path = []
        PATH_POP = object()
        to_search = [start]
        while True:
            cur = to_search.pop()
            while cur is PATH_POP:
                path_set.remove(path.pop())
                if not to_search:
                    return None
                cur = to_search.pop()
            if cur==end and path:
                path.append(cur)
                return path
            if cur in path_set:
                del path[:path.index(cur)]
                path.append(cur)
                return path
            path.append(cur)
            path_set.add(cur)
            to_search.append(PATH_POP)
            to_search.extend(self.forward[cur])
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
    def get_reachable(self, start):
        reached = set([start])
        to_search = [start]
        while to_search:
            cur = to_search.pop()
            for n in self.forward[cur]:
                if n not in reached:
                    to_search.append(n)
                    reached.add(n)
        return reached
    def get_unreachable(self, start):
        reachable = self.get_reachable(start)
        return set(v for v in self.vertices if v not in reachable)
    def is_root(self, v):
        return not bool(self.backward[v])
    def roots(self):
        return set(v for v in self.vertices if self.is_root(v))
    def is_leaf(self, v):
        return not bool(self.forward[v])
    def leaves(self):
        return set(v for v in self.vertices if self.is_leaf(v))
