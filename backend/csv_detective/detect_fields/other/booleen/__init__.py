from os.path import dirname, join
from csv_detective.process_text import _process_text

PROPORTION = 1

def _is(val):
    '''Détection les booléens'''
    #liste_bool = ['0','1','vrai','faux','true','false','oui','non', 'yes', 'no', 'y', 'n', 'o']
    liste_bool = ['vrai','faux','true','false','oui','non', 'yes', 'no']

    list_bool_short = ['y', 'n', 'o']
    match = False

    a = any([val.lower().strip() == x for x in list_bool_short])
    if a:
        match = True


    return val.lower() in liste_bool or match
