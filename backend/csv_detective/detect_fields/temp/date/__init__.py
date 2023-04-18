import re
from dateutil.parser import parse
import dateutil.parser as dateutil
from csv_detective.process_text import _mini_process_text

PROPORTION = 1


def is_dateutil_date(val: str) -> bool:
    try:
        parse(val, fuzzy=False)
        return True
    except (ValueError, TypeError, OverflowError):
        return False


def is_float(val: str) -> bool:
    try:
        float(val)
        return True
    except ValueError:
        return False
# Add by Chokki
def is_decimal(s):
    # not a number is not a decimal
    if s.lower() == "nan":
        return False

    # check "." and ","
    if s.find(".") >= 0 and s.find(",") >= 0:
        return False
    else:
        s = s.replace(",", ".")

    try:
        float(s)
        return True
    except ValueError:
        return False

def is_date(s):
    def regex_test(s):
        date_match = re.search(r'[0-9]+-[0-9]+-[0-9]+', s)
        return date_match is not None and (len(s) - len(date_match[0])) <= 19

    def month_test(s):
        words = s.lower().split(' ')
        for word in words:
            return word in [
                "january", "february", "march", "april", "may", "june",
                "july", "august", "september", "october", "november", "december",
                "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug",
                "sep", "oct", "nov", "dec", "fev", "avr", "mai", "jui",
                "janvier", "fevrier", "mars", "avril", "juin", "juillet",
                "aout", "septembre", "octobre", "novembre", "decembre"
            ]

    def date_format_test(s):
        try:
            dateutil.parse(s)
            return True
        except (ValueError, OverflowError):
            return False

    '''regex_test(s) or'''
    return month_test(s) or (regex_test(s) and date_format_test(s) and not is_decimal(s))


def _is(val):
    '''Renvoie True si val peut être une date, False sinon'''
    val = _mini_process_text(val)
    # matches 1993-12/02
    a = bool(re.match(r'^(19|20)\d\d[ -/_;.:,](0[1-9]|1[012])[ -/_;.:,](0[1-9]|[12][0-9]|3[01])$', val))

    # matches 02/12 03 and 02_12 2003
    b = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01])[ -/_](0[1-9]|1[012])[ -/_]([0-9]{2}|(19|20)[0-9]{2}$)', val))

    # matches 02052003
    c = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[012])([0-9]{2}|(19|20){2}$)', val))

    # matches 19931202
    d = bool(re.match(r'^(19|20)\d\d(0[1-9]|1[012])(0[1-9]$|[12][0-9]$|3[01]$)', val))

    # matches JJ*MM*AAAA
    e = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01]).?(0[1-9]|1[012]).?(19|20)?\d\d$', val))

    # matches JJ-mmm-AAAA
    f = bool(re.match(r'^(0[1-9]|[12][0-9]|3[01])[ -/_;.:,](jan|fev|feb|mar|avr|apr|mai|may|jun|jui|jul|aou|aug|sep|oct|nov|dec)[ -/_;.:,]([0-9]{2}$|(19|20)[0-9]{2}$)', val))
    #Add by chokki
    g = bool(re.match(r'^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}$', val))

    h = bool(re.match(r'^\d{4}-(?:[1-9]|0[1-9]|1[012])-(?:[1-9]|0[1-9]|[12][0-9]|3[01])$', val))

    i = bool(re.match(r'^(19|20)\d\d[ -/_;.:,](0[1-9]|1[012])$', val))

    rep = is_date(val)
    return a or b or c or d or e or f or g or h or i or rep
