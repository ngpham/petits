import enum
import pmdbpy
import functools

class Command:
  class CommandType(enum.Enum):
    CREATE = 1
    SELECT = 2
    INSERT = 3

  def __init__(self, cmdType):
    self.cmdType = cmdType
    self.cmd = None
    self.attributes = []

  def addAttribute(self, atb):
    self.attributes.append(atb)

  def execute(self): raise Exception('Command not yet supported')
### end Command

class TableExistedException(Exception): pass

class CreateCommand(Command):
  def __init__(self, tableName):
    super(CreateCommand, self).__init__(Command.CommandType.CREATE)
    self.baseRelationName = tableName

  @pmdbpy.overrides(Command)
  def execute(self, dbs):
    try:
      if (dbs.dataDict.isTableNameExisted(self.baseRelationName)):
        raise TableExistedException("Table already existed: " + self.baseRelationName)

      baseRelation = pmdbpy.BaseRelation.fromAttributes(self.attributes)
      tupleList = []
      for atb in baseRelation.attributes:
        if atb.dtype == pmdbpy.DataType.String:
          datatype = 'S'
        elif atb.dtype == pmdbpy.DataType.Integer:
          datatype = 'I'
        else: raise Exception('Unknown data type')
        tupleList.append((
          self.baseRelationName,
          atb.name,
          datatype,
          baseRelation.filename))

      (masterRelation, masterFile) = dbs.dataDict.getMasterTuple()
      for t in tupleList:
        masterFile.writeTuple(t)

      dbs.dataDict.addBaseRelation(baseRelation)
      print ('------Table Created Successfully')
    except TableExistedException as e:
      print('Error executing sql: ', e)
    except Exception as e:
      print('Error executing sql: ', e)
      if (dbs.dataDict.isTableNameExisted(self.baseRelationName)):
        dbs.dataDict.removeBaseRelationByName(self.baseRelationName)

class InsertCommand(Command):
  def __init__(self, tableName):
    super(InsertCommand, self).__init__(Command.CommandType.INSERT)
    self.baseRelationName = tableName

  def setValueTuple(self, vt):
    self.valueTuple = vt

  @pmdbpy.overrides(Command)
  def execute(self, dbs):
    try:
      (relation, dbFile) = dbs.dataDict.getTableTupleByName(self.baseRelationName)
      dbFile.writeTuple(self.valueTuple)
      print ('Row inserted into database')
    except Exception as e:
      print('Error executing sql: ', e)


class SelectCommand(Command):
  def __init__(self):
    super(SelectCommand, self).__init__(Command.CommandType.SELECT)
    self.selectClause = SelectClause()

  def execute(self, dbs):
    self.selectClause.prepare(dbs)
    lazyTuples = self.selectClause.lazyTuples(dbs)
    count = 0

    if (self.selectClause.selectList == '*'):
      selected = self.selectClause.flatAtbNameList
    else:
      selected = self.selectClause.selectList

    print("<" + "--".join(selected) + ">")
    for row in lazyTuples:
      l = [str(x) for x in row]
      count += 1
      print(" ".join(l))
    print("===={} rows found".format(count))


class WhereClause:
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs
  def __str__(self):
    return (self.lhs.nameValue + ' = ' + self.rhs.nameValue)


class SelectClause(pmdbpy.Relation):
  def __init__(self):
    super(SelectClause, self).__init__();
    self.whereClause = None
    self.selectList = []
    self.flatAtbNameList = []
    self.relationName = None
    self.relation = pmdbpy.Relation()

  def setWhereClause(self, whereClause):
    self.whereClause = whereClause

  def setSelectList(self, atbNameList):
    self.selectList = atbNameList

  def prepare(self, dbs):
    for r in self.relation.relationList:
      if isinstance(r, SelectClause):
        r.prepare(dbs)
        if (r.selectList[0] == '*'):
          for atbName in r.flatAtbNameList:
            self.flatAtbNameList.append(atbName)
        else:
          for atbName in r.selectList:
            self.flatAtbNameList.append(atbName)
      else:
        for atb in r.attributes:
          self.flatAtbNameList.append(atb.name)

  @pmdbpy.overrides(pmdbpy.Relation)
  def lazyTuples(self, dbs):
    res = self.relation.lazyTuples(dbs)
    if (self.selectList[0] == '*'):
      res.positionFilter = None
      self.selectList = self.flatAtbNameList
    else:
      res.positionFilter = list(map(lambda x: self.flatAtbNameList.index(x),
                                    self.selectList))
    if (self.whereClause is not None):
      lhs = self.whereClause.lhs
      rhs = self.whereClause.rhs
      if (lhs.isColumn and rhs.isColumn):
        pos = list(map(lambda x: self.flatAtbNameList.index(x),
                  [lhs.nameValue, rhs.nameValue]))
        pos1 = [i for i, x in
          enumerate(self.flatAtbNameList) if x == lhs.nameValue]
        pos2 = [i for i, x in
          enumerate(self.flatAtbNameList) if x == rhs.nameValue]
        if len(set(pos1) | set(pos2)) != 2:
          raise Exception('WHERE Clause: "' + str(self.whereClause) +
            '" Ambiguity in column names')
        res.condition = ([pos1[0], pos2[-1]], 1)
      elif (lhs.isColumn and not rhs.isColumn):
        pos = list(map(lambda x: self.flatAtbNameList.index(x),
                  [lhs.nameValue]))
        res.condition = (pos, rhs.nameValue)
      else:
        raise Exception('WHERE Clause: "' + str(self.whereClause) +
          '" is not supported. Please use: column = column OR column = const')

    return res
