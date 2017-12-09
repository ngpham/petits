import pmdbpy

class DataDictionary:
  def __init__(self, dbs):
    self.dbs = dbs
    self.baseRelationMap = {}
    self.initMasterRelation('master')

  def initMasterRelation(self, masterName):
    atbs = list([
      pmdbpy.Attribute(masterName, 'table', pmdbpy.DataType.String),
      pmdbpy.Attribute(masterName, 'attribute', pmdbpy.DataType.String),
      pmdbpy.Attribute(masterName, 'datatype', pmdbpy.DataType.String),
      pmdbpy.Attribute(masterName, 'dbfile', pmdbpy.DataType.String)])

    relation = pmdbpy.BaseRelation.fromAttributes(atbs, masterName)
    dbFile = pmdbpy.DbFile(relation)
    self.baseRelationMap['master'] = (relation, dbFile)

    dbFile.resetFilePointer()
    t = dbFile.readNextTuple()
    tableName = t[0] if t is not None else ''
    temp = []
    while t is not None:
      atb = pmdbpy.Attribute(t[0], t[1], pmdbpy.String2DataType[t[2]])
      if t[0] == tableName:
        temp.append(atb)
      else:
        r = pmdbpy.BaseRelation.fromAttributes(temp)
        f = pmdbpy.DbFile(r)
        self.baseRelationMap[tableName] = (r, f)
        tableName = t[0]
        temp = []
        temp.append(atb)
      t = dbFile.readNextTuple()

    if tableName != '':
      r = pmdbpy.BaseRelation.fromAttributes(temp)
      f = pmdbpy.DbFile(r)
      self.baseRelationMap[tableName] = (r, f)

  def isTableNameExisted(self, tableName):
    return (self.baseRelationMap.get(tableName, None) is not None)

  def getTableTupleByName(self, tableName):
    if (self.isTableNameExisted(tableName)):
      return self.baseRelationMap[tableName]
    else:
      raise Exception('Table ', tableName, 'does not exist.')

  def getMasterTuple(self):
    return self.getTableTupleByName('master')

  def addBaseRelation(self, relation):
    dbFile = pmdbpy.DbFile(relation)
    self.baseRelationMap[list(relation.relationMap.keys())[0]] = (relation, dbFile)

  def removeBaseRelationByName(self, relationName):
    del self.baseRelationMap[relationName]


