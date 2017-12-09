import pmdbpy
import enum

class DataType(enum.Enum):
  Integer = 1
  String = 2

String2DataType = {
  'S': DataType.String,
  'I': DataType.Integer,
  'STRING': DataType.String,
  'INT': DataType.Integer
}

DataTypeFormat = {
  DataType.Integer: 'i',
  DataType.String: '64p'
}

DataTypeSize = {
  DataType.Integer: 4,
  DataType.String: 64
}

ByteOrderSetting = '!'
