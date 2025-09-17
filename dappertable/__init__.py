'''
Taken from https://medium.com/@gullevek/python-output-formatting-double-byte-characters-6d6d18d04be3
Use these functions to get proper length of strings for formatting with east asian characters
'''
from re import sub
from typing import List
from unicodedata import east_asian_width

def shorten_string_cjk(intput_string: str, width: int, placeholder: str = '..') -> str:
    '''
    Shorten a string with CJK (double byte) characters

    intput_string (string): input string to shorten
    width (int): character count to shorten too
    placeholder (str, optional): cut of end characters if space is there. Defaults to '..'.
    '''
    # get the length with double byte charactes
    string_len_cjk = string_length_cjk(str(intput_string))
    # if double byte width is too big
    if string_len_cjk > width:
        # set current length and output string
        cur_len = 0
        out_string = ''
        # loop through each character
        for char in str(intput_string):
            # set the current length if we add the character
            cur_len += 2 if east_asian_width(char) in "WF" else 1
            # if the new length is smaller than the output length to shorten too add the char
            if cur_len <= (width - len(placeholder)):
                out_string += char
        # return string with new width and placeholder
        return f"{out_string}{placeholder}"
    return str(intput_string)

def string_length_cjk(input_string: str) -> int:
    '''
    String lenth for a CJK (double byte) string

    string (string): string to get length for
    '''
    # return string len including double count for double width characters
    return sum(1 + (east_asian_width(c) in "WF") for c in input_string)

def format_string_length(input_string: str, length: int) -> int:
    '''
    Returns length udpated for string with double byte characters
    get string length normal, get string length including double byte characters
    then subtract that from the original length

    input_string (string): string to calculate length of
    length (int): maxium length for string
    '''
    return length - (string_length_cjk(input_string) - len(input_string))


# https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
def chunk_list(input_list, size):
    '''
    Split list into equal sized chunks
    '''
    size = max(1, size)
    return [input_list[i:i+size] for i in range(0, len(input_list), size)]

class DapperTableException(Exception):
    '''
    Generic exception class
    '''

class DapperTableHeader():
    '''
    Basic header type
    '''
    def __init__(self, name: str, length: int):
        '''
        Set basic variables
        '''
        self.name = name
        self.length = length

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


class DapperTable():
    '''
    Split large inputs into smaller messages, also supports formatting
    '''
    def __init__(self, header_options : DapperTableHeaderOptions = None,
                 rows_per_message: int = None, collapse_newlines: bool = True):
        '''
        Init a dapper table

        headerOptions       :   DapperTable header options, if not given will treat as raw input
        rows_per_message    :   Split table by this number of rows to different messages
        collapse_newlines   :   Collapse multiple newlines in messages
        '''

        self._rows_per_message = rows_per_message
        self.collapse_newlines = collapse_newlines
        if rows_per_message and rows_per_message < 1:
            raise DapperTableException('Invalid value for rows per message')
        self._rows = []

        self._headers = None
        self._separator = None

        if header_options:
            self._headers = header_options.headers
            # Make sure we add a single space at the end
            self._separator = f'{header_options.separator.replace(" ", "")} '

    def add_row(self, row: List[str] | str) -> bool:
        '''
        Add row to table

        row     :   List of items to go in row, assumes each item list is string representation
        '''
        # If headers, add extra checks, else just accept input
        if self._headers:
            if not isinstance(row, list):
                raise DapperTableException('Row input must be list if headers were given')
            if len(row) != len(self._headers):
                raise DapperTableException('Row length must match length of headers')
        self._rows.append(row)
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

    def _generate_headers(self) -> List[str]:
        '''
        Generate header content, first two rows of table
        '''
        col_items = []
        total_length = 0
        # Setup headers as first row
        for col in self._headers:
            col_string = shorten_string_cjk(col.name, col.length)
            col_length = format_string_length(col_string, col.length)
            col_items.append(f'{col_string:{col_length}}')
            total_length += col.length
        row_string = self._separator.join(i for i in col_items)
        row_string = row_string.rstrip(' ')
        total_length += len(self._separator) * (len(col_items) - 1)
        # First row and then table formatter
        return [row_string, '-' * total_length]

    def _format_row(self, row) -> str:
        '''
        Format row content to headers
        '''
        col_items = []
        for (count, item) in enumerate(row):
            col_string = shorten_string_cjk(item, self._headers[count].length)
            col_length = format_string_length(col_string, self._headers[count].length)
            col_items.append(f'{col_string:{col_length}}')
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
        if not self._rows_per_message:
            return self._format_final_print(all_output)
        # Split rows if necessary
        split_rows = chunk_list(all_output, self._rows_per_message)
        split_output = []
        for sr in split_rows:
            split_output.append(self._format_final_print(sr))
        return split_output

    @property
    def size(self) -> int:
        '''
        Return size of table (does not include headers)
        '''
        return len(self._rows)
