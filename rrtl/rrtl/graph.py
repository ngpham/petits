
from rrtl import *

class Graph:
  def __init__(self):
    self.fun_sym_cluster = {}  # {vertex.fun_sym : cluster}
    self.edges = []

  def _add_vertex(self, v):
    if not isinstance(v, Vertex): raise RuntimeError()
    (self.fun_sym_cluster
      .setdefault(v.fun_sym, VertexCluster(v.fun_sym))
      .add_vertex(v))

  def add_edge(self, e):
    if not isinstance(e, Edge): raise RuntimeError()
    if not e in self.edges:
      self._add_vertex(e.src)
      self._add_vertex(e.dst)
      # e.src.add_dst(e.dst, e.weight)
      self.edges.append(e)

  def remove_edge_keeping_vertexes(self, edge):
    if not isinstance(edge, Edge): raise RuntimeError()
    self.edges.remove(edge)

  def remove_if_isolated(self, vertex):
    if not isinstance(vertex, Vertex): raise RuntimeError()
    for edge in self.edges:
      if edge.contains(vertex): return False
    self.fun_sym_cluster.get(vertex.fun_sym).remove_vertex(vertex)
    return True

  def remove_edges_incident(self, vertex):
    if not isinstance(vertex, Vertex): raise RuntimeError()
    self.edges = [e for e in self.edges if e.src != vertex and e.dst != vertex]

  def __repr__(self):
    s1 = [self.__class__.__qualname__ + '(\n']
    for fun_sym, cluster in self.fun_sym_cluster.items():
      s2 = [repr(cluster) + '\n']
      for v in cluster.vertexes:
        s2.append(' ' + repr(v) + '\n')
      s1.append("".join(s2))
    return "".join(s1) + ')'

  def __str__(self):
    s = ''
    for _, cluster in self.fun_sym_cluster.items():
      s += str(cluster) + '\n'
      for v in cluster.vertexes:
        s += ' ' + str(v)
      s += '\n'
    return s

