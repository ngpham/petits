from rrtl import *

# unify functions: alpha-rewrite of free variable, or overwrite with Skolem constant.
class Unifier:
  def __init__(self, sym1, sym2):
    if not isinstance(sym1, Symbol) or not isinstance(sym2, Symbol): raise RuntimeError()
    symbol = None
    if sym1.sym_type == SymbolType.SkolemConst:
      if sym2.sym_type == SymbolType.FreeVar:
        symbol = sym1
      else: pass
    elif sym1.sym_type == SymbolType.FreeVar:
      if (sym2.sym_type == SymbolType.SkolemConst or
          sym2.sym_type == SymbolType.FreeVar):
        symbol = sym2
    self.sym = symbol

  def substitute(self, vertex):
    if self.sym is None: return None
    if vertex.var_sym.sym_type == SymbolType.FreeVar:
      return Vertex(vertex.fun_sym, self.sym)
    else: return vertex

  def __str__(self):
    return str(self.sym)


# construct a new edge (literal) by unifying 2 edges.
# add new attribute for Edge to store the 2 constitutional edges.
def _combine_2_edges(cls, edge1, edge2):
  if not isinstance(edge1, Edge) or not isinstance(edge2, Edge): raise RuntimeError()
  if edge1.dst != edge2.src: raise RuntimeError()
  combined = cls(edge1.src, edge2.dst, edge1.weight + edge2.weight)
  combined.hyper_tuple = (edge1, edge2)
  return combined
setattr(Edge, 'combine_2_edges', classmethod(_combine_2_edges))
setattr(Edge, 'hyper_tuple', None)


def _combine_2_edges_with_unifier(cls, edge1, edge2, uni):
  if not isinstance(edge1, Edge) or not isinstance(edge2, Edge): raise RuntimeError()
  combined = None
  src = uni.substitute(edge1.src)
  dst = uni.substitute(edge2.dst)
  if src is not None and dst is not None:
    combined = cls(src, dst, edge1.weight + edge2.weight)
    combined.hyper_tuple = (edge1, edge2)
  return combined
setattr(Edge, 'combine_2_edges_with_unifier', classmethod(_combine_2_edges_with_unifier))


def _trace_path(edge):
  path = []
  if edge.hyper_tuple is not None:
    path = path + edge.hyper_tuple[0].trace_path()
    path = path + edge.hyper_tuple[1].trace_path()
  else:
    path.append(edge)
  return path
setattr(Edge, 'trace_path', _trace_path)


# An self edge is a cycle in the original graph, however, we need to
# reject "twisted" cycle i.e. 8-form
def _validate_get_cycle(self_edge):
  cycle = self_edge.trace_path()
  vertexes = []
  valid = True
  for arc in cycle:
    is_in_same_cluster = False
    for node in vertexes:
      if node.fun_sym == arc.src.fun_sym:
        is_in_same_cluster = True
        break;
    if is_in_same_cluster:
      valid = False
      break
    vertexes.append(arc.src)
  if valid: return cycle
  else: return None
setattr(Edge, 'validate_get_cycle', _validate_get_cycle)


# consider a vertex, add new edges by combining 1 incomming egde with 1 outgoing.
# also consider the equivalent veretexes (by unification) in the same cluster.
# return any self arcs
def _cycle_invariant_add_with_unification(graph, vertex, cluster):
  if (not isinstance(vertex, Vertex) or
     not isinstance(cluster, VertexCluster)): raise RuntimeError()
  incomming_arcs = []
  outgoing_arcs = []
  self_arcs = []

  for arc in graph.edges:
    if arc.dst == vertex or arc.src == vertex:
      if arc.is_self_edge():
        self_arcs.append(arc)
      elif arc.dst == vertex:
        incomming_arcs.append(arc)
      else:
        outgoing_arcs.append(arc)

  for node in cluster.vertexes:
    Debug.trace('in-cluster vertex: ', vertex)
    if node == vertex:
      for left in incomming_arcs:
        for right in outgoing_arcs:
          new_arc = Edge.combine_2_edges(left, right)
          Debug.trace('new arc added for', vertex, ':', new_arc, 'by:', left, right)
          if new_arc is not None: graph.add_edge(new_arc)
    else:
      Debug.trace('process pair: ', vertex, node)
      uni = Unifier(vertex.var_sym, node.var_sym)
      extra_incomming_arcs = []
      extra_outgoing_arcs = []
      if uni.sym is not None:
        for arc in graph.edges:
          if arc.dst == node or arc.src == node:
            if arc.is_self_edge(): pass # will be considered when we call this function on "node"
            elif arc.dst == node:
              extra_incomming_arcs.append(arc)
            else:
              extra_outgoing_arcs.append(arc)
        for left in extra_incomming_arcs:
          for right in outgoing_arcs:
            new_arc = Edge.combine_2_edges_with_unifier(left, right, uni)
            Debug.trace('new edge added', vertex, node, uni, ':', new_arc)
            if new_arc is not None: graph.add_edge(new_arc)
        for left in incomming_arcs:
          for right in extra_outgoing_arcs:
            new_arc = Edge.combine_2_edges_with_unifier(left, right, uni)
            Debug.trace('new edge added', vertex, node, uni, ':', new_arc)
            if new_arc is not None: graph.add_edge(new_arc)
        # (left in extra_incomming_arcs, right in extra_outgoing_arcs)
        # will be consider when we call this function on "node"
  return self_arcs
setattr(
  Graph,
  'cycle_invariant_add_with_unification',
  _cycle_invariant_add_with_unification)


# keep removing vertices and discover cycles during the process
def _shrink(graph):
  cycles = []
  for fun_sym in sorted(graph.fun_sym_cluster.keys(), key = lambda x: x.name):
    cluster = graph.fun_sym_cluster[fun_sym]
    num_shrinked_vertexes = len(cluster.vertexes)
    while (num_shrinked_vertexes > 0 and len(cluster.vertexes) > 0):
      prev = len(cluster.vertexes)
      vertex = cluster.vertexes[-1]
      Debug.trace('ready to process', vertex)
      self_arcs = (
        graph.cycle_invariant_add_with_unification(vertex, cluster))
      for arc in self_arcs:
        circuit = arc.validate_get_cycle()
        if circuit is not None:
          cycle = Cycle(*circuit)
          cycles.append(cycle)
          Debug.trace('cycle found:', cycle)

      graph.remove_edges_incident(vertex)
      Debug.trace('to remove ', vertex)
      graph.remove_if_isolated(vertex)
      num_shrinked_vertexes = prev - len(cluster.vertexes)

  return cycles
setattr(Graph, 'shrink', _shrink)
