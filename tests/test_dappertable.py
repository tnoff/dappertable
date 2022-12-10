from dappertable import shorten_string_cjk, format_string_length
from dappertable import DapperTable

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
        {
            'name': 'Pos',
            'length': 3,
        },
        {
            'name': 'Title',
            'length': 24,
        }
    ]
    x = DapperTable(headers)
    x.add_row(['1', 'foo1234'])
    x.add_row(['2', 'すせそなにぬねのまみむめも〜'])
    result = x.print()
    assert result == 'Pos || Title                   \n1   || foo1234                 \n2   || すせそなにぬねのまみむ..'
    x.add_row(['3', '日本語は'])
    x.rows_per_message = 2
    results = x.print()
    assert results[0] == 'Pos || Title                   \n1   || foo1234                 \n2   || すせそなにぬねのまみむ..'
    assert results[1] == '3   || 日本語は                '