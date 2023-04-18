from csv_detective.utils import full_word_strictly_inside_string
from csv_detective.process_text import _process_text

PROPORTION = 0.5

def _is(header):
    '''Returns 1 if the (processed) header matches one of the expected words combination, else 0'''

    words_combinations_list = ['latitude', 'lat', 'y', 'yf', 'yd', 'coordonnee y', 'coord y', 'ycoord', 'geocodage y gps', 'location latitude', 'ylatitude', 'ylat', 'latitude (y)', 'latitudeorg', 'coordinates.latitude', 'googlemap latitude', 'latitudelieu', 'latitude googlemap', 'latitude wgs84', 'y wgs84', 'latitude (wgs84)']
    processed_header = _process_text(header)

    header_matches_words_combination = 1.5*float(any([words_combination == processed_header for words_combination in words_combinations_list]))
    words_combination_in_header = 0.5*float(any([full_word_strictly_inside_string(words_combination, processed_header) for words_combination in words_combinations_list]))

    return max(header_matches_words_combination, words_combination_in_header)
