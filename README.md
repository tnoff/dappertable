# DapperTable

Similar to [prettytable](https://pypi.org/project/prettytable/), print formatted tables in python using f-string. Tables can be split into a list of strings if requested, which is useful when sending messages via 3rd party libraries that limit messages on length of a string.

Handles wide characters (including East Asian languages that have double-width spacing) using the [wcwidth](https://pypi.org/project/wcwidth/) library for accurate display width calculations. Initial logic inspired by: [this @gullevek post](https://medium.com/@gullevek/python-output-formatting-double-byte-characters-6d6d18d04be3)

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

### Header Formatting


Similar to pretty table, set headers first and then add each individual row. The `DapperTableHeader` object will set the top header row and the max length of each column. If an column in a row later on is added with a length greater than the one in the column, it will be shortened with a `...` suffix added.

Example:
```
>>> from dappertable import DapperTable, DapperTableHeader, DapperTableHeaderOptions
>>> t = DapperTable(header_options=DapperTableHeaderOptions([DapperTableHeader('pos', 3), DapperTableHeader('name', 10)]))
>>> t.add_row([1, 'foo'])
>>> t.add_row([2, 'example title'])
>>> t.print()
'pos|| name\n----------------\n1  || foo\n2  || example ..'
```

### Pagination Options

If you pass `pagination_options` you can setup output to return a list of strings that match the params.

For example you can use `PaginationRows` with the `rows_per_message` value into the initial table, this will split the table into a list of multiple strings. This is useful for clients sending requests via an API, so you can 'paginate' the table in a manner of speaking.

```
>>> from dappertable import DapperTable, DapperTableHeader, DapperTableHeaderOptions, PaginationRows
>>> t = DapperTable(header_options=DapperTableHeaderOptions([DapperTableHeader('pos', 3), DapperTableHeader('name', 10)]), pagination_options=PaginationRows(2))
>>> t.add_row([1, 'foo'])
>>> t.add_row([2, 'example'])
>>> t.add_row([3, 'bar'])
>>> t.print()
['pos|| name\n----------------', '1  || foo\n2  || example', '3  || bar']
```

You can also use `PaginationLength` to with the `length_per_message` value to split up the output into multiple strings where the max length of each string is this value.

```
>>> from dappertable import DapperTable, PaginationLength
>>> t = DapperTable(pagination_options=PaginationLength(10))
>>> t.add_row('12345')
>>> t.add_row('12345')
>>> t.add_row('12345')

>>> t.print()
['12345\n12345', '12345']
```


### Zero Padding

The headers have an `zero_pad_index` option to format index like column options to include leading 0s to make the output look a bit cleaner. Take the following example:

```
>>> from dappertable import DapperTable, DapperTableHeader, DapperTableHeaderOptions
>>> t = DapperTable(header_options=DapperTableHeaderOptions([DapperTableHeader('pos', 3, zero_pad_index=True), DapperTableHeader('name', 10)]))
>>> for count in range(15):
...     t.add_row([count, 'foo'])
... 
>>> t.print()
'pos|| name\n----------------\n00 || foo\n01 || foo\n02 || foo\n03 || foo\n04 || foo\n05 || foo\n06 || foo\n07 || foo\n08 || foo\n09 || foo\n10 || foo\n11 || foo\n12 || foo\n13 || foo\n14 || foo'

```

### Collapse Newlines

By default `collapse_newlines` is set to True, this removes double newlines (`\n\n`) from outputs.

## Advanced Usage

You can also request a list of rows from after pagination processing and use methods to print these directly. This is if you want to get the pagination for some 'locked' input and edit the `DapperRow` instances themselves.

You can use `get_paginated_rows` to get a List of `DapperRow` objects which contain the formatted or unformatted strings (depending on header inputs), and then pass this data into `print_rows` to get the list of outputs.

If you want you can edit the `DapperRow` object directly with `.edit()` to directly modify input if you want to skip some formatting options.