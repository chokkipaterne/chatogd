from os.path import dirname, join
from csv_detective.process_text import _mini_process_text
import re

PROPORTION = 1

def _is(val):
    '''Detects urls'''
    #Add by chokki
    val = _mini_process_text(val)
    reg = "https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
    a = 'http://' in val
    b = 'www.' in val
    c = any([x in val for x in ['.fr', '.com', '.org', '.gouv', '.net', '.io', '.be']])
    d = not ('@' in val)
    return ((a or b or c) and d) or (re.search(reg, val.lower(), re.M) is not None)
