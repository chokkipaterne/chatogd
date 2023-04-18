import re

PROPORTION = 1

def _is(val):
    '''Detects UUIDs'''
    regex = r'^[{]?[0-9a-fA-F]{8}' + '-?([0-9a-fA-F]{4}-?)' + '{3}[0-9a-fA-F]{12}[}]?$'
    uuid_pattern = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$"
    return bool(re.match(regex, val)) or bool(re.match(uuid_pattern, val.lower()))
