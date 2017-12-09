"""BCNF Grammar
<identifier> ::= <alphanumeric>
<op> ::= "+" | "-"
<fun> ::= <identifier> "(" <identifier> ")"
<atom> ::= <fun> <op> <number> "<=" <fun>
         | <fun> "<=" <fun>
<clause> ::= <atom>
           | <atom> "or" <clause>
<formula> ::= <clause> "\n"
            | <clause> "\n" <formula>
"""

import pyparsing as pp
import rrtl

class _Parser:
  def __init__(self, fun_hook, atom_hook, clause_hook):
    pp.ParserElement.setDefaultWhitespaceChars(' \t')
    kwOr = pp.CaselessKeyword('or')
    leq = pp.Literal('<=')
    oprt = pp.Literal('+') | pp.Literal('-')
    lpar, rpar = map(pp.Suppress, '()')
    number = pp.Word(pp.nums).setParseAction(lambda x: int(x[0]))
    identifier = pp.Word(pp.alphas, pp.alphanums)

    fun = (
      identifier('funName') + lpar + identifier('varName') + rpar
    ).setParseAction(fun_hook)

    atom = (
      (fun('lfun') + oprt('sign') + number('number') + leq + fun('rfun')) |
      (fun('lfun') + leq + fun('rfun'))
    ).setParseAction(atom_hook)

    clause = (
      pp.Suppress(pp.lineStart) + pp.delimitedList(atom, kwOr) + pp.Suppress(pp.lineEnd)
    ).setParseAction(clause_hook)
    self.formula = pp.Group(pp.OneOrMore(clause)) + pp.Suppress(pp.lineEnd)

  def parse(self, input):
    return self.formula.parseString(input)


class Parser:
  def __init__(self, graph, clauses_set):
    def _fun_as_vertex(toks):
      fname = toks['funName']
      vname = toks['varName']
      fsym = rrtl.Symbol(fname, rrtl.SymbolType.Function)
      vsym = (
        rrtl.Symbol(vname, rrtl.SymbolType.FreeVar) if vname == vname.lower() else
        rrtl.Symbol(vname, rrtl.SymbolType.SkolemConst)
      )
      return rrtl.Vertex(fsym, vsym)

    def _atom_as_edge(toks):
      weight = 0
      if toks.get('number') is not None:
        if toks.sign == '+': weight = toks.number
        else: weight = - toks.number
      edge = rrtl.Edge(toks.lfun, toks.rfun, weight)
      graph.add_edge(edge)
      return edge

    def _add_clause(toks):
      clause = rrtl.Clause()
      for lit in toks: clause.add_literal(lit)
      clauses_set.add_clause(clause)
      return toks

    self.delegate = _Parser(_fun_as_vertex, _atom_as_edge, _add_clause)

  def parseSpec2Graph(self, spec):
    try:
      par_res = self.delegate.parse(spec)
    except Exception as e:
      print('Error during parsing')
      raise e
