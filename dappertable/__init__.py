# Taken from https://medium.com/@gullevek/python-output-formatting-double-byte-characters-6d6d18d04be3
from unicodedata import east_asian_width

def shorten_string_cjk(intput_string, width, placeholder='..'):
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
    else:
        return str(intput_string)

def string_length_cjk(input_string):
    '''
    String lenth for a CJK (double byte) string

    string (string): string to get length for
    '''
    # return string len including double count for double width characters
    return sum(1 + (east_asian_width(c) in "WF") for c in input_string)

def format_string_length(input_string, length):
    '''
    Returns length udpated for string with double byte characters
    get string length normal, get string length including double byte characters
    then subtract that from the original length

    input_string (string): string to calculate length of
    length (int): maxium length for string
    '''
    return length - (string_length_cjk(input_string) - len(input_string))


class DapperTableException(Exception):
    pass

class DapperTable():
    '''
    Format nice tables with f-string
    '''
    def __init__(self, headers, rows_per_message=None):
        '''
        Init a dapper table

        headers             :   List of headers to put at top. Should be list of dicts with {name: <name>, length: <length>}
        rows_per_message    :   Split table by this number of rows to different messages
        '''
        if not headers:
            raise DapperTableException('Must have at least one header')
        self.headers = headers
        self.rows_per_message = rows_per_message
        if rows_per_message and rows_per_message < 1:
            raise DapperTableException('Invalid value for rows per message')
        self._rows = []
        try:
            col_items = []
            for col in self.headers:
                col_string = shorten_string_cjk(col['name'], col['length'])
                col_length = format_string_length(col_string, col['length'])
                col_items.append(f'{col_string:{col_length}}')
            self._rows.append('|| '.join(i for i in col_items))
        except KeyError:
            raise DapperTableException('Headers missing header "name" or "length"')

    def add_row(self, row):
        '''
        Add row to table

        row     :   List of items to go in row, must match length of headers
        '''
        if len(row) != len(self.headers):
            raise DapperTableException('Row length must match length of headers')
        col_items = []
        for (count, item) in enumerate(row):
            col_string = shorten_string_cjk(item, self.headers[count]['length'])
            col_length = format_string_length(col_string, self.headers[count]['length'])
            col_items.append(f'{col_string:{col_length}}')
        self._rows.append('|| '.join(i for i in col_items))
    
    def remove_row(self, index):
        '''
        Remove row from table

        index   :   Index of row, cannot remove headers
        '''
        # Add 1 so we dont remove first item which is headers
        try:
            del self._rows[index + 1]
        except IndexError:
            raise DapperTableException('Invalid deletion index')

    def print(self):
        '''
        Print table
        '''
        if not self.rows_per_message:
            return '\n'.join(i for i in self._rows)
        table_strings = []
        table = self._rows[0]
        for (count, item) in enumerate(self._rows[1:]):
            if not table:
                table = f'{item}'
            else:
                table = f'{table}\n{item}'
            if (count + 1) % self.rows_per_message == 0:
                table_strings.append(table)
                table = ''
        if table:
            table_strings.append(table)
        return table_strings