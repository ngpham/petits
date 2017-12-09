from rrtl import *

class Clause:
  def __init__(self): self.literals = []

  def add_literal(self, literal):
    if not isinstance(literal, Edge): raise RuntimeError()
    self.literals.append(literal)

  def __repr__(self):
    s = [self.__class__.__qualname__ + '(']
    for l in self.literals:
      s.append(repr(l))
    return ''.join(s, ',') + ')'

  def __str__(self):
    s = ''
    for lit in self.literals:
      s += str(lit)
    return s


class ClausesSet:
  def __init__(self):
    self.clauses = []
    self.literal_dict = {}   # {literal:[clause]}

  def add_clause(self, clause):
    if not isinstance(clause, Clause): raise RuntimeError()
    self.clauses.append(clause)
    for literal in clause.literals:
      assoc = self.literal_dict.get(literal)
      if assoc is None: assoc = []
      assoc.append(clause)
      self.literal_dict[literal] = assoc

  def is_unsatisfied_with(self, literals):
    literals_set = set(literals)
    Debug.trace('compare: ', *literals_set)
    for c in self.clauses:
      found_all = True
      Debug.trace('with ', *c.literals)
      for lit in c.literals:
        if lit not in literals_set:
          found_all = False
          break
      if found_all:
        Debug.trace('found unsatisfied clause!')
        return True
    Debug.trace('end-compare')
    return False

  def __str__(self):
    s = 'Begin ClauseSet\n'
    s += ' ' + 'All clauses:\n'
    for clause in self.clauses:
      s += '  ' + str(clause) + '\n'
    s += ' ' + 'Litearl and associative clauses:\n'
    for lit, clauses in self.literal_dict.items():
      s += '  ' + str(lit) + ': ' + str(len(clauses)) + ' clauses\n'
    s += 'End ClauseSet'
    return s


class Cycle(Clause):
  def __init__(self, *edges):
    super(Cycle, self).__init__()
    self.weight = 0
    self.positive = False
    self.negate_positive = False
    for edge in edges:
      self.add_literal(edge)
      self.weight += edge.weight
    if self.weight > 0:
      self.positive = True
    if len(self.literals) - self.weight > 0:
      self.negate_positive = True

  def __str__(self):
    s = ''
    if self.positive: s += 'positive cycle '
    if self.negate_positive: s += 'positive negated cycle '
    s += super(Cycle, self).__str__()
    return s


class Verifier:
  def __init__(self, clauses_set, cycles):
    self.clauses_set = clauses_set
    self.positive_cycles = []
    for c in cycles:
      if c.positive:
        self.positive_cycles.append(c)
      if c.negate_positive:
        self.clauses_set.add_clause(c)

  def verify(self):
    def rec(clauses_set, cycle_index, num_cycles, literals):
      if cycle_index == num_cycles: return False
      for literal in self.positive_cycles[cycle_index].literals:
        literals.append(literal)
        sub_unsatisfied = False
        if clauses_set.is_unsatisfied_with(literals):
          sub_unsatisfied = True
        else:
          sub_unsatisfied = rec(clauses_set, cycle_index + 1, num_cycles, literals)
        del(literals[-1])
        if sub_unsatisfied: return True
      return False

    num_cycles = len(self.positive_cycles)
    return rec(self.clauses_set, 0, num_cycles, [])
