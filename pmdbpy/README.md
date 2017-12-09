#### A poor man's database in python
An incomplete relational database.

Database format: master, _table1, _table2, ...

There is no "Drop table", no Key, ... actually this list will get longer than the code.
Instead, let's look at an example of what it can do:

```sql
Create employee (id INT, name STRING, division STRING)
Create salary (id INT, salary INT)
Create head (boss INT, division STRING)
INSERT INTO employee (1, 'Alicia', 'Direction')
INSERT INTO salary( 1, 100000)
INSERT INTO employee (2, 'Bob', 'Production')
INSERT INTO salary (2, 95000)
INSERT INTO head (2, 'Production')
SELECT name, salary FROM employee, salary WHERE id = id
select * from (select * from (select * from employee, salary where id = id), head where id = id)
Select id, name from (Select * from employee, salary Where id = id), head where id = 31
```

#### Dependencies
pyparsing
