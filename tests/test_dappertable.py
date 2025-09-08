import pytest

from dappertable import shorten_string_cjk, format_string_length
from dappertable import DapperTable, DapperTableHeader, DapperTableException

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
    x = DapperTable(headers)
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
    x = DapperTable(headers, rows_per_message=2)
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    result = x.print()
    assert result == ['pos|| name\n----------\n1  || a\n2  || b', '3  || c']

def test_dapper_table_length():
    headers = [
        DapperTableHeader('pos', 3),
        DapperTableHeader('name', 4),
    ]
    x = DapperTable(headers, rows_per_message=2)
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    result = x.size()
    assert result == 3

def test_dapper_table_no_headers_no_rows():
    with pytest.raises(DapperTableException) as error:
        DapperTable([])
        assert 'Must have at least one header' in str(error.value)
    with pytest.raises(DapperTableException) as invalid_error:
        DapperTable([1,2], rows_per_message=-1)
        assert 'Invalid value for rows per message' in str(invalid_error.value)
    with pytest.raises(DapperTableException) as invalid_row:
        DapperTable([{'foo': 'bar'}])
        assert 'Header must be DapperTableHeader object' in str(invalid_row.value)

def test_add_invalid_row():
    headers = [
        DapperTableHeader('pos', 3),
        DapperTableHeader('name', 4),
    ]
    x = DapperTable(headers, rows_per_message=2)
    with pytest.raises(DapperTableException) as error:
        x.add_row(['foo'])
        assert 'Row length must match length of headers' in str(error.value)

def test_delete_row():
    headers = [
        DapperTableHeader('pos', 3),
        DapperTableHeader('name', 4)
    ]
    x = DapperTable(headers, rows_per_message=2)
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    x.remove_row(1)
    result = x.size()
    assert result == 2
    result = x.print()
    assert result == ['pos|| name\n----------\n1  || a\n3  || c']
    with pytest.raises(DapperTableException) as error:
        x.remove_row(99)
        assert 'Invalid deletion index' in str(error.value)

def test_separator_override():
    headers = [
        DapperTableHeader('pos', 3),
        DapperTableHeader('name', 4)
    ]
    x = DapperTable(headers, rows_per_message=2, separator='+')
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    x.remove_row(1)
    result = x.size()
    assert result == 2
    result = x.print()
    assert result == ['pos+ name\n---------\n1  + a\n3  + c']
