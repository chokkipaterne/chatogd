from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1
f = open(join(dirname(__file__), 'country.txt'), 'r')
countries = f.read().split('\n')
f.close()

#add by chokki
def _is(val):
    '''Match avec le nom des countries'''

    val = _process_text(val)
    match = False
    a = any([val == x.lower().strip() for x in countries])
    if a:
        match = True
    return match
