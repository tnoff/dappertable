# DapperTable

Similar to PrettyTable, print formatted tables in python using f-string. Tables returned as a list of formatted strings if requested.

This is useful when printing large tables out to a 3rd party library that caps the length of a message, such as printing a formatted table as a Discord message.

Handles East Asian languages that have double spaced characters. Most of the logic taken from: https://medium.com/@gullevek/python-output-formatting-double-byte-characters-6d6d18d04be3

## Usage

Similar to pretty table, set headers first and then add each individual row.

Example:
```
>>> from dappertable import DapperTable
>>> t = DapperTable([{'name': 'pos', 'length': 3}, {'name': 'title', 'length': 48}])
>>> t.add_row(['1', 'example title'])
>>> t.add_row(['2', 'foo bar example 12345678'])
>>> t.print()
'pos || title                                           
 1   || example title                                   
 2   || foo bar example 12345678                        
>>>
```

You can also pass in a `rows_per_message` value into the initial table, this will split the table into multiple strings. This is useful for clients sending requests via an api, so you can 'paginate' the table in a manner of speaking. I use this alot in my discord bot implementation for example, since each message has a maximum length that can be sent.

```
>>> t = DapperTable([{'name': 'pos', 'length': 3}, {'name': 'title', 'length': 48}], rows_per_message=2)
>>> t.add_row(['1', 'example title'])
>>> t.add_row(['2', 'foo bar example 12345678'])
>>> t.add_row(['3', 'pet that dog'])
>>> t.print()
['pos || title                                           \n1   || example title                                   \n2   || foo bar example 12345678                        ',
 '3   || pet that dog                                    ']
>>>
```