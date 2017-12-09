import pmdbpy
import itertools
import cmd

samples = [
    "Create employee (id INT, name STRING, division STRING)",
    "Create salary (id INT, salary INT)",
    "Create head (boss INT, division STRING)",
    "INSERT INTO employee (1, 'Alicia', 'Direction')",
    "INSERT INTO salary( 1, 100000)",
    "INSERT INTO employee (2, 'Bob', 'Production')",
    "INSERT INTO salary (2, 95000)",
    "INSERT INTO head (2, 'Production')",
    "Select * from employee",
    "Select * from salary",
    "Select * from head",
    "SELECT name, salary FROM employee, salary WHERE id = id",
    "Select * from employee, salary",
    "Select * from Employee, (Select * from Head)",
    "Select * from (SELECT * from HEAD), (Select * from Salary)",
    "select id, name from employee",
    "Select name, salary from (select id, name from employee), salary",
    "Select name, salary from (select id, name from employee), salary where id = id",
    "Select name, salary from (select id, name from employee), salary where id = name",
    "Select * from (select name, salary from employee, salary where id = id)",
    "select * from (select * from (select * from employee, salary where id = id))",
    "select * from (select * from (select * from employee, salary where id = id), head)",
    "select * from (select * from (select * from employee, salary where id = id), head where id = id)",
    "select * from (select * from (select * from head))",
    "Select * from (select name, salary from employee, salary where id = id) where salary = 95000",
    "Select id, name from (Select * from employee, salary Where id = id), head where id = 31",
  ]

class PoorManSqlCmd(cmd.Cmd):
  intro ='''
    This is a poor man's sql implementation.
    Support nested query and simple WHERE clause.
    Database format: master, _table1, _table2, ...
    There is no "Drop table", please manually delete if needed.
    There is no Key, thus duplication insertion is not detected.
    Type "execute_samples" to generate a sample database and execute some commands.
    Type "exit" to quit.'''

  prompt = '(pmdbpy) '

  def __init__(self, dbs):
    super(PoorManSqlCmd, self).__init__()
    self.dbs = dbs

  def default(self, line):
    if line == 'exit': exit(0)
    elif line == 'execute_samples':
      for sample in samples:
        try:
          print("*** ", sample)
          sql = self.dbs.parser.parseSql(sample)
          self.dbs.executeSQL(sql)
        except Exception as e: print(e)
    else:
      try:
        sql = self.dbs.parser.parseSql(line)
        self.dbs.executeSQL(sql)
      except Exception as e: print(e)

  def emptyline(self): pass


def main():
  dbs = pmdbpy.DbSys()
  pmdbpyShell = PoorManSqlCmd(dbs)
  pmdbpyShell.cmdloop()

if __name__ == '__main__': main()
