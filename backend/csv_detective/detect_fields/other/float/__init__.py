from os.path import dirname, join
from csv_detective.process_text import _mini_process_text
import re

PROPORTION = 1

def _is(val):
    '''Detects floats'''
    """try:
        float(val.replace(' ', '').replace(',', '.'))
        return True
    except ValueError:
        return False"""
    #Add by chokki
    regex = r'^[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?$'
    return bool(re.match(regex, val))
