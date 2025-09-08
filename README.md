# DapperTable

Similar to [prettytable](https://pypi.org/project/prettytable/), print formatted tables in python using f-string. Tables can be split into a list of strings if requested, which is useful when sending messages via 3rd party libraries that limit messages on length of a string.

Handles East Asian languages that have double spaced characters. Most of the logic taken from: https://medium.com/@gullevek/python-output-formatting-double-byte-characters-6d6d18d04be3

## Usage

Similar to pretty table, set headers first and then add each individual row. The `DapperTableHeader` object will set the top header row and the max length of each column. If an column in a row later on is added with a length greater than the one in the column, it will be shortened with a `...` suffix added.

Example:
```
>>> from dappertable import DapperTable, DapperTableHeader
>>> t = DapperTable([DapperTableHeader('pos', 3), DapperTableHeader('name', 48)])
>>> t.add_row(['1', 'example title'])
>>> t.add_row(['2', 'foo bar example 12345678'])
>>> t.print()
'pos || title                                           
 1   || example title                                   
 2   || foo bar example 12345678                        
>>>
```

If you pass `rows_per_message` value into the initial table, this will split the table into a list of multiple strings. This is useful for clients sending requests via an API, so you can 'paginate' the table in a manner of speaking.

```
>>> t = DapperTable([DapperTableHeader('pos', 3), DapperTableHeader('title', 48)], rows_per_message=2)
>>> t.add_row(['1', 'example title'])
>>> t.add_row(['2', 'foo bar example 12345678'])
>>> t.add_row(['3', 'pet that dog'])
>>> t.print()
['pos || title                                           \n1   || example title                                   \n2   || foo bar example 12345678                        ',
 '3   || pet that dog                                    ']
>>>
```