from os.path import dirname, join
from csv_detective.process_text import _process_text_phone
import re

PROPORTION = 1

def _is(val):
    '''Detects phone'''
    #add by chokki
    val = _process_text_phone(val)
    #regex = "^\\+?\\d{1,4}?[-.\\s]\\(?\\d{1,3}?\\)?[-.\\s]\\d{1,4}[-.\\s]\\d{1,4}[-.\\s]\\d{1,9}$"
    regex2 = "^\\+?[1-9][0-9]{7,14}$"
    regex3 = "^00[1-9]{7,14}$"
    return bool(re.match(regex2, val)) or bool(re.match(regex3, val))
    #return bool(re.match(regex, val)) or bool(re.match(regex2, val))
