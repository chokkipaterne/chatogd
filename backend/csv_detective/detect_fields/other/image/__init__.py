from os.path import dirname, join
from csv_detective.process_text import _process_text
from mimetypes import MimeTypes

PROPORTION = 1

def _is(s):
    #Add by chokki
    '''Detects image'''
    mime = MimeTypes()
    mime_type = mime.guess_type(s)[0]

    if mime_type is None:
        return False

    return "image" in mime_type.split("/")[0]
