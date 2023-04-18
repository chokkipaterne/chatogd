from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    #Add by chokki
    '''Detects hexcolor'''
    return re.search(r'^#?(?:[0-9a-fA-F]{3}){1,2}$', val) is not None
