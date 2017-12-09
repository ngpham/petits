from rrtl import *

class Edge:
  def __init__(self, src, dst, weight):
    if not isinstance(src, Vertex) or not isinstance(dst, Vertex): raise RuntimeError()
    self.src = src
    self.dst = dst
    self.weight = weight

  def contains(self, vertex):
    return self.src == vertex or self.dst == vertex

  def __eq__(self, o):
    return (self.src == o.src and
            self.dst == o.dst and
            self.weight == o.weight)

  def is_self_edge(self):
    return self.src == self.dst

  def __hash__(self):
    return hash(self.src) + hash(self.dst) + self.weight

  def __repr__(self):
    return '{}({}, {}, {})'.format(
      self.__class__.__qualname__,
      repr(self.src),
      repr(self.dst),
      self.weight
    )

  def __str__(self):
    s = '['
    s += str(self.src) + "->" + str(self.dst) + ":" + str(self.weight) + ']'
    return s
