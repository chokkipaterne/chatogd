from csv_detective.process_text import _mini_process_text
import re

PROPORTION = 1

def _is(val):
    '''Renvoie True si val peut être une date au format iso, False sinon
    AAAA-MM-JJ HH-MM-SS avec indication du fuseau horaire

    '''
    val = _mini_process_text(val)

    a = bool(re.match(r'^\d\d\d\d[ -/](0[1-9]|1[012])[ -/](0[1-9]|[12][0-9]|3[01])[tT ]+[\d:\.]{5,8}([zZ]|[+\-][012]\d[0-5]\d)?$', val))
    # add by chokki
    reg = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
    reg2 = "^(?:\\d{4})-(?:\\d{2})-(?:\\d{2})T(?:\\d{2}):(?:\\d{2}):(?:\\d{2}(?:\\.\\d*)?)(?:(?:-(?:\\d{2}):(?:\\d{2})|Z)?)$"

    TIMESTAMP_MATCHER = re.compile(
        r'^\d{4}-\d{1,2}-\d{1,2}[T ]+\d{1,2}:\d{1,2}:\d{1,2}(\.\d{1,6})?'
        r' *(([+-]\d{1,2}(:\d{1,2})?)|Z|UTC)?$')
    reg3 = "\d{4}[ -/]\d{1,2}[ -/]\d{1,2}[T ]+\d{1,2}:\d{1,2}(:\d{1,2})?"
    reg4 = "\d{1,2}[ -/]\d{1,2}[ -/]\d{4}[T ]+\d{1,2}:\d{1,2}(:\d{1,2})?"


    return a or (re.search(reg3, val.upper()) is not None) or (re.search(reg4, val.upper()) is not None) or (re.search(reg, val.upper()) is not None) or (re.search(reg2, val.upper()) is not None) or bool(TIMESTAMP_MATCHER.match(val.upper()))
