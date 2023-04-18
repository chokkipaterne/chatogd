from csv_detective.process_text import _mini_process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut etre une latitude,longitude'''
    val = _mini_process_text(val)
    nb_parts_spaces = val.split(" ")
    nb_parts_comma = val.split(",")

    # Add by Chokki
    reg1 = r"[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)(,)*\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)"
    # Geographic coordinates (e.g. 35°56′51″N 75°45′12″E)
    reg2 = r"[0-9]+°[0-9]+(′|')[0-9]+(″|''|′′)\s*[N|S](,)*\s*[0-9]+°[0-9]+(′|')[0-9]+(″|''|′′)\s*[W,E]"
    reg3 = r"[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)\s[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)"
    # End Add by Chokki

    a = (re.search(reg1, val, flags=re.I | re.M) is not None or re.search(reg2, val, flags=re.I | re.M) is not None or re.search(reg3, val, flags=re.I | re.M) is not None) and (re.search("point", val) or ("(" in val and ")" in val))
    b = (re.match(r"^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)(,)*\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$", val, flags=re.I | re.M) is not None or re.match(r"^[0-9]+°[0-9]+(′|')[0-9]+(″|''|′′)\s*[N|S](,)*\s*[0-9]+°[0-9]+(′|')[0-9]+(″|''|′′)\s*[W,E]$", val, flags=re.I | re.M) is not None or re.match(r"^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)\s[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$", val, flags=re.I | re.M) is not None)
    return (a or b) and (len(nb_parts_spaces) >= 2 or len(nb_parts_comma) >= 2)
