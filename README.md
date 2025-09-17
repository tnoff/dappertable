# DapperTable

Similar to [prettytable](https://pypi.org/project/prettytable/), print formatted tables in python using f-string. Tables can be split into a list of strings if requested, which is useful when sending messages via 3rd party libraries that limit messages on length of a string.

Handles East Asian languages that have double spaced characters. Most of the logic taken from: https://medium.com/@gullevek/python-output-formatting-double-byte-characters-6d6d18d04be3

## Basic Usage

With no options added at init, just adds rows and prints entire value with newline separation.

```
>>> from dappertable import DapperTable
>>> x = DapperTable()
>>> x.add_row('first row')
True
>>> x.add_row('second row')
True
>>> x.print()
'first row\nsecond row'
```

Use the `rows_per_message` option to return a list of strings instead, with each item in the list matching the max number or rows.

```
>>> from dappertable import DapperTable
>>> x = DapperTable(rows_per_message=3)
>>> x.add_row('first row')
True
>>> x.add_row('second row')
True
>>> x.add_row('third row')
True
>>> x.print()
['first row\nsecond row\nthird row']
```

## Header Formatting


Similar to pretty table, set headers first and then add each individual row. The `DapperTableHeader` object will set the top header row and the max length of each column. If an column in a row later on is added with a length greater than the one in the column, it will be shortened with a `...` suffix added.

Example:
```
>>> from dappertable import DapperTable, DapperTableHeader, DapperTableHeaderOptions
>>> t = DapperTable(header_options=DapperTableHeaderOptions([DapperTableHeader('pos', 3), DapperTableHeader('name', 10)]))
>>> t.add_row([1, 'foo'])
True
>>> t.add_row([2, 'example title'])
True
>>> t.print()
'pos|| name\n----------------\n1  || foo\n2  || example ..'
```

If you pass `rows_per_message` value into the initial table, this will split the table into a list of multiple strings. This is useful for clients sending requests via an API, so you can 'paginate' the table in a manner of speaking.

```
>>> from dappertable import DapperTable, DapperTableHeader, DapperTableHeaderOptions
>>> t = DapperTable(header_options=DapperTableHeaderOptions([DapperTableHeader('pos', 3), DapperTableHeader('name', 10)]), rows_per_message=2)
>>> t.add_row([1, 'foo'])
True
>>> t.add_row([2, 'example'])
True
>>> t.add_row([3, 'bar'])
True
>>> t.print()
['pos|| name\n----------------', '1  || foo\n2  || example', '3  || bar']
```

## Collapse Newlines

By default `collapse_newlines` is set to True, this removes double newlines (`\n\n`) from outputs.