from csv_detective.process_text import _mini_process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut etre une longitude'''
    try:
        val = _mini_process_text(val)
        regex = r'^[-+]?(\d+([.,]\d*)?|[.,]\d+)$'
        if bool(re.match(regex, val)):
            val = float(val.replace(',','.'))
            if int(val) == val:
                return False
            return val >= -180 and val <= 180
        else:
            return False
    except:
        return False
