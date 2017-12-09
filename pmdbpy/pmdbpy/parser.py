import pmdbpy
import pyparsing as pp
import pprint

""" The BNF Grammar

<select> ::= "SELECT" <select list> <table expression>

<select list> ::= "*" | <select sublist>

<select sublist> ::= <column-identifier> | <column-identifier> "," <select sublist>

<table expression> ::= <from clause> [<where clause>]

<from clause> ::= "FROM" <table reference list>

<table reference list> ::= <table reference> | <table reference> "," <table reference list>

<table reference> ::= <table primary> | <join table>

<table primary> ::= <table-identifier> | <sub query>

<sub query> ::=  "(" <select> ")"

<where clause> ::= "WHERE" <comparison predicate>

<comparison predicate> ::= <row value predicand> <comparison predicate part2>

<comparison predicate part2> ::= "=" <row value predicand>

<row value predicand> ::= <identifier> | <number> | <string>

<string> ::= "'" [a-Z0-9]* "'"
<number> ::= [0..9]*
<value> ::= <number> | <string>
<value list> ::= <value> | <value>, <value list>
"""

kwSelect = pp.CaselessKeyword('SELECT')
kwFrom = pp.CaselessKeyword('FROM')
kwCreate = pp.CaselessKeyword('CREATE')
kwInt = pp.CaselessKeyword('INT')
kwString = pp.CaselessKeyword('STRING')
kwWhere = pp.CaselessKeyword('WHERE')
kwInsert = pp.CaselessKeyword('INSERT')
kwInto = pp.CaselessKeyword('INTO')
comma = pp.Literal(',')
eqcomp = pp.Literal('=')
star = pp.Literal('*')
leftp, rightp = map(pp.Suppress, "()")

def toInteger(toks):
  return int(toks[0])

identifier = pp.Word(pp.alphas, pp.alphanums).setParseAction(pp.downcaseTokens)
number = pp.Word(pp.nums).setParseAction(toInteger)
sqString = pp.sglQuotedString.setParseAction(pp.removeQuotes)
selectList = pp.Group(pp.delimitedList(identifier) | star)
value = number('number') | sqString('string')
valueList = pp.delimitedList(value)
column = pp.Group(identifier('name') + (kwInt | kwString)('dtype'))
columnList = pp.delimitedList(column)

def nameGenerator(x):
  while True:
    yield ('_tmpTable_' + str(x))
    x += 1
relationNameGen = nameGenerator(0)

class DbsRef:
  dbs = None

def genSelectCommand(toks):
  rel = pmdbpy.SelectCommand()
  rel.selectClause.relationName = next(relationNameGen)
  rel.selectClause.relation = toks.tableReferenceList
  rel.selectClause.setSelectList(toks.selectList)
  if (toks.where != ''):
    rel.selectClause.setWhereClause(pmdbpy.WhereClause(
        toks.where.comparison.lhs,
        toks.where.comparison.rhs))
  return rel

def genSelectClause(toks):
  rel = pmdbpy.SelectClause()
  rel.relationName = next(relationNameGen)
  rel.setSelectList(toks.sqlSelect.selectList)
  rel.relation = toks.sqlSelect.tableReferenceList
  if (toks.where != ''):
    rel.setWhereClause(pmdbpy.WhereClause(
        toks.sqlSelect.where.comparison.lhs,
        toks.sqlSelect.where.comparison.rhs))
  return rel

def genTable(toks):
  return (DbsRef.dbs.dataDict.getTableTupleByName(toks.table)[0])

def genTableList(toks):
  rel = pmdbpy.Relation()
  for r in toks:
    rel.addRelation(r)
  return rel

def genValue(toks):
  value = pmdbpy.AttributeValue()
  if (toks.number != ''):
    value.dtype = pmdbpy.DataType.Integer
    value.nameValue = toks.number
    value.isColumn = False
  elif (toks.string != ''):
    value.dtype = pmdbpy.DataType.String
    value.nameValue = toks.string
    value.isColumn = False
  elif (toks.column != ''):
    value.nameValue = toks.column
    value.isColumn = True
  return value

subquery = pp.Forward().setParseAction(genSelectClause)
colValue = (number('number') | sqString('string') | identifier('column'))
comparison = pp.Group(colValue('lhs').setParseAction(genValue)
                      + '='
                      + colValue('rhs').setParseAction(genValue))
where = (kwWhere + comparison('comparison'))

tableReference = identifier('table').addParseAction(genTable) | subquery('subquery')
tableReferenceList = pp.delimitedList(tableReference)

sqlSelect = (kwSelect +
  selectList('selectList') + kwFrom +
  tableReferenceList('tableReferenceList').setParseAction(genTableList) +
  pp.Optional(where('where'))
)

subquery << leftp + sqlSelect('sqlSelect') + rightp

sqlCreate = (kwCreate +
  identifier('table') + '(' + columnList('columnList') + ')'
)

sqlInsert = (kwInsert + kwInto + identifier('table') +
  leftp + valueList('valueList') + rightp)

command = (pp.stringStart +
  (sqlSelect('sqlSelect').setParseAction(genSelectCommand)
   | sqlCreate('sqlCreate')
   | sqlInsert('sqlInsert'))
  + pp.stringEnd)

class Parser:
  def __init__(self, dbs):
    self.command = command
    self.dbs = dbs
    DbsRef.dbs = dbs

  def parseSql(self, sqlCmd):
    try:
      parseRes = self.command.parseString(sqlCmd)
    except pp.ParseException as e:
      raise Exception('Syntax error: ' + '"' + e.pstr[:(e.loc+1)] + '": '+e.msg)

    if parseRes.sqlCreate != '':
      sql = pmdbpy.CreateCommand(parseRes.table)
      for col in parseRes.columnList:
        sql.addAttribute(
          pmdbpy.Attribute(parseRes.table, col[0], pmdbpy.String2DataType[col[1]]))
    elif parseRes.sqlInsert != '':
      sql = pmdbpy.InsertCommand(parseRes.table)
      if not self.dbs.dataDict.isTableNameExisted(parseRes.table):
        raise Exception("Table does not exist: " + parseRes.table)
      (table, dbfile) = self.dbs.dataDict.getTableTupleByName(parseRes.table)
      if len(table.attributes) != len(parseRes.valueList):
        raise Exception('Mismatch number of attributes')
      valueTuple = ()
      for (atb, value) in zip(table.attributes, parseRes.valueList):
        if atb.dtype == pmdbpy.DataType.Integer:
          try:
            v = int(value)
          except Exception as e:
            raise Exception('Cannot convert to INT as required by: ' + atb.name)
        elif atb.dtype == pmdbpy.DataType.String:
          v = value
        valueTuple += (v,)

      sql.setValueTuple(valueTuple)
    elif parseRes.sqlSelect != '':
      sql = parseRes.sqlSelect
      # sql.gen(self.dbs)
      # sql = sql.selectCommand
    else:
      raise Exception('Unknow query/command')

    return sql

