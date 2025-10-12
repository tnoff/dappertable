import pytest

from dappertable import shorten_string, format_string_length, string_width
from dappertable import DapperRow, DapperTable, DapperTableHeader, DapperTableHeaderOptions, DapperTableException
from dappertable import PaginationRows, PaginationLength

def test_shorten_string():
    input = 'Some string 123 other text'
    assert shorten_string(input, 5) == 'Som..'
    assert shorten_string(input, 50) == input
    input = '日本語は'
    assert shorten_string(input, 10) == input
    assert shorten_string(input, 7) == '日本..'
    input = 'あいうえおかきくけこさしす 1 other text'
    assert shorten_string(input, 36) == 'あいうえおかきくけこさしす 1 other..'

def test_format_string_length():
    input = 'Some string 123 other text'
    assert format_string_length(input, 20) == 20
    input = '日本語は'
    # 4 CJK chars (W width) -> ceil(4/4) = 1 extra padding
    assert format_string_length(input, 20) == 17
    input = 'あいうえおかきくけこさしす 1 other text'
    assert format_string_length(input, 32) == 32
    input1 = 'Some string すせそなにぬねのまみむめも〜'
    input2 = 'SOME OTHER STRING THAT IS LONG'
    input1_string = shorten_string(input1, 50)
    input2_string = shorten_string(input2, 50)
    input1_length = format_string_length(input1_string, 50)
    input2_length = format_string_length(input2_string, 50)
    new_string = f'||{input1_string:{input1_length}}||\n||{input2_string:{input2_length}}||'
    # input1 has 18 chars, 32 display width, 14 W chars -> ceil(14/4) = 4 extra padding
    assert new_string == '||Some string すせそなにぬねのまみむめも〜              ||\n||SOME OTHER STRING THAT IS LONG                    ||'

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
    x.add_row(['6', 'サンセット・ロード', 'Reiko Takahashi - Topic'])
    x.add_row(['7', '禁断のテレパシー', '工藤静香 -PONY CANYON-'])
    x.add_row(['8', 'BEWITCHED（ARE YOU LEAVING SOON)', '秋本奈緒美 - Topic'])
    result = x.print()
    print(x.print())
    assert result == 'Pos|| Title                                           || Uploader\n'\
                     '-----------------------------------------------------------------\n'\
                     '1  || [HQ] toe - 孤独の発明 ( Kodoku No Hatsumei)       || Hui Hon Man\n'\
                     '2  || "Tremelo + Delay" by Toe                        || Topshelf Records\n'\
                     '3  || "むこう岸が視る夢" by Toe                          || Topshelf Records\n'\
                     '4  || "All I Understand Is That I Don_t Understand" ..|| Topshelf Records\n'\
                     '5  || "C" by Toe                                      || Topshelf Records\n' \
                     '6  || サンセット・ロード                                 || Reiko Takahashi - Topic\n' \
                     '7  || 禁断のテレパシー                                  || 工藤静香 -PONY CANYON-\n' \
                     '8  || BEWITCHED（ARE YOU LEAVING SOON)                || 秋本奈緒美 - Topic'

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

    headers = [
        DapperTableHeader('pos', 3),
        DapperTableHeader('name', 4),
    ]
    x = DapperTable(header_options=DapperTableHeaderOptions(headers))
    x.add_row(['1', 'foo'])
    x.add_row(['2', 'bar'])
    x.edit_row(1, ['2', 'foo2'])
    assert x.print() == 'pos|| name\n----------\n1  || foo\n2  || foo2'

def test_leading_zeros():
    headers = [
        DapperTableHeader('pos', 3, zero_pad_index=True),
        DapperTableHeader('name', 5)
    ]
    x = DapperTable(header_options=DapperTableHeaderOptions(headers))
    for count in range(11):
        x.add_row([count, 'foobar'])

    print(x.print())
    assert '00 ||' in x.print()
    assert '10 ||' in x.print()

def test_cjk_spacing_scenarios():
    # Test with multi-column table with CJK content
    headers = [DapperTableHeader('Title', 10), DapperTableHeader('Extra', 5)]
    table = DapperTable(header_options=DapperTableHeaderOptions(headers))

    table.add_row(['あいうえお', 'test'])  # 5 CJK chars = 10 display width
    result = table.print()

    # Just verify it renders without errors
    assert 'あいうえお' in result
    assert 'test' in result

    headers2 = [DapperTableHeader('Col', 2), DapperTableHeader('Extra', 5)]
    table2 = DapperTable(header_options=DapperTableHeaderOptions(headers2))

    table2.add_row(['あ', 'test'])  # 1 CJK char = 2 display width
    result2 = table2.print()

    # Just verify it renders without errors
    assert 'あ' in result2
    assert 'test' in result2

def test_cjk_no_spacing_needed():
    # Create a scenario where space_count = target_width - len(col_string) <= 0
    headers = [DapperTableHeader('Col', 1)]
    table = DapperTable(header_options=DapperTableHeaderOptions(headers))

    table.add_row(['あ'])  # This will be truncated to 'あ' but still triggers the condition
    result = table.print()

    assert result is not None  # Just verify it doesn't crash

def test_cjk_header_spacing():
    # Test with multi-column table with CJK headers
    headers = [DapperTableHeader('あいうえお', 10), DapperTableHeader('Extra', 5)]
    table = DapperTable(header_options=DapperTableHeaderOptions(headers))
    table.add_row(['test', 'data'])

    result = table.print()
    # Just verify it renders without errors
    assert 'あいうえお' in result
    assert 'test' in result

    # Test header with CJK character
    headers2 = [DapperTableHeader('あ', 2), DapperTableHeader('Extra', 5)]
    table2 = DapperTable(header_options=DapperTableHeaderOptions(headers2))
    table2.add_row(['x', 'data'])

    result2 = table2.print()
    # Just verify it renders without errors
    assert 'あ' in result2
    assert 'x' in result2

def test_last_column_no_unicode_spacing():
    headers = [DapperTableHeader('Col1', 5), DapperTableHeader('LastCol', 10)]
    table = DapperTable(header_options=DapperTableHeaderOptions(headers))

    table.add_row(['test', 'あいうえお'])  # Last column has CJK that exactly fits
    result = table.print()

    lines = result.split('\n')
    for line in lines:
        if 'あいうえお' in line:
            # The line should end with the CJK text, no Unicode spacing after it
            assert line.endswith('あいうえお')
            break

def test_cjk_spacing_multi_column():
    headers = [
        DapperTableHeader('Pos', 3, zero_pad_index=True),
        DapperTableHeader('Wait Time', 9),
        DapperTableHeader('Title', 48),
        DapperTableHeader('Uploader', 32),
    ]
    table = DapperTable(header_options=DapperTableHeaderOptions(headers))
    table.add_row(['1', '4:53', 'Yours', 'Yuki Saito - Topic'])
    table.add_row(['2', '10:59', '禁断のテレパシー', '工藤静香 -PONY CANYON-'])
    table.add_row(['3', '14:46', '雨', 'Kei Ishiguro - Topic'])
    table.add_row(['4', '2:28:12', 'サンセット・ロード', 'Reiko Takahashi - Topic'])
    table.add_row(['5', '2:32:32', 'ファッシネイション', '岡崎舞子 - Topic'])
    table.add_row(['6', '2:36:14', 'Crystal Night', '1986 OMEGA TRIBE - Topic'])

    result = table.print()
    assert result == 'Pos|| Wait Time|| Title                                           || Uploader\n'\
                     '-----------------------------------------------------------------------------\n'\
                     '1  || 4:53     || Yours                                           || Yuki Saito - Topic\n'\
                     '2  || 10:59    || 禁断のテレパシー                                  || 工藤静香 -PONY CANYON-\n'\
                     '3  || 14:46    || 雨                                               || Kei Ishiguro - Topic\n'\
                     '4  || 2:28:12  || サンセット・ロード                                 || Reiko Takahashi - Topic\n'\
                     '5  || 2:32:32  || ファッシネイション                                 || 岡崎舞子 - Topic\n'\
                     '6  || 2:36:14  || Crystal Night                                   || 1986 OMEGA TRIBE - Topic'

def test_wcwidth_fallback(mocker):
    mocker.patch('dappertable.wcswidth', return_value=-1)
    assert string_width('abcd') == 4
    assert string_width('ファッシネイション') == 9

    assert shorten_string('abcd', 10) == 'abcd'
    assert shorten_string('ファッシネイション', 10) == 'ファッシネイション'
    assert shorten_string('ファッシネイション', 5) == 'ファッシネイ..'

def test_get_paginated_rows():
    table = DapperTable()
    table.add_row('foo bar foo')
    assert table.get_paginated_rows() == [DapperRow('foo bar foo', 'foo bar foo')]

def test_print_rows():
    headers = [
        DapperTableHeader('pos', 3, zero_pad_index=True),
        DapperTableHeader('name', 15)
    ]
    x = DapperTable(header_options=DapperTableHeaderOptions(headers), pagination_options=PaginationLength(25))
    for count in range(3):
        x.add_row([count, f'foo{count}'])
    
    row_splits = x.get_paginated_rows()
    assert x.print_rows(row_splits[0]) == 'pos|| name\n----------'
    assert x.print_rows(row_splits[1]) == '0  || foo0\n1  || foo1'
    assert x.print_rows(row_splits[2]) == '2  || foo2'
    row_splits[1][0].edit('')
    assert x.print_rows(row_splits[1]) == '1  || foo1'

def test_dapper_row():
    x = DapperRow('foo', 'foo')
    assert len(x) == 3
    assert x[0] == 'f'
