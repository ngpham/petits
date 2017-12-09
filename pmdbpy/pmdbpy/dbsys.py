import pmdbpy

class DbSys:
  def __init__(self):
    self.dataDict = pmdbpy.DataDictionary(self)
    self.parser = pmdbpy.Parser(self)

  def executeSQL(self, sql):
    sql.execute(self)

  def shutdown(self):
    pass
