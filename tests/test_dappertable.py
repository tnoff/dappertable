import pytest

from dappertable import shorten_string, format_string_length, string_width
from dappertable import DapperRow, DapperTable, Column, Columns, DapperTableError
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
        Column('Pos', 3),
        Column('Title', 48),
        Column('Uploader', 32),
    ]
    x = DapperTable(columns=Columns(headers))
    x.add_row(['1', '[HQ] toe - 孤独の発明 ( Kodoku No Hatsumei)', 'Hui Hon Man'])
    x.add_row(['2', '"Tremelo + Delay" by Toe', 'Topshelf Records'])
    x.add_row(['3', '"むこう岸が視る夢" by Toe', 'Topshelf Records'])
    x.add_row(['4', '"All I Understand Is That I Don_t Understand" - Toe', 'Topshelf Records'])
    x.add_row(['5', '"C" by Toe', 'Topshelf Records'])
    x.add_row(['6', 'サンセット・ロード', 'Reiko Takahashi - Topic'])
    x.add_row(['7', '禁断のテレパシー', '工藤静香 -PONY CANYON-'])
    x.add_row(['8', 'BEWITCHED（ARE YOU LEAVING SOON)', '秋本奈緒美 - Topic'])
    result = x.render()
    print(x.render())
    assert result == 'Pos|| Title                                           || Uploader\n'\
                     '-----------------------------------------------------------------\n'\
                     '1  || [HQ] toe - 孤独の発明 ( Kodoku No Hatsumei)       || Hui Hon Man\n'\
                     '2  || "Tremelo + Delay" by Toe                        || Topshelf Records\n'\
                     '3  || "むこう岸が視る夢" by Toe                         || Topshelf Records\n'\
                     '4  || "All I Understand Is That I Don_t Understand" ..|| Topshelf Records\n'\
                     '5  || "C" by Toe                                      || Topshelf Records\n' \
                     '6  || サンセット・ロード                                 || Reiko Takahashi - Topic\n' \
                     '7  || 禁断のテレパシー                                  || 工藤静香 -PONY CANYON-\n' \
                     '8  || BEWITCHED（ARE YOU LEAVING SOON)                || 秋本奈緒美 - Topic'

def test_dapper_table_rows():
    headers = [
        Column('pos', 3),
        Column('name', 4),
    ]
    x = DapperTable(columns=Columns(headers), pagination_options=PaginationRows(2))
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    result = x.render()
    assert result == ['pos|| name\n----------', '1  || a\n2  || b', '3  || c']

def test_dapper_table_length():
    headers = [
        Column('pos', 3),
        Column('name', 4),
    ]
    x = DapperTable(columns=Columns(headers), pagination_options=PaginationRows(2))
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
    assert x.render() == ['1234\n1234', '1234']

    x = DapperTable(pagination_options=PaginationLength(10))
    x.add_row('123456789')
    x.add_row('123456789')
    x.add_row('123456789')
    assert x.render() == ['123456789', '123456789', '123456789']

    x = DapperTable(pagination_options=PaginationLength(10))
    x.add_row('1234')
    x.add_row('1234')
    x.add_row('1234')
    x.add_row('123456789')
    assert x.render() == ['1234\n1234', '1234', '123456789']


def test_dapper_table_split_length_invalid_input():
    x = DapperTable(pagination_options=PaginationLength(10))
    x.add_row('1234789012345')
    with pytest.raises(DapperTableError) as error:
        x.render()
    assert 'Length of input "1234789012345" is greater than max length 10' in str(error.value)
    with pytest.raises(DapperTableError) as error:
        DapperTable(pagination_options=PaginationLength(-5))
    assert 'Invalid value for length per message: -5' in str(error.value)

def test_dapper_table_no_headers_no_rows():
    with pytest.raises(DapperTableError) as error:
        DapperTable(columns=Columns([]))
    assert 'Must have at least one header' in str(error.value)
    with pytest.raises(DapperTableError) as invalid_error:
        DapperTable(columns=Columns(Column('name', 5)), pagination_options=PaginationRows(-1))
    assert 'Invalid value for rows per message: -1' in str(invalid_error.value)
    with pytest.raises(DapperTableError) as invalid_row:
        Columns('foo')
    assert 'Header must be Column object' in str(invalid_row.value)

def test_add_invalid_row():
    headers = [
        Column('pos', 3),
        Column('name', 4),
    ]
    x = DapperTable(columns=Columns(headers), pagination_options=PaginationRows(2))
    with pytest.raises(DapperTableError) as error:
        x.add_row(['foo'])
        assert 'Row length must match length of headers' in str(error.value)

def test_delete_row():
    headers = [
        Column('pos', 3),
        Column('name', 4)
    ]
    x = DapperTable(columns=Columns(headers), pagination_options=PaginationRows(2))
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    x.remove_row(1)
    result = x.size
    assert result == 2
    result = x.render()
    assert result == ['pos|| name\n----------', '1  || a\n3  || c']
    with pytest.raises(DapperTableError) as error:
        x.remove_row(99)
        assert 'Invalid deletion index' in str(error.value)

def test_separator_override():
    headers = [
        Column('pos', 3),
        Column('name', 4)
    ]
    x = DapperTable(columns=Columns(headers, separator='+'), pagination_options=PaginationRows(2))
    x.add_row(['1', 'a'])
    x.add_row(['2', 'b'])
    x.add_row(['3', 'c'])
    x.remove_row(1)
    result = x.size
    assert result == 2
    result = x.render()
    assert result == ['pos+ name\n---------', '1  + a\n3  + c']

def test_no_headers_basic():
    x = DapperTable()
    x.add_row('foo bar stuff')
    x.add_row('more stuff here')
    assert x.size == 2
    result = x.render()
    assert result == 'foo bar stuff\nmore stuff here'
    x.remove_row(0)
    assert x.render() == 'more stuff here'

def test_no_headers_with_messages_per_set():
    x = DapperTable(pagination_options=PaginationRows(2))
    x.add_row('foo bar stuff')
    x.add_row('more stuff here')
    x.add_row('another row just for fun')
    assert x.size == 3
    result = x.render()
    assert result == ['foo bar stuff\nmore stuff here', 'another row just for fun']

def test_invalid_row_add():
    x = DapperTable(Columns([Column('pos', 3), Column('name', 5)]))
    with pytest.raises(DapperTableError) as error:
        x.add_row('foo')
        assert 'Row input must be list if headers were given' in str(error.value)

def test_collapse_newline():
    x = DapperTable()
    x.add_row('')
    x.add_row('')
    x.add_row('')
    assert x.render() == ''

    x.add_row('foo')
    x.add_row('')
    x.add_row('')
    x.add_row('bar')
    assert x.render() == 'foo\nbar'

    x = DapperTable(collapse_newlines=False)
    x.add_row('')
    x.add_row('')
    assert x.render() == '\n'

    x = DapperTable(pagination_options=PaginationRows(2))
    x.add_row('')
    x.add_row('')
    x.add_row('')
    x.add_row('')
    assert x.render() == ['', '']

def test_edit_row():
    x = DapperTable()
    x.add_row('row 1')
    x.add_row('row 2')
    x.add_row('row 3')
    x.edit_row(1, 'row 2 updated')
    assert x.render() == 'row 1\nrow 2 updated\nrow 3'

    with pytest.raises(DapperTableError) as error:
        x.edit_row(-1, 'foo')
    assert 'Index must be positive number' in str(error.value)

    with pytest.raises(DapperTableError) as error:
        x.edit_row(100, 'foo')
    assert 'Invalid edit index given 100' in str(error.value)

    headers = [
        Column('pos', 3),
        Column('name', 4),
    ]
    x = DapperTable(columns=Columns(headers))
    x.add_row(['1', 'foo'])
    x.add_row(['2', 'bar'])
    x.edit_row(1, ['2', 'foo2'])
    assert x.render() == 'pos|| name\n----------\n1  || foo\n2  || foo2'

def test_leading_zeros():
    headers = [
        Column('pos', 3, zero_pad=True),
        Column('name', 5)
    ]
    x = DapperTable(columns=Columns(headers))
    for count in range(11):
        x.add_row([count, 'foobar'])

    print(x.render())
    assert '00 ||' in x.render()
    assert '10 ||' in x.render()

def test_cjk_spacing_scenarios():
    # Test with multi-column table with CJK content
    headers = [Column('Title', 10), Column('Extra', 5)]
    table = DapperTable(columns=Columns(headers))

    table.add_row(['あいうえお', 'test'])  # 5 CJK chars = 10 display width
    result = table.render()

    # Just verify it renders without errors
    assert 'あいうえお' in result
    assert 'test' in result

    headers2 = [Column('Col', 2), Column('Extra', 5)]
    table2 = DapperTable(columns=Columns(headers2))

    table2.add_row(['あ', 'test'])  # 1 CJK char = 2 display width
    result2 = table2.render()

    # Just verify it renders without errors
    assert 'あ' in result2
    assert 'test' in result2

def test_cjk_no_spacing_needed():
    # Create a scenario where space_count = target_width - len(col_string) <= 0
    headers = [Column('Col', 1)]
    table = DapperTable(columns=Columns(headers))

    table.add_row(['あ'])  # This will be truncated to 'あ' but still triggers the condition
    result = table.render()

    assert result is not None  # Just verify it doesn't crash

def test_cjk_header_spacing():
    # Test with multi-column table with CJK headers
    headers = [Column('あいうえお', 10), Column('Extra', 5)]
    table = DapperTable(columns=Columns(headers))
    table.add_row(['test', 'data'])

    result = table.render()
    # Just verify it renders without errors
    assert 'あいうえお' in result
    assert 'test' in result

    # Test header with CJK character
    headers2 = [Column('あ', 2), Column('Extra', 5)]
    table2 = DapperTable(columns=Columns(headers2))
    table2.add_row(['x', 'data'])

    result2 = table2.render()
    # Just verify it renders without errors
    assert 'あ' in result2
    assert 'x' in result2

def test_last_column_no_unicode_spacing():
    headers = [Column('Col1', 5), Column('LastCol', 10)]
    table = DapperTable(columns=Columns(headers))

    table.add_row(['test', 'あいうえお'])  # Last column has CJK that exactly fits
    result = table.render()

    lines = result.split('\n')
    for line in lines:
        if 'あいうえお' in line:
            # The line should end with the CJK text, no Unicode spacing after it
            assert line.endswith('あいうえお')
            break

def test_cjk_spacing_multi_column():
    headers = [
        Column('Pos', 3, zero_pad=True),
        Column('Wait Time', 9),
        Column('Title', 48),
        Column('Uploader', 32),
    ]
    table = DapperTable(columns=Columns(headers))
    table.add_row(['1', '4:53', 'Yours', 'Yuki Saito - Topic'])
    table.add_row(['2', '10:59', '禁断のテレパシー', '工藤静香 -PONY CANYON-'])
    table.add_row(['3', '14:46', '雨', 'Kei Ishiguro - Topic'])
    table.add_row(['4', '2:28:12', 'サンセット・ロード', 'Reiko Takahashi - Topic'])
    table.add_row(['5', '2:32:32', 'ファッシネイション', '岡崎舞子 - Topic'])
    table.add_row(['6', '2:36:14', 'Crystal Night', '1986 OMEGA TRIBE - Topic'])

    result = table.render()
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

def test_get_pages():
    table = DapperTable()
    table.add_row('foo bar foo')
    assert table.get_pages() == [DapperRow('foo bar foo', 'foo bar foo')]

def test_format_page():
    headers = [
        Column('pos', 3, zero_pad=True),
        Column('name', 15)
    ]
    x = DapperTable(columns=Columns(headers), pagination_options=PaginationLength(25))
    for count in range(3):
        x.add_row([count, f'foo{count}'])

    pages = x.get_pages()
    assert x.format_page(pages[0]) == 'pos|| name\n----------'
    assert x.format_page(pages[1]) == '0  || foo0\n1  || foo1'
    assert x.format_page(pages[2]) == '2  || foo2'
    pages[1][0].edit('')
    assert x.format_page(pages[1]) == '1  || foo1'

def test_dapper_row():
    x = DapperRow('foo', 'foo')
    assert len(x) == 3
    assert x[0] == 'f'

def test_prefix_suffix_no_pagination():
    """Test prefix/suffix with no pagination"""
    x = DapperTable(prefix='START:', suffix=':END')
    x.add_row('foo')
    x.add_row('bar')
    result = x.render()
    assert result == 'START:foo\nbar:END'

def test_prefix_suffix_with_length_pagination():
    """Test prefix/suffix with length-based pagination - multiple pages"""
    x = DapperTable(pagination_options=PaginationLength(10), prefix='[', suffix=']')
    x.add_row('1234')  # 4 chars
    x.add_row('1234')  # 4 chars
    x.add_row('1234')  # 4 chars
    result = x.render()
    # First chunk: '[' (1) + '1234\n1234' (9) = 10 total
    # Second chunk: '1234' (4) + ']' (1) = 5 total
    assert result == ['[1234\n1234', '1234]']

def test_prefix_suffix_with_rows_pagination():
    """Test prefix/suffix with rows-based pagination"""
    x = DapperTable(pagination_options=PaginationRows(2), prefix='>>>', suffix='<<<')
    x.add_row('foo')
    x.add_row('bar')
    x.add_row('baz')
    result = x.render()
    assert result == ['>>>foo\nbar', 'baz<<<']

def test_prefix_exceeds_length():
    """Test error when prefix alone exceeds pagination length"""
    with pytest.raises(DapperTableError) as error:
        DapperTable(pagination_options=PaginationLength(5), prefix='TOOLONG')
    assert 'Prefix length (7) exceeds pagination length (5)' in str(error.value)

def test_suffix_exceeds_length():
    """Test error when suffix alone exceeds pagination length"""
    with pytest.raises(DapperTableError) as error:
        DapperTable(pagination_options=PaginationLength(5), suffix='TOOLONG')
    assert 'Suffix length (7) exceeds pagination length (5)' in str(error.value)

def test_prefix_only():
    """Test with only prefix, no suffix"""
    x = DapperTable(pagination_options=PaginationLength(10), prefix='> ')
    x.add_row('test1')
    x.add_row('test2')
    result = x.render()
    assert result[0].startswith('> ')
    assert not result[-1].endswith('> ')

def test_suffix_only():
    """Test with only suffix, no prefix"""
    x = DapperTable(pagination_options=PaginationLength(10), suffix=' <')
    x.add_row('test1')
    x.add_row('test2')
    result = x.render()
    assert result[-1].endswith(' <')
    assert not result[0].startswith(' <')

def test_prefix_suffix_with_cjk():
    """Test CJK characters in prefix/suffix are handled correctly"""
    x = DapperTable(pagination_options=PaginationLength(20), prefix='日本:', suffix=':語')
    x.add_row('test1')
    x.add_row('test2')
    result = x.render()
    # First page should have prefix
    assert result[0].startswith('日本:')
    # Last page should have suffix
    assert result[-1].endswith(':語')

def test_prefix_suffix_single_page():
    """Test prefix/suffix when table fits in single page"""
    x = DapperTable(pagination_options=PaginationLength(50), prefix='START\n', suffix='\nEND')
    x.add_row('row1')
    x.add_row('row2')
    result = x.render()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == 'START\nrow1\nrow2\nEND'

def test_prefix_suffix_row_too_long_with_suffix():
    """Test that suffix gets its own page when row doesn't fit with it"""
    x = DapperTable(pagination_options=PaginationLength(10), suffix='SUFFIX')
    x.add_row('12345678')  # 8 chars, doesn't fit with 6 char suffix
    result = x.render()
    # Should create two pages: one with the row, one with just the suffix
    assert len(result) == 2
    assert result[0] == '12345678'
    assert result[1] == 'SUFFIX'

def test_prefix_row_too_long_with_prefix():
    """Test that prefix gets its own page when row doesn't fit with it"""
    x = DapperTable(pagination_options=PaginationLength(10), prefix='PREFIX')
    x.add_row('12345678')  # 8 chars, doesn't fit with 6 char prefix
    result = x.render()
    # Should create two pages: one with just the prefix, one with the row
    assert len(result) == 2
    assert result[0] == 'PREFIX'
    assert result[1] == '12345678'

def test_suffix_with_multiple_rows_requiring_move():
    """Test that rows are moved when multiple rows don't fit with suffix"""
    x = DapperTable(pagination_options=PaginationLength(20), suffix='SUFFIX')
    # Add rows that fit in one chunk without suffix but not with it
    # Each row is 5 chars, with newlines: 5 + 1 + 5 + 1 + 5 = 17 chars
    # With SUFFIX (6 chars), total would be 23, exceeding limit of 20
    x.add_row('row11')
    x.add_row('row22')
    x.add_row('row33')
    result = x.render()
    # Should move rows to accommodate suffix
    assert len(result) == 2
    # First page should have some rows
    assert 'row11' in result[0]
    # Last page should have suffix
    assert result[1].endswith('SUFFIX')

def test_enclosure_no_pagination():
    """Test enclosure with no pagination"""
    x = DapperTable(enclosure_start='```\n', enclosure_end='\n```')
    x.add_row('line 1')
    x.add_row('line 2')
    result = x.render()
    assert result == '```\nline 1\nline 2\n```'

def test_enclosure_with_length_pagination():
    """Test enclosure wraps each page and accounts for enclosure length in pagination"""
    x = DapperTable(pagination_options=PaginationLength(20), enclosure_start='```\n', enclosure_end='\n```')
    # Each enclosure adds 8 chars (4 for start, 4 for end)
    # Available space per chunk: 20 - 8 = 12 chars
    x.add_row('12345')  # 5 chars
    x.add_row('67890')  # 5 chars (total 11 with newline)
    x.add_row('abcde')  # 5 chars (would be 17 with newline, exceeds 12)
    result = x.render()
    assert len(result) == 2
    assert result[0] == '```\n12345\n67890\n```'
    assert result[1] == '```\nabcde\n```'

def test_enclosure_with_prefix_suffix():
    """Test correct ordering: prefix, enclosure_start, content, enclosure_end, suffix"""
    x = DapperTable(pagination_options=PaginationLength(50),
                   prefix='**Report:**\n',
                   suffix='\n*End*',
                   enclosure_start='```\n',
                   enclosure_end='\n```')
    x.add_row('data')
    result = x.render()
    assert len(result) == 1
    assert result[0] == '**Report:**\n```\ndata\n```\n*End*'

def test_enclosure_markdown_example():
    """Real-world example with markdown code blocks"""

    headers = [
        Column('Name', 10),
        Column('Value', 5)
    ]
    x = DapperTable(columns=Columns(headers),
                   pagination_options=PaginationLength(100),
                   prefix='**Data:**\n',
                   enclosure_start='```\n',
                   enclosure_end='\n```')
    x.add_row(['Item 1', '123'])
    x.add_row(['Item 2', '456'])
    result = x.render()
    assert len(result) == 1
    assert result[0].startswith('**Data:**\n```\n')
    assert result[0].endswith('\n```')
    assert 'Item 1' in result[0]

def test_enclosure_start_only():
    """Test with only opening enclosure"""
    x = DapperTable(enclosure_start='>>> ')
    x.add_row('test')
    result = x.render()
    assert result == '>>> test'

def test_enclosure_end_only():
    """Test with only closing enclosure"""
    x = DapperTable(enclosure_end=' <<<')
    x.add_row('test')
    result = x.render()
    assert result == 'test <<<'

def test_enclosure_all_features():
    """Test with prefix, suffix, enclosure, and pagination all together"""
    x = DapperTable(pagination_options=PaginationLength(25),
                   prefix='[',
                   suffix=']',
                   enclosure_start='<',
                   enclosure_end='>')
    # Available space: 25 - 2 (enclosure) = 23
    # First chunk: 23 - 1 (prefix) = 22
    x.add_row('12345678901234567890')  # 20 chars
    x.add_row('abc')  # 3 chars
    result = x.render()
    assert len(result) == 2
    assert result[0] == '[<12345678901234567890>'
    assert result[1] == '<abc>]'

def test_enclosure_large_overhead():
    """Test when enclosure overhead is large but leaves some space"""
    x = DapperTable(pagination_options=PaginationLength(25),
                   enclosure_start='LONG_START_',
                   enclosure_end='_LONG_END')
    # Enclosure overhead: 11 + 9 = 20, leaves 5 chars for content
    x.add_row('xyz')  # 3 chars, fits
    result = x.render()
    assert len(result) == 1
    assert result[0] == 'LONG_START_xyz_LONG_END'

def test_len():
    x = DapperTable()
    x.add_row('foo')
    x.add_row('bar')
    assert len(x) == 2
