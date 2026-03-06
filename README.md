# DapperTable

A Python library for building formatted, paginated text tables — designed for bots and CLI tools that need to send output in chunks.

Handles wide characters (including East Asian languages) using the [wcwidth](https://pypi.org/project/wcwidth/) library. Initial logic inspired by [this @gullevek post](https://medium.com/@gullevek/python-output-formatting-double-byte-characters-6d6d18d04be3).

## Installation

```
$ git clone https://github.com/tnoff/dappertable.git
$ pip install dappertable/
```

## Core Concepts

- **`Column(name, width)`** — defines a column with a header name and max display width. Values wider than `width` are truncated with `..`.
- **`Columns([...])`** — groups columns together, with an optional separator string (default `||`).
- **`PaginationLength(n)`** — splits output into pages where each page is at most `n` characters.
- **`PaginationRows(n)`** — splits output into pages of at most `n` rows each.
- **`prefix`** — text prepended to the first page only.
- **`suffix`** — text appended to the last page only.
- **`enclosure_start` / `enclosure_end`** — text wrapped around the content of *every* page (e.g. markdown code fences).

## Basic Usage

Without columns, `DapperTable` just joins rows with newlines:

```python
from dappertable import DapperTable

table = DapperTable()
table.add_row('first row')
table.add_row('second row')
print(table.render())
# 'first row\nsecond row'
```

## Formatted Table with Columns

Define columns up front — each row must then be a list matching the column count. Values that exceed the column width are truncated with `..`:

```python
from dappertable import DapperTable, Column, Columns

table = DapperTable(columns=Columns([
    Column('Pos', 3),
    Column('Title', 30),
    Column('Uploader', 20),
]))
table.add_row(['1', 'My Favourite Song', 'Some Artist'])
table.add_row(['2', 'A Very Long Title That Will Get Cut Off Here', 'Another Artist'])
print(table.render())
```

Output:
```
Pos|| Title                         || Uploader
--------------------------------------------------
1  || My Favourite Song             || Some Artist
2  || A Very Long Title That Will.. || Another Artist
```

## Discord Bot Example

The most common use case: send a paginated, code-block-wrapped table as multiple Discord messages. Discord has a 2000 character message limit, so `PaginationLength(2000)` splits the table automatically. `enclosure_start` and `enclosure_end` wrap each page in a markdown code fence so the table renders with monospace formatting. `prefix` adds a title to the first page.

```python
from dappertable import DapperTable, Column, Columns, PaginationLength

DISCORD_MAX_MESSAGE_LENGTH = 2000

table = DapperTable(
    columns=Columns([
        Column('Pos', 3, zero_pad=True),
        Column('Title', 40),
        Column('Uploader', 40),
    ]),
    pagination_options=PaginationLength(DISCORD_MAX_MESSAGE_LENGTH),
    enclosure_start='```\n',
    enclosure_end='\n```',
    prefix='Now Playing Queue\n',
)

queue = [
    ('Yours', 'Yuki Saito'),
    ('禁断のテレパシー', '工藤静香'),
    ('Crystal Night', '1986 OMEGA TRIBE'),
]
for i, (title, uploader) in enumerate(queue, 1):
    table.add_row([str(i), title, uploader])

for message in table.render():
    # channel.send(message)  # each string fits within Discord's limit
    print(message)
    print()
```

Output (single page in this case):
```
Now Playing Queue
` `` `
Pos|| Title                                    || Uploader
------------------------------------------------------------
01 || Yours                                    || Yuki Saito
02 || 禁断のテレパシー                           || 工藤静香
03 || Crystal Night                            || 1986 OMEGA TRIBE
` `` `
```

When the table is long enough to span multiple pages, each page gets its own code fence, and the prefix only appears on the first page.

### Playlist List Example

```python
table = DapperTable(
    columns=Columns([
        Column('ID', 3),
        Column('Playlist Name', 64),
        Column('Last Queued', 20),
    ]),
    pagination_options=PaginationLength(DISCORD_MAX_MESSAGE_LENGTH),
    enclosure_start='```\n',
    enclosure_end='\n```',
    prefix='Playlist List\n',
)

for i, (name, last_queued) in enumerate(playlists):
    table.add_row([str(i), name, last_queued])

for message in table.render():
    pass  # channel.send(message)
```

## Pagination Options

### By character length

```python
from dappertable import DapperTable, PaginationLength

table = DapperTable(pagination_options=PaginationLength(20))
table.add_row('row one')    # 7 chars
table.add_row('row two')    # 7 chars (total 15 with newline)
table.add_row('row three')  # 9 chars (would exceed 20)
print(table.render())
# ['row one\nrow two', 'row three']
```

### By row count

```python
from dappertable import DapperTable, PaginationRows

table = DapperTable(pagination_options=PaginationRows(2))
table.add_row('alpha')
table.add_row('beta')
table.add_row('gamma')
print(table.render())
# ['alpha\nbeta', 'gamma']
```

## Prefix and Suffix

`prefix` is prepended to the first page; `suffix` is appended to the last. When using `PaginationLength`, their character widths are accounted for in the page size calculation.

```python
from dappertable import DapperTable, PaginationLength

table = DapperTable(
    pagination_options=PaginationLength(2000),
    prefix='Results:\n',
    suffix='\nPage 1 of 1',
)
table.add_row('some data')
print(table.render())
# ['Results:\nsome data\nPage 1 of 1']
```

## Enclosure

`enclosure_start` and `enclosure_end` wrap the content of *every* page. This is the right tool for markdown code fences when paginating, since each page needs its own opening and closing fence.

The page layout order is: `prefix` → `enclosure_start` → content → `enclosure_end` → `suffix`.

```python
from dappertable import DapperTable, PaginationLength

table = DapperTable(
    pagination_options=PaginationLength(50),
    prefix='**Table:**\n',
    enclosure_start='```\n',
    enclosure_end='\n```',
)
table.add_row('row 1')
table.add_row('row 2')
print(table.render())
# ['**Table:**\n```\nrow 1\nrow 2\n```']
```

## Zero Padding

Set `zero_pad=True` on a `Column` to left-pad numeric index values with zeros. The padding width is determined automatically from the total row count, so it stays consistent as rows are added:

```python
from dappertable import DapperTable, Column, Columns

table = DapperTable(columns=Columns([
    Column('Pos', 3, zero_pad=True),
    Column('Name', 10),
]))
for i in range(12):
    table.add_row([str(i), f'item {i}'])
print(table.render())
# Pos|| Name
# --------------
# 00 || item 0
# 01 || item 1
# ...
# 11 || item 11
```

## Custom Column Separator

The default column separator is `||`. Override it per `Columns` instance:

```python
from dappertable import DapperTable, Column, Columns

table = DapperTable(columns=Columns(
    [Column('A', 5), Column('B', 5)],
    separator='|',
))
table.add_row(['foo', 'bar'])
print(table.render())
# A    | B
# -----------
# foo  | bar
```

## Modifying Rows

```python
from dappertable import DapperTable

table = DapperTable()
table.add_row('original')
table.add_row('keep this')
table.edit_row(0, 'updated')
table.remove_row(0)
print(table.render())
# 'keep this'

print(len(table))  # 1
```

## Advanced: Accessing Pages Directly

Use `get_pages()` and `format_page()` when you want to inspect or modify the paginated rows before rendering:

```python
from dappertable import DapperTable, Column, Columns, PaginationLength

table = DapperTable(
    columns=Columns([Column('pos', 3), Column('name', 10)]),
    pagination_options=PaginationLength(30),
)
table.add_row(['1', 'foo'])
table.add_row(['2', 'bar'])

pages = table.get_pages()
for page in pages:
    print(table.format_page(page))
```

Individual rows can also be edited directly via `DapperRow.edit()` to bypass column formatting:

```python
pages[0][0].edit('custom content')
print(table.format_page(pages[0]))
```
