'''
Taken from https://medium.com/@gullevek/python-output-formatting-double-byte-characters-6d6d18d04be3
Use these functions to get proper length of strings for formatting with wide characters
'''
from enum import Enum
from math import ceil
from re import sub
from typing import List
from unicodedata import east_asian_width
from wcwidth import wcswidth

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
def chunk_list(input_list: List[str], size: int) -> List[List[str]]:
    '''
    Split list into equal sized chunks
    '''
    size = max(1, size)
    return [input_list[i:i+size] for i in range(0, len(input_list), size)]

def chunk_list_by_length(input_list: List[str], max_length: int) -> List[List[str]]:
    '''
    Split list by length
    '''
    new_rows = []
    current_size = 0
    current_rows = []

    for current_item in input_list:
        if string_width(current_item) > max_length:
            raise DapperTableException(f'Length of input "{current_item}" is greater than iteration max length {max_length}')
        if string_width(current_item) + current_size > max_length:
            new_rows.append(current_rows)
            current_rows = []
            current_size = 0
        current_rows.append(current_item)
        current_size += string_width(current_item)
    new_rows.append(current_rows)
    return new_rows

class DapperTableException(Exception):
    '''
    Generic exception class
    '''

class DapperTableHeader():
    '''
    Basic header type
    '''
    def __init__(self, name: str, length: int, zero_pad_index: bool = False):
        '''
        Set basic variables

        name    :   Name for header
        length  :   Max length of content, otherwise will shorten
        zero_pad_index  :   Pad zeros in front of index column if applicable
        '''
        self.name = name
        self.length = length
        self.zero_pad_index = zero_pad_index

class DapperTableHeaderOptions():
    '''
    Combined Header Options
    '''
    def __init__(self, headers: List[DapperTableHeader], separator='||'):
        self.headers = headers
        self.separator = separator
        if isinstance(headers, DapperTableHeader):
            self.headers = [headers]
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

class PaginationSetting():
    '''
    Pagination settings
    '''
    def __init__(self, pagination_type: PaginationOptions):
        self.pagination_type = pagination_type

class PaginationRows(PaginationSetting):
    '''
    Pagination By Rows
    '''
    def __init__(self, rows_per_message: int):
        super().__init__(PaginationOptions.ROWS)
        self.rows_per_message = rows_per_message

class PaginationLength(PaginationSetting):
    '''
    Pagination By Length
    '''
    def __init__(self, length_per_message: int):
        super().__init__(PaginationOptions.LENGTH)
        self.length_per_message = length_per_message


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

        self._headers = None
        self._separator = None

        if header_options:
            self._headers = header_options.headers
            # Make sure we add a single space at the end
            self._separator = f'{header_options.separator.replace(" ", "")} '

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

    def add_row(self, row: List[str] | str) -> bool:
        '''
        Add row to table

        row     :   List of items to go in row, assumes each item list is string representation
        '''
        # If headers, add extra checks, else just accept input
        self._validate_row(row)
        self._rows.append(row)
        return True

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
        self._rows[int(index)] = row
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
        return [row_string, '-' * total_length]

    def _format_row(self, row) -> str:
        '''
        Format row content to headers
        '''
        total_size = len(self._rows)
        col_items = []
        for (count, item) in enumerate(row):
            if self._headers[count].zero_pad_index:
                total_digits = len(str(total_size))
                column_size = len(str(item))
                item = f'{"0" * (total_digits - column_size)}{item}'
            col_string = shorten_string(item, self._headers[count].length)
            is_last_column = count == len(self._headers) - 1
            formatted_col = self._generate_formatted_string(self._headers[count].length, col_string, is_last_column)
            col_items.append(formatted_col)
        row_string = self._separator.join(i for i in col_items)
        row_string = row_string.rstrip(' ')
        return row_string

    def _format_rows(self) -> List[str]:
        '''
        Format all rows in the table
        '''
        output = []
        for row in self._rows:
            if self._headers:
                output += [self._format_row(row)]
                continue
            output += [row]
        return output

    def _format_final_print(self, row_output: List[str]) -> str:
        '''
        If set, remove double newlines and clean up output
        '''
        combined = '\n'.join(i for i in row_output)
        if not self.collapse_newlines:
            return combined
        combined = sub(r'\n{2,}', '\n', combined)
        combined = combined.strip('\n')
        return combined

    def print(self) -> List[str] | str:
        '''
        Print table
        '''
        # Set outputs properly
        all_output = []
        if self._headers:
            all_output += self._generate_headers()
        all_output += self._format_rows()
        # If no pagination options given
        if self._rows_per_message or self._length_per_message:
            split_rows = []
            if self._rows_per_message:
                split_rows = chunk_list(all_output, self._rows_per_message)
            if self._length_per_message:
                split_rows = chunk_list_by_length(all_output, self._length_per_message)
            split_output = []
            for sr in split_rows:
                split_output.append(self._format_final_print(sr))
            return split_output

        # If no pagination options given
        return self._format_final_print(all_output)

    @property
    def size(self) -> int:
        '''
        Return size of table (does not include headers)
        '''
        return len(self._rows)
