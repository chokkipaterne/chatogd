import pandas as pd
from urllib3 import PoolManager
import re
import requests
import csv
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile

def test_col_val(serie, test_func, proportion=0.9, skipna=True, num_rows=50, output_mode='ALL'):
    ''' Tests values of the serie using test_func.
         - skipna : if True indicates that NaNs are not counted as False
         - proportion :  indicates the proportion of values that have to pass the test
    for the serie to be detected as a certain format
    '''
    def apply_test_func(serie, test_func, _range): #TODO : change for a cleaner method and only test columns in modules labels
        try:
            #print(serie)
            rep = serie.iloc[_range].apply(test_func)
            #print(rep)
            return rep
        except AttributeError: # .name n'est pas trouvé
            return test_func(serie.iloc[_range])


    serie = serie[serie.notnull()]
    ser_len = len(serie)
    num_rows = min(ser_len, num_rows)
    #print(num_rows)
    _range = range(0, ser_len)
    if ser_len == 0:
        return False
    if(output_mode == 'ALL'):
        return apply_test_func(serie, test_func, _range).sum() / num_rows
    else:
        if proportion == 1:  # Then try first 1 value, then 5, then all
            for _range in [
                range(0, min(1, ser_len)),
                range(min(1, ser_len), min(5, ser_len)),
                range(min(5, ser_len), min(num_rows, ser_len))
            ]:  # Pour ne pas faire d'opérations inutiles, on commence par 1,
                # puis 5 puis num_rows valeurs
                if all(apply_test_func(serie, test_func, _range)):
                    pass
                else:
                    return 0.0
            return 1.0
        else:
            result = apply_test_func(serie, test_func, _range).sum() / len(serie)
            return  result if result >= proportion else 0.0

def test_col_label(label, test_func, proportion=1, output_mode='ALL') :
    ''' Tests label (from header) using test_func.
         - proportion :  indicates the minimum score to pass the test for the serie to be detected as a certain format
    '''
    if output_mode == 'ALL' :
        return test_func(label)
    else :
        result = test_func(label)
        return result if result >= proportion else False

def test_col(table, all_tests, num_rows, output_mode):
    # Initialising dict for tests
    test_funcs = dict()
    for test in all_tests:
        name = test.__name__.split('.')[-1]

        test_funcs[name] = {
            'func': test._is,
            'prop': test.PROPORTION
        }

    return_table = pd.DataFrame(columns=table.columns)
    for key, value in test_funcs.items():
        return_table.loc[key] = table.apply(lambda serie: test_col_val(
            serie,
            value['func'],
            value['prop'],
            num_rows = num_rows,
            output_mode=output_mode
        ))
    """pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    print(return_table)"""
    return return_table

def test_label(table, all_tests, output_mode) :
    # Initialising dict for tests
    test_funcs = dict()
    for test in all_tests:
        name = test.__name__.split('.')[-1]

        test_funcs[name] = {
            'func': test._is,
            'prop': test.PROPORTION
        }

    return_table = pd.DataFrame(columns=table.columns)
    for key, value in test_funcs.items():
        return_table.loc[key] = [test_col_label(
            col_name,
            value['func'],
            value['prop'],
            output_mode=output_mode
        ) for col_name in table.columns]
    return return_table

#modify by chokki
def prepare_output_dict(return_table, output_mode, threshold=0):
    return_dict_cols = return_table.to_dict('dict')
    return_dict_cols_intermediary = {}
    for column_name in return_dict_cols:
        return_dict_cols_intermediary[column_name] = []
        return_dict_cols_intermediary_full = []
        score_types = {}
        for detected_value_type in return_dict_cols[column_name]:
            if return_dict_cols[column_name][detected_value_type] == 0:
                continue
            dict_tmp = {}
            dict_tmp['format'] = detected_value_type
            dict_tmp['score'] = return_dict_cols[column_name][detected_value_type]

            if dict_tmp['score'] >= threshold:
                score_types[detected_value_type] = dict_tmp['score']
                return_dict_cols_intermediary_full.append(dict_tmp)

        toremove = []
        max_score = -1
        type_max = []
        sorted_score_types = dict(sorted(score_types.items(), key=lambda item: item[1]))
        for k,v in sorted_score_types.items():
            if v > max_score:
                max_score = v
                type_max = []
            if v == max_score:
                type_max.append(k)

        if "booleen" in score_types:
            if "float" in score_types and score_types["float"] > score_types["booleen"]:
                toremove.append("booleen")
            elif "int" in score_types and score_types["int"] > score_types["booleen"]:
                toremove.append("booleen")
        if "int" in score_types:
            if "float" in score_types and score_types["float"] > score_types["int"]:
                toremove.append("int")
            if "float" in score_types and score_types["float"] == score_types["int"]:
                toremove.append("float")

        return_dict_cols_intermediary[column_name] = [x for x in return_dict_cols_intermediary_full if x['format'] not in toremove]

        # Clean dict using priorities
        formats_detected = {x['format'] for x in return_dict_cols_intermediary[column_name]}
        formats_to_remove = set()

        # Deprioritise float and int detection vs others
        #formats_to_remove = formats_to_remove.union({'float', 'int'})
        if 'float' not in type_max:
            formats_to_remove.add('float')
        if 'int' not in type_max:
            formats_to_remove.add('int')
        if ('float' in type_max or 'int' in type_max):
            rem_geo = 0
            if "latitude_wgs" in type_max and threshold > 0.5:
                rem_geo = 1
                formats_to_remove.add('latitude_wgs')
            if "longitude_wgs" in type_max and threshold > 0.5:
                rem_geo = 1
                formats_to_remove.add('longitude_wgs')
            if "int" in type_max and "float" in type_max and len(type_max) > 2 and rem_geo == 0:
                formats_to_remove.add('float')
                formats_to_remove.add('int')
            elif ("int" in type_max or "float" in type_max) and not ("int" in type_max and "float" in type_max) and len(type_max) > 1 and rem_geo == 0:
                formats_to_remove.add('float')
                formats_to_remove.add('int')

        #if len(formats_detected - {'float', 'int'}) > 0:
        #    formats_to_remove = formats_to_remove.union({'float', 'int'})
        #if 'int' in formats_detected:
        #    formats_to_remove.add('float')
        if 'latitude_wgs_fr_metropole' in formats_detected:
            formats_to_remove.add('latitude_l93')
        if 'longitude_wgs_fr_metropole' in formats_detected:
            formats_to_remove.add('longitude_l93')
        if 'code_region' in formats_detected:
            formats_to_remove.add('code_departement')

        formats_to_keep = formats_detected - formats_to_remove

        detections = return_dict_cols_intermediary[column_name]
        detections = [x for x in detections if x['format'] in formats_to_keep]

        if output_mode == 'ALL':
            if len(detections) == 0:
                return_dict_cols_intermediary[column_name] = [{"python_type": "string","format": "string","score": 1.0}]
            else:
                return_dict_cols_intermediary[column_name] = sorted(detections, key=lambda x: x['score'], reverse=True)
        if output_mode == 'LIMITED':
            return_dict_cols_intermediary[column_name] = max(detections, key=lambda x: x['score']) if len(detections) > 0 else {'format': 'string', 'score': 1.0}

    return return_dict_cols_intermediary

#modify by chokki
def full_word_strictly_inside_string(word, string) :
    return (' '+word+' ' in string) or (string.startswith(word+' ')) or (string.endswith(' '+word))

#Check if the url is downloadable
def is_downloadable(url):
    rep = False
    if ("metadata" in url.lower()):
        return rep

    pool = PoolManager()
    #print(url)
    response = pool.request("GET", url, preload_content=False)

    # Maximum amount we want to read
    max_bytes = 200000000
    max_count = 50

    content_bytes = response.headers.get("Content-Length")
    print(content_bytes)
    if content_bytes and int(content_bytes) < max_bytes:
        rep = True
    elif content_bytes is None:
        # Alternatively, stream until we hit our limit
        amount_read = 0
        rep = True
        count = 0
        for chunk in response.stream():
            count += 1
            amount_read += len(chunk)
            print(amount_read)
            if amount_read > max_bytes or count > max_count:
                rep = False
                break
    # Release the connection back into the pool
    response.release_conn()
    return rep

#sort keys
def sort_keys(dicto):
    return dict(sorted(dicto.items(), key=lambda x: x[0]))

#Download zip resource
def download_zipfile(zipurl, save_path):
    try:
        with urlopen(zipurl) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as zfile:
                zfile.extractall(save_path)
                return True
    except Exception as e:
        return False
    return False

#Download csv resource
def download_csv(csv_url, save_path):
    req = requests.get(csv_url)
    if req and int(req.status_code) == 200:
        url_content = req.content
        csv_file = open(save_path, 'wb')
        csv_file.write(url_content)
        csv_file.close()
        return True
    return False

#Validate email
def isValid(email):
    regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
    checkres = False
    if re.fullmatch(regex, email):
        checkres = True
    return checkres
