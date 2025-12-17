'''
Taken from https://medium.com/@gullevek/python-output-formatting-double-byte-characters-6d6d18d04be3
Use these functions to get proper length of strings for formatting with wide characters
'''
from dataclasses import dataclass, field
from enum import Enum
from math import ceil
from re import sub
from typing import List
from unicodedata import east_asian_width
from wcwidth import wcswidth

class DapperTableException(Exception):
    '''
    Generic exception class
    '''

@dataclass
class DapperTableHeader:
    '''
    Basic header type
    '''
    name: str
    length: int
    zero_pad_index: bool = False

@dataclass
class DapperTableHeaderOptions:
    '''
    Combined Header Options
    '''
    headers: List[DapperTableHeader] | DapperTableHeader
    separator: str = '||'

    def __post_init__(self):
        if isinstance(self.headers, DapperTableHeader):
            self.headers = [self.headers]
        if not self.headers:
            raise DapperTableException('Must have at least one header')
        for header in self.headers:
            if not isinstance(header, DapperTableHeader):
                raise DapperTableException('Header must be DapperTableHeader object')


class PaginationOptions(Enum):
    '''
    Default pagination options
    '''
    ROWS = 'rows'
    LENGTH = 'length'

@dataclass
class PaginationSetting:
    '''
    Pagination settings
    '''
    pagination_type: PaginationOptions

@dataclass
class PaginationRows(PaginationSetting):
    '''
    Pagination By Rows
    '''
    rows_per_message: int
    pagination_type: PaginationOptions = field(default=PaginationOptions.ROWS, init=False)

@dataclass
class PaginationLength(PaginationSetting):
    '''
    Pagination By Length
    '''
    length_per_message: int
    pagination_type: PaginationOptions = field(default=PaginationOptions.LENGTH, init=False)


@dataclass
class DapperRow:
    '''
    Instance of a row in a table
    '''
    content: str
    input_values: List[str] | str
    zero_padding_value: int | None = None

    def edit(self, new_content: str) -> bool:
        '''
        Allow raw editing of row content
        '''
        self.content = new_content
        self.input_values = new_content
        return True

    def __eq__(self, other):
        '''
        Override equals check
        '''
        return other.content == self.content

    def __len__(self):
        '''
        Override length check
        '''
        return len(self.content)

    def __getitem__(self, index: int):
        '''
        Override get item
        '''
        return self.content[index]

def shorten_string(intput_string: str, width: int, placeholder: str = '..') -> str:
    '''
    Shorten a string with wide characters (e.g. East Asian characters)

    intput_string (string): input string to shorten
    width (int): character count to shorten too
    placeholder (str, optional): cut of end characters if space is there. Defaults to '..'.
    '''
    # get the display width using wcwidth
    string_display_width = string_width(str(intput_string))
    # if display width is too big
    if string_display_width > width:
        # set current length and output string
        out_string = ''
        # loop through each character
        for char in str(intput_string):
            # Calculate what the width would be if we add this character
            new_string = out_string + char
            new_string_width = wcswidth(new_string)
            # Handle non-printable characters - fall back to basic length
            if new_string_width == -1:
                new_string_width = len(new_string)

            # if the new length is smaller than the output length to shorten too add the char
            if new_string_width <= (width - wcswidth(placeholder)):
                out_string += char
            else:
                break
        # return string with new width and placeholder
        return f"{out_string}{placeholder}"
    return str(intput_string)

def string_width(input_string: str) -> int:
    '''
    Get display width of a string (accounts for wide characters)

    string (string): string to get display width for
    '''
    # Use wcwidth library for accurate display width calculation
    width = wcswidth(input_string)
    # wcswidth returns -1 if string contains non-printable characters
    # Fall back to basic string length in that case
    if width == -1:
        return len(input_string)
    return width

def format_string_length(input_string: str, length: int) -> int:
    '''
    Returns length updated for string with wide characters
    Calculate the padding width needed to achieve the desired display width
    when using Python's string formatting with wide characters (e.g. East Asian)

    input_string (string): string to calculate length of
    length (int): desired display width for string
    '''
    display_width = string_width(input_string)
    char_count = len(input_string)

    # For proper separator alignment, we need consistent format widths
    # When the display width meets or exceeds target, we use the target length
    # to ensure all separators align at the same character position
    if display_width >= length:
        return length

    # For strings shorter than target, calculate the needed padding
    # Count actual wide East Asian characters (excluding fullwidth ASCII like ＂)
    # to determine adjustment needed for terminals that don't render wide chars correctly
    needed_padding = length - display_width

    # Count only true wide characters (W width), not fullwidth ASCII variants (F width)
    true_wide_count = sum(1 for c in input_string if east_asian_width(c) == 'W')
    adjusted_padding = needed_padding + (ceil(true_wide_count / 4))

    return char_count + adjusted_padding


# https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
def chunk_list(input_list: List[object], chunk_size: int) -> List[List[object]]:
    '''
    Split list into equal sized chunks

    input_list: Input list of any type
    chunk_size: Chunk list into size bits
    '''
    size = max(1, chunk_size)
    return [input_list[i:i+size] for i in range(0, len(input_list), size)]

def chunk_list_by_length(input_list: List[DapperRow], max_length: int) -> List[List[str]]:
    '''
    Split list by length
    '''
    new_rows = []
    current_size = 0
    current_rows = []

    for current_item in input_list:
        if string_width(current_item.content) > max_length:
            raise DapperTableException(f'Length of input "{current_item.content}" is greater than iteration max length {max_length}')
        if string_width(current_item.content) + current_size > max_length:
            new_rows.append(current_rows)
            current_rows = []
            current_size = 0
        current_rows.append(current_item)
        current_size += string_width(current_item.content)
    new_rows.append(current_rows)
    return new_rows

class DapperTable():
    '''
    Split large inputs into smaller messages, also supports formatting
    '''
    def __init__(self, header_options : DapperTableHeaderOptions = None,
                 pagination_options: PaginationSetting = None, collapse_newlines: bool = True):
        '''
        Init a dapper table

        headerOptions       :   DapperTable header options, if not given will treat as raw input
        collapse_newlines   :   Collapse multiple newlines in messages
        '''
        self.collapse_newlines = collapse_newlines
        self._rows = []
        self._header_rows = []

        self._rows_per_message = None
        self._length_per_message = None
        if pagination_options:
            if pagination_options.pagination_type == PaginationOptions.ROWS:
                self._rows_per_message = pagination_options.rows_per_message
                if pagination_options.rows_per_message and pagination_options.rows_per_message < 1:
                    raise DapperTableException(f'Invalid value for rows per message: {pagination_options.rows_per_message}')
            if pagination_options.pagination_type == PaginationOptions.LENGTH:
                self._length_per_message = pagination_options.length_per_message
                if pagination_options.length_per_message < 1:
                    raise DapperTableException(f'Invalid value for length per message: {pagination_options.length_per_message}')

        # Headers
        self._headers = None
        self._separator = None
        # Track pad indexing
        self._contains_zero_pad_index = False

        if header_options:
            self._headers = header_options.headers
            for header in self._headers:
                if header.zero_pad_index:
                    self._contains_zero_pad_index = True
                    break
            # Make sure we add a single space at the end
            self._separator = f'{header_options.separator.replace(" ", "")} '
            # Init first headers
            self._header_rows = self._generate_headers()

    def _generate_formatted_string(self, target_width: int, col_string: str, is_last_column: bool = False) -> str:
        '''
        Generate a properly formatted string with appropriate spacing for CJK characters.
        '''
        if string_width(col_string) < target_width:
            col_length = format_string_length(col_string, target_width)
            return f'{col_string:{col_length}}'
        # If last column, don't add spacing to save space
        if is_last_column:
            return col_string

        # Use one regular space plus thin spaces for better readability
        space_count = target_width - len(col_string)
        return col_string + ' ' * space_count

    def _generate_headers(self) -> List[str]:
        '''
        Generate header content, first two rows of table
        '''
        col_items = []
        # Setup headers as first row
        for i, col in enumerate(self._headers):
            col_string = shorten_string(col.name, col.length)
            is_last_column = i == len(self._headers) - 1
            formatted_col = self._generate_formatted_string(col.length, col_string, is_last_column)
            col_items.append(formatted_col)
        row_string = self._separator.join(i for i in col_items)
        row_string = row_string.rstrip(' ')
        # Calculate total length based on actual display width
        total_length = string_width(row_string)
        # First row and then table formatter
        return [DapperRow(row_string, None), DapperRow('-' * total_length, None)]

    def _validate_row(self, row: List[str] | str) -> bool:
        '''
        Validate row input
        '''
        if self._headers:
            if not isinstance(row, list):
                raise DapperTableException('Row input must be list if headers were given')
            if len(row) != len(self._headers):
                raise DapperTableException('Row length must match length of headers')
        return True


    def _check_padding_zeros(self, new_value: str) -> int:
        '''
        Check how many padded zeros should be added
        '''
        return len(str(len(self._rows))) - len(str(new_value))

    def _format_row(self, row: List[str]) -> DapperRow:
        '''
        Format row content to headers
        '''
        padding = None
        col_items = []
        for (count, item) in enumerate(row):
            if self._headers[count].zero_pad_index:
                padding = self._check_padding_zeros(item)
                item = f'{"0" * padding}{item}'
            col_string = shorten_string(item, self._headers[count].length)
            is_last_column = count == len(self._headers) - 1
            formatted_col = self._generate_formatted_string(self._headers[count].length, col_string, is_last_column)
            col_items.append(formatted_col)
        row_string = self._separator.join(i for i in col_items)
        row_string = row_string.rstrip(' ')
        return DapperRow(row_string, row, zero_padding_value=padding)

    def __reset_zero_pad_index(self, current_index: int) -> bool:
        '''
        Reset zero pad index on previous rows
        '''
        if not self._contains_zero_pad_index:
            return False
        # Format previous rolls to make sure leading prefixes is set
        padding_check = None
        for idx in range(current_index - 1, -1, -1):
            row = self._rows[idx]
            if padding_check is None:
                for (count, item) in enumerate(row.input_values):
                    # If the padding is already fine, lets just return
                    if self._headers[count].zero_pad_index:
                        padding = self._check_padding_zeros(item)
                        if padding == row.zero_padding_value:
                            return True
                        # Else lets keep going
                        padding_check = False
                        break
            self._rows[idx] = self._format_row(row.input_values)
        return True

    def add_row(self, row: List[str] | str) -> int:
        '''
        Add row to table

        row     :   List of items to go in row, assumes each item list is string representation

        returns: index of new data added
        '''
        # If headers, add extra checks, else just accept input
        self._validate_row(row)
        row_data = DapperRow(row, row)
        if self._headers:
            row_data = self._format_row(row)
        self._rows.append(row_data)
        self.__reset_zero_pad_index(len(self._rows) - 1)
        return len(self._rows) - 1

    def edit_row(self, index: int, row: List[str] | str) -> bool:
        '''
        Edit row contents
        
        index   :   Index of row to update
        row     :   List of items to go in row, assumes each item list is string representation
        '''
        if index < 0:
            raise DapperTableException('Index must be positive number')
        try:
            _current_value = self._rows[int(index)]
        except IndexError as exc:
            raise DapperTableException(f'Invalid edit index given {index}') from exc
        self._validate_row(row)
        row_data = DapperRow(row, row)
        if self._headers:
            row_data = self._format_row(row)
        self._rows[int(index)] = row_data
        return True

    def remove_row(self, index: int) -> bool:
        '''
        Remove row from table

        index   :   Index of row, cannot remove headers
        '''
        try:
            del self._rows[index]
        except IndexError as exc:
            raise DapperTableException('Invalid deletion index') from exc
        return True

    def get_paginated_rows(self) -> List[DapperRow]:
        '''
        Return list of rows based on pagination options
        '''
        # If no pagination options, return raw list
        all_rows = self._header_rows + self._rows
        if not (self._rows_per_message or self._length_per_message):
            return all_rows
        if self._rows_per_message:
            return chunk_list(all_rows, self._rows_per_message)
        # Assume length per message
        return chunk_list_by_length(all_rows, self._length_per_message)

    def print_rows(self, row_list: List[DapperRow]) -> str:
        '''
        If set, remove double newlines and clean up output
        '''
        combined = '\n'.join(i.content for i in row_list)
        if not self.collapse_newlines:
            return combined
        combined = sub(r'\n{2,}', '\n', combined)
        combined = combined.strip('\n')
        return combined

    def print(self) -> List[str] | str:
        '''
        Print table
        '''
        # If no pagination options given
        if not (self._rows_per_message or self._length_per_message):
            return self.print_rows(self._header_rows + self._rows)
        split_rows = self.get_paginated_rows()
        split_output = []
        for sr in split_rows:
            split_output.append(self.print_rows(sr))
        return split_output


    @property
    def size(self) -> int:
        '''
        Return size of table (does not include headers)
        '''
        return len(self._rows)
