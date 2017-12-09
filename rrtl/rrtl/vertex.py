from rrtl import *

class Vertex:
  def __init__(self, fun_sym, var_sym):
    if (not isinstance(fun_sym, Symbol) or
        not isinstance(var_sym, Symbol)): raise RuntimeError()
    self.fun_sym = fun_sym
    self.var_sym = var_sym

  def __repr__(self):
    return '{}({}, {})'.format(
      self.__class__.__qualname__,
      repr(self.fun_sym),
      repr(self.var_sym)
    )

  def __str__(self):
    s = 'Vertex:' + str(self.fun_sym) + '(' + str(self.var_sym) + ')'
    return s

  def __eq__(self, other):
    return (self.fun_sym == other.fun_sym and self.var_sym == other.var_sym)
  def __hash__(self):
    return hash(self.fun_sym) + hash(self.var_sym)


class VertexCluster:
  def __init__(self, fun_sym):
    if not isinstance(fun_sym, Symbol): raise RuntimeError()
    self.fun_sym = fun_sym
    self.vertexes = []

  def add_vertex(self, vertex):
    if not isinstance(vertex, Vertex): raise RuntimeError()
    if vertex not in self.vertexes:
      self.vertexes.append(vertex)

  def remove_vertex(self, vertex):
    if not isinstance(vertex, Vertex): raise RuntimeError()
    self.vertexes.remove(vertex)

  def get_vertex(self, tup_sym):
    if type(tup_sym) is not tuple: raise RuntimeError()
    if self.fun_sym != tup_sym[0]: raise RuntimeError()
    return next((v for v in self.vertexes if v.var_sym == tup_sym[1]), None)

  def __repr__(self):
    return '{}({})'.format(
      self.__class__.__qualname__,
      repr(self.fun_sym)
    )

  def __str__(self):
    return 'Cluster:' + str(self.fun_sym)
