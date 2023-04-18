from os.path import dirname, join
from csv_detective.process_text import _process_text
import re

PROPORTION = 1

def _is(val):
    '''Repère le sexe'''
    val =_process_text(val)

    list_sex_short = ['h', 'f', 'm']
    match = False
    a = any([val.lower().strip() == x for x in list_sex_short])
    if a:
        match = True

    return (val in ['homme', 'femme', 'men', 'women', 'masculin', 'feminin', 'male', 'female', 'males', 'females', 'mens', 'womens']) or match
