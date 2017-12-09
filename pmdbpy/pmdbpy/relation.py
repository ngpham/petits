import pmdbpy
import copy
import itertools
import functools

class Attribute:
  def __init__(self, relationName, name, dtype):
    self.name = name
    self.dtype = dtype
    self.relationName = relationName

  def __hash__(self):
    return hash((self.name, self.dtype, self.relationName))

  def __eq__(self, other):
    if type(self) is type(other):
      return (
        self.name == other.dtype and
        self.dtype == other.dtype and
        self.relationName == other.relationName
      )
    else: return False
### end Attribute

class TupleIterator:
  def __init__(self, dbfile):
    self.dbfile = dbfile
    self.positionFilter = None
    self.condition = None
  def __iter__(self):
    self.dbfile.resetFilePointer()
    return self
  def __next__(self):
    accepted = True
    while True:
      n = self.dbfile.readNextTuple()
      if n is None:
        raise StopIteration
      else:
        l = list(n)
        if self.condition is not None:
          indexes = self.condition[0]
          const = self.condition[1]
          if len(indexes) == 2:
            if type(l[indexes[0]]) != type(l[indexes[1]]):
              raise Exception('Type mistmached in WHERE condition')
            else:
              accepted = (l[indexes[0]] == l[indexes[1]])
          if len(indexes) == 1:
            if type(l[indexes[0]]) != type(const):
              raise Exception('Type mistmached in WHERE condition')
            else:
              accepted = (l[indexes[0]] == const)
        if accepted: break

    if self.positionFilter is None:
      return tuple(l)
    else:
      return tuple(l[i] for i in self.positionFilter)

class WrappedTupleIterator:
  def __init__(self, iterator):
    self.iter = iterator
    self.positionFilter = None
    self.condition = None
  def __iter__(self):
    self.iter.__iter__()
    return self
  def __next__(self):
    accepted = True
    while True:
      n = next(self.iter)
      if n is None:
        raise StopIteration
      else:
        l = list(n)
        if self.condition is not None:
          indexes = self.condition[0]
          const = self.condition[1]
          if len(indexes) == 2:
            if type(l[indexes[0]]) != type(l[indexes[1]]):
              raise Exception('Type mistmached in WHERE condition')
            else:
              accepted = (l[indexes[0]] == l[indexes[1]])
          if len(indexes) == 1:
            if type(l[indexes[0]]) != type(const):
              raise Exception('Type mistmached in WHERE condition')
            else:
              accepted = (l[indexes[0]] == const)
        if accepted: break

    if self.positionFilter is None:
      return tuple(l)
    else:
      return tuple(l[i] for i in self.positionFilter)


class CrossProductTupleIterator:
  def __init__(self, tupleIter1, tupleIter2):
    self.tupleIter1 = tupleIter1
    self.tupleIter2 = tupleIter2
    self.crossprod = itertools.product(tupleIter1, tupleIter2)
    # a list of positions to return [1, 2, 3]
    self.positionFilter = None
    # a tuple of condition ([pos1, pos2], 1) or ([post1], const)
    # TODO: redesign
    self.condition = None

  def __iter__(self):
    self.crossprod = itertools.product(self.tupleIter1, self.tupleIter2)
    return self

  def __next__(self):
    accepted = True
    try:
      while True:
        n = next(self.crossprod)
        l = [elem for t in n for elem in t]
        if self.condition is not None:
          indexes = self.condition[0]
          const = self.condition[1]
          if len(indexes) == 2:
            if type(l[indexes[0]]) != type(l[indexes[1]]):
              raise Exception('Type mistmached in WHERE condition')
            else:
              accepted = (l[indexes[0]] == l[indexes[1]])
          if len(indexes) == 1:
            if type(l[indexes[0]]) != type(const):
              raise Exception('Type mistmached in WHERE condition')
            else:
              accepted = (l[indexes[0]] == const)
        if accepted: break
    except StopIteration:
      raise StopIteration

    if self.positionFilter is None:
      return tuple(l)
    else:
      return tuple(l[i] for i in self.positionFilter)

class Relation:
  @classmethod
  def fromAttributes(cls, atbs):
    obj = cls()
    for atb in atbs:
      obj.addAttribute(atb)
    return obj

  def __init__(self):
    # [attributes]
    self.attributes = []

    # {relationName: {attributeName:attribute}}
    self.relationMap = {}

    # {attributeName: [attributes]}
    # i.e. same attribute name from multiple relations
    self.attributeMap = {}

    # list of sub-relation
    self.relationList = []

  def __iter__(self):
    return iter(self.attributes)

  def isBase(self): return False

  def __copy__(self):
    obj = self.__class__()
    obj.attributes = self.attributes
    obj.relationMap = self.relationMap
    obj.attributeMap = self.attributeMap
    return obj

  def addRelation(self, relation):
    if not isinstance(relation, Relation):
      raise Exception('Type Error')
    self.relationList.append(relation)
    for atb in relation.attributes:
      self.addAttribute(atb)

  def addAttribute(self, atb):
    relationName = atb.relationName
    attributeName = atb.name

    atbMap = None
    if relationName in self.relationMap:
      atbMap = self.relationMap.get(relationName)
      if attributeName in atbMap:
        raise Exception('Attribute name duplicated: ', attributeName)

    self.attributes.append(atb)

    if atbMap is None:
      atbMap = {}
      self.relationMap[relationName] = atbMap
    atbMap[attributeName] = atb

    atbList = self.attributeMap.get(attributeName, None)
    if atbList is None:
      atbList = []
      self.attributeMap[attributeName] = atbList
    atbList.append(atb)

  def lazyTuples(self, dbs):
    if (len(self.relationList) == 1):
      return WrappedTupleIterator(self.relationList[0].lazyTuples(dbs))

    res = functools.reduce(
        lambda x, y: CrossProductTupleIterator(x, y),
        map(lambda x: x.lazyTuples(dbs), self.relationList))
    return res
### end Relation


class BaseRelation(Relation):
  @classmethod
  def fromAttributes(cls, atbs, filename=''):
    obj = super(BaseRelation, cls).fromAttributes(atbs)
    if filename == '':
      filename = '_' + atbs[0].relationName
    obj.filename = filename
    return obj

  def __init__(self):
    super(BaseRelation, self).__init__()

  @pmdbpy.overrides(Relation)
  def lazyTuples(self, dbs):
    (r ,dbf) = dbs.dataDict.getTableTupleByName(self.attributes[0].relationName)
    return TupleIterator(dbf)

  @pmdbpy.overrides(Relation)
  def isBase(self): return true
### end BaseRelation

class AttributeValue:
  def __init__(self):
    self.dtype = None
    self.nameValue = None
    self.isColumn = False
