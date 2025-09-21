import pytest

from dappertable import shorten_string_cjk, format_string_length
from dappertable import DapperTable, DapperTableHeader, DapperTableHeaderOptions, DapperTableException
from dappertable import PaginationRows, PaginationLength

def test_shorten_string_cjk():
    input = 'Some string 123 other text'
    assert shorten_string_cjk(input, 5) == 'Som..'
    assert shorten_string_cjk(input, 50) == input
    input = '日本語は'
    assert shorten_string_cjk(input, 10) == input
    assert shorten_string_cjk(input, 7) == '日本..'
    input = 'あいうえおかきくけこさしす 1 other text'
    assert shorten_string_cjk(input, 36) == 'あいうえおかきくけこさしす 1 other..'

def test_format_string_length():
    input = 'Some string 123 other text'
    assert format_string_length(input, 20) == 20
    input = '日本語は'
    assert format_string_length(input, 20) == 16
    input = 'あいうえおかきくけこさしす 1 other text'
    assert format_string_length(input, 32) == 19
    input1 = 'Some string すせそなにぬねのまみむめも〜'
    input2 = 'SOME OTHER STRING THAT IS LONG'
    input1_string = shorten_string_cjk(input1, 50)
    input2_string = shorten_string_cjk(input2, 50)
    input1_length = format_string_length(input1_string, 50)
    input2_length = format_string_length(input2_string, 50)
    new_string = f'||{input1_string:{input1_length}}||\n||{input2_string:{input2_length}}||'
    assert new_string == '||Some string すせそなにぬねのまみむめも〜          ||\n||SOME OTHER STRING THAT IS LONG                    ||'

def test_dapper_table():
    headers = [
        DapperTableHeader('Pos', 3),
        DapperTableHeader('Title', 48),
        DapperTableHeader('Uploader', 32),
    ]
    x = DapperTable(header_options=DapperTableHeaderOptions(headers))
    x.add_row(['1', '[HQ] toe - 孤独の発明 ( Kodoku No Hatsumei)', 'Hui Hon Man'])
    x.add_row(['2', '"Tremelo + Delay" by Toe', 'Topshelf Records'])
    x.add_row(['3', '"むこう岸が視る夢" by Toe', 'Topshelf Records'])
    x.add_row(['4', '"All I Understand Is That I Don_t Understand" - Toe', 'Topshelf Records'])
    x.add_row(['5', '"C" by Toe', 'Topshelf Records'])
    result = x.print()
    assert result == 'Pos|| Title                                           || Uploader\n'\
                     '-----------------------------------------------------------------------------------------\n'\
                     '1  || [HQ] toe - 孤独の発明 ( Kodoku No Hatsumei)     || Hui Hon Man\n'\
                     '2  || "Tremelo + Delay" by Toe                        || Topshelf Records\n'\
                     '3  || "むこう岸が視る夢" by Toe                     || Topshelf Records\n'\
                     '4  || "All I Understand Is That I Don_t Understand" ..|| Topshelf Records\n'\
                     '5  || "C" by Toe                                      || Topshelf Records'


def test_dapper_table_rows():
    headers = [
        DapperTableHeader('pos', 3),
        DapperTableHeader('name', 4),
    ]
    x = DapperTable(header_options=DapperTableHeaderOptions(headers), pagination_options=PaginationRows(2))
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    result = x.print()
    assert result == ['pos|| name\n----------', '1  || a\n2  || b', '3  || c']

def test_dapper_table_length():
    headers = [
        DapperTableHeader('pos', 3),
        DapperTableHeader('name', 4),
    ]
    x = DapperTable(header_options=DapperTableHeaderOptions(headers), pagination_options=PaginationRows(2))
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    result = x.size
    assert result == 3


def test_dapper_table_split_length():
    x = DapperTable(pagination_options=PaginationLength(10))
    x.add_row('1234')
    x.add_row('1234')
    x.add_row('1234')
    assert x.print() == ['1234\n1234', '1234']

    x = DapperTable(pagination_options=PaginationLength(10))
    x.add_row('123456789')
    x.add_row('123456789')
    x.add_row('123456789')
    assert x.print() == ['123456789', '123456789', '123456789']

    x = DapperTable(pagination_options=PaginationLength(10))
    x.add_row('1234')
    x.add_row('1234')
    x.add_row('1234')
    x.add_row('123456789')
    assert x.print() == ['1234\n1234', '1234', '123456789']


def test_dapper_table_split_length_invalid_input():
    x = DapperTable(pagination_options=PaginationLength(10))
    x.add_row('1234789012345')
    with pytest.raises(DapperTableException) as error:
        x.print()
    assert 'Length of input "1234789012345" is greater than iteration max length 10' in str(error.value)
    with pytest.raises(DapperTableException) as error:
        DapperTable(pagination_options=PaginationLength(-5))
    assert 'Invalid value for length per message: -5' in str(error.value)

def test_dapper_table_no_headers_no_rows():
    with pytest.raises(DapperTableException) as error:
        DapperTable(header_options=DapperTableHeaderOptions([]))
    assert 'Must have at least one header' in str(error.value)
    with pytest.raises(DapperTableException) as invalid_error:
        DapperTable(header_options=DapperTableHeaderOptions(DapperTableHeader('name', 5)), pagination_options=PaginationRows(-1))
    assert 'Invalid value for rows per message: -1' in str(invalid_error.value)
    with pytest.raises(DapperTableException) as invalid_row:
        DapperTableHeaderOptions('foo')
    assert 'Header must be DapperTableHeader object' in str(invalid_row.value)

def test_add_invalid_row():
    headers = [
        DapperTableHeader('pos', 3),
        DapperTableHeader('name', 4),
    ]
    x = DapperTable(header_options=DapperTableHeaderOptions(headers), pagination_options=PaginationRows(2))
    with pytest.raises(DapperTableException) as error:
        x.add_row(['foo'])
        assert 'Row length must match length of headers' in str(error.value)

def test_delete_row():
    headers = [
        DapperTableHeader('pos', 3),
        DapperTableHeader('name', 4)
    ]
    x = DapperTable(header_options=DapperTableHeaderOptions(headers), pagination_options=PaginationRows(2))
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    x.remove_row(1)
    result = x.size
    assert result == 2
    result = x.print()
    assert result == ['pos|| name\n----------', '1  || a\n3  || c']
    with pytest.raises(DapperTableException) as error:
        x.remove_row(99)
        assert 'Invalid deletion index' in str(error.value)

def test_separator_override():
    headers = [
        DapperTableHeader('pos', 3),
        DapperTableHeader('name', 4)
    ]
    x = DapperTable(header_options=DapperTableHeaderOptions(headers, separator='+'), pagination_options=PaginationRows(2))
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    x.remove_row(1)
    result = x.size
    assert result == 2
    result = x.print()
    assert result == ['pos+ name\n---------', '1  + a\n3  + c']

def test_no_headers_basic():
    x = DapperTable()
    x.add_row('foo bar stuff')
    x.add_row('more stuff here')
    assert x.size == 2
    result = x.print()
    assert result == 'foo bar stuff\nmore stuff here'
    x.remove_row(0)
    assert x.print() == 'more stuff here'

def test_no_headers_with_messages_per_set():
    x = DapperTable(pagination_options=PaginationRows(2))
    x.add_row('foo bar stuff')
    x.add_row('more stuff here')
    x.add_row('another row just for fun')
    assert x.size == 3
    result = x.print()
    assert result == ['foo bar stuff\nmore stuff here', 'another row just for fun']

def test_invalid_row_add():
    x = DapperTable(DapperTableHeaderOptions([DapperTableHeader('pos', 3), DapperTableHeader('name', 5)]))
    with pytest.raises(DapperTableException) as error:
        x.add_row('foo')
        assert 'Row input must be list if headers were given' in str(error.value)

def test_collapse_newline():
    x = DapperTable()
    x.add_row('')
    x.add_row('')
    x.add_row('')
    assert x.print() == ''

    x.add_row('foo')
    x.add_row('')
    x.add_row('')
    x.add_row('bar')
    assert x.print() == 'foo\nbar'

    x = DapperTable(collapse_newlines=False)
    x.add_row('')
    x.add_row('')
    assert x.print() == '\n'

    x = DapperTable(pagination_options=PaginationRows(2))
    x.add_row('')
    x.add_row('')
    x.add_row('')
    x.add_row('')
    assert x.print() == ['', '']

def test_edit_row():
    x = DapperTable()
    x.add_row('row 1')
    x.add_row('row 2')
    x.add_row('row 3')
    x.edit_row(1, 'row 2 updated')
    assert x.print() == 'row 1\nrow 2 updated\nrow 3'

    with pytest.raises(DapperTableException) as error:
        x.edit_row(-1, 'foo')
    assert 'Index must be positive number' in str(error.value)

    with pytest.raises(DapperTableException) as error:
        x.edit_row(100, 'foo')
    assert 'Invalid edit index given 100' in str(error.value)

def test_leading_zeros():
    headers = [
        DapperTableHeader('pos', 3, zero_pad_index=True),
        DapperTableHeader('name', 4)
    ]
    x = DapperTable(header_options=DapperTableHeaderOptions(headers))
    for count in range(11):
        x.add_row([count, 'foobar'])

    print(x.print())
    assert '00 ||' in x.print()