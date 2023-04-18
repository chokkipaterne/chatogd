from csv_detective.process_text import _mini_process_text
import re

PROPORTION = 1

#add by chokki
def _is(val):
    '''Renvoie True si val peut etre geoshape'''
    val = _mini_process_text(val)
    reg1 = r"[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)(,)*\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)"
    # Geographic coordinates (e.g. 35°56′51″N 75°45′12″E)
    reg2 = r"[0-9]+°[0-9]+(′|')[0-9]+(″|''|′′)\s*[N|S](,)*\s*[0-9]+°[0-9]+(′|')[0-9]+(″|''|′′)\s*[W,E]"

    if (re.search(reg1, val, flags=re.I | re.M) is not None or re.search(reg2, val, flags=re.I | re.M) is not None) and (re.search("type", val) or re.search("polygon", val) or re.search("coordinates", val)):
        return True

    return False
