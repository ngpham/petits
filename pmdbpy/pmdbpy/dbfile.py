import pmdbpy
import struct

class DbFile:
  def __init__(self, relation):
    if not isinstance(relation, pmdbpy.BaseRelation):
      raise Exception('BaseRelation expected')
    self.filename = relation.filename

    self.fmt = pmdbpy.ByteOrderSetting
    self.recordSize = 0
    for atb in relation.attributes:
      self.fmt += pmdbpy.DataTypeFormat[atb.dtype]
      self.recordSize += pmdbpy.DataTypeSize[atb.dtype]
    try:
      self.dbf = open(self.filename, 'r+b')
    except FileNotFoundError:
      self.dbf = open(self.filename, 'w+b')

  def __enter__(self):
    try:
      self.dbf = open(self.filename, 'r+b')
    except FileNotFoundError:
      self.dbf = open(self.filename, 'w+b')
    return self

  def __exit__(self, *argv):
    self.dbf.flush()
    self.dbf.close()

  def writeTuple(self, values):
    rawTuple = DbFile.tuple2raw(values)
    binary = struct.pack(self.fmt, *rawTuple)
    self.dbf.seek(0, 2)
    self.dbf.write(binary)
    self.dbf.flush()

  def resetFilePointer(self):
    self.dbf.seek(0)

  def readNextTuple(self):
    binary = self.dbf.read(self.recordSize)
    if len(binary) == 0: return None
    raw = struct.unpack(self.fmt, binary)
    return DbFile.raw2tuple(raw)

  @classmethod
  def tuple2raw(self, values):
    def toRaw(x):
      if isinstance(x, int):
        return x
      elif isinstance(x, str):
        return bytes(x, 'ascii')

    return tuple(map(toRaw, values))

  @classmethod
  def raw2tuple(self, byteStrList):
    def toValue(x):
      if isinstance(x, bytes):
        return str(x, 'ascii')
      elif isinstance(x, int):
        return x
      else:
        raise Exception('Unsupported type encountered')

    return tuple(map(toValue, byteStrList))
### end DbFile
