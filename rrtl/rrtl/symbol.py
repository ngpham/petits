import enum

class SymbolType(enum.Enum):
  Function = 1
  FreeVar = 2
  SkolemConst = 3


class Symbol:
  @classmethod
  def default_free_var(cls):
    return cls('x', SymbolType.FreeVar)

  def __init__(self, name, sym_type):
    self.name = name
    self.sym_type = sym_type

  def __repr__(self):
    return '{}({}, {})'.format(
      self.__class__.__qualname__,
      self.name,
      repr(self.sym_type)
    )

  def __str__(self):
    return self.name

  def __eq__(self, o):
    return (self.name == o.name and self.sym_type == o.sym_type)

  def __hash__(self):
    return hash(self.name) + hash(self.sym_type)
