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
            'length': 48,
        },
        {
            'name': 'Uploader',
            'length': 32,
        }
    ]
    x = DapperTable(headers)
    x.add_row(['1', '[HQ] toe - 孤独の発明 ( Kodoku No Hatsumei)', 'Hui Hon Man'])
    x.add_row(['2', '"Tremelo + Delay" by Toe', 'Topshelf Records'])
    x.add_row(['3', '"むこう岸が視る夢" by Toe', 'Topshelf Records'])
    x.add_row(['4', '"All I Understand Is That I Don_t Understand" - Toe', 'Topshelf Records'])
    x.add_row(['5', '"C" by Toe', 'Topshelf Records'])
    result = x.print()
    assert result == 'Pos|| Title                                           || Uploader\n'\
                     '1  || [HQ] toe - 孤独の発明 ( Kodoku No Hatsumei)     || Hui Hon Man\n'\
                     '2  || "Tremelo + Delay" by Toe                        || Topshelf Records\n'\
                     '3  || "むこう岸が視る夢" by Toe                     || Topshelf Records\n'\
                     '4  || "All I Understand Is That I Don_t Understand" ..|| Topshelf Records\n'\
                     '5  || "C" by Toe                                      || Topshelf Records'


def test_dapper_table_rows():
    headers = [
        {
            'name': 'pos',
            'length': 3,
        },
        {
            'name': 'name',
            'length': 4,
        }
    ]
    x = DapperTable(headers, rows_per_message=2)
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    result = x.print()
    assert result == ['pos|| name\n1  || a\n2  || b', '3  || c']