import re
from csv_detective.process_text import _mini_process_text

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut être une date, False sinon'''
    val = _mini_process_text(val)
    # matches 1993-12/02
    TIME_MATCHER = re.compile(r'^\d{1,2}:\d{1,2}:\d{1,2}(\.\d{1,6})?$')

    return bool(TIME_MATCHER.match(val))
