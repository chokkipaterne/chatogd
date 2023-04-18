from django.shortcuts import render, redirect
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from chatdata.models import *
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
import json
import re
import io
import pandas as pd
import numpy as np
from csv_detective.detect_fields import temp
from csv_detective.detect_fields import other
from csv_detective.explore_csv import data_quality_dataset
import urllib
import os


# Create your views here.

#Check if val is a date
def check_is_date(val):
    if temp.date._is(val) or temp.datetime_iso._is(val) or temp.datetime_rfc822._is(val) or temp.year._is(val):
        return True
    return False

def custom_len(val):
    try:
        if val is None:
            return 0
        else:
            return len(val)
    except Exception as e:
        return 0

def get_weights(metadata_dimensions, data_dimensions):
    weights = {}
    for d in metadata_dimensions:
        weights[d["id"]] = d["weight"]
        for m in d["metrics"]:
            weights[m["id"]] = m["weight"]
    for d in data_dimensions:
        weights[d["id"]] = d["weight"]
        for m in d["metrics"]:
            weights[m["id"]] = m["weight"]
    return weights

def get_info_url(url):
    try:
        r = urllib.request.urlopen(url)
        header = r.headers                              # type is email.message.EmailMessage
        contentType = header.get_content_type()         # or header.get('content-type')
        contentLength = header.get('content-length')
        filename = header.get_filename()
        ext = ""
        if filename:
            ext = filename.split(".")[-1]
        return {"contentType":contentType,"contentLength":contentLength, "filename":filename, "ext":ext}
    except Exception as e:
        print(e)
        return {"contentType":"","contentLength":0, "filename":"", "ext":""}

#count number of empty fields in metadata
def count_null(var, fields_to_include, count):
    type_var = type(var).__name__
    if type_var == "int" or type_var == "float" or type_var == "bool":
        return 0
    elif (type_var == "str" and var == "") or (type_var == "NoneType"):
        return 1
    elif type_var == 'list':
        if custom_len(var) == 0:
            return 1
        else:
            for v in var:
                count += count_null(v, fields_to_include, 0)
            return count
    elif type_var == 'dict':
        if bool(var):
            for k, v in var.items():
                if k == "fields":
                    to_include = []
                    for f in v:
                        if f["name"] in fields_to_include:
                            to_include.append(f)
                    if custom_len(to_include) == 0:
                        count += 0
                    else:
                        count += count_null(to_include, fields_to_include, 0)
                else:
                    count += count_null(v, fields_to_include, 0)
            return count
        else:
            return 1
    else:
        return 0

#count total number of fields in metadata
def count_total(var, fields_to_include, count):
    type_var = type(var).__name__
    if type_var == "int" or type_var == "float" or type_var == "bool":
        return 1
    elif (type_var == "str" and var == "") or (type_var == "NoneType"):
        return 1
    elif type_var == 'list':
        if custom_len(var) == 0:
            return 1
        else:
            is_dict = 0
            for v in var:
                if type(v).__name__ == 'dict':
                    is_dict = 1
                    count += count_total(v, fields_to_include, 0)
            if is_dict == 0:
                count = 1
            return count
    elif type_var == 'dict':
        if bool(var):
            for k, v in var.items():
                if k == "fields":
                    to_include = []
                    for f in v:
                        if f["name"] in fields_to_include:
                            to_include.append(f)
                    if custom_len(to_include) == 0:
                        count += 0
                    else:
                        count += count_total(to_include, fields_to_include, 0)
                else:
                    count += count_total(v, fields_to_include, 0)
            return count
        else:
            return 1
    else:
        return 1
    
def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

# Calculate metrics quality
def md1_1(request, file, fields_to_include):
    null_fields = count_null(file, fields_to_include, 0)
    total_fields = count_total(file, fields_to_include, 0)
    if total_fields == 0:
        return 0
    else:
        return (1 - (null_fields/total_fields))*100

def md2_1(request, file):
    value = 0
    if "metas" in file:
        if "default" in file["metas"]:
            if "keyword" in file["metas"]["default"]:
                if custom_len(file["metas"]["default"]["keyword"]) > 0:
                    value = 100
    return value

def md2_2(request, file):
    value = 0
    if "metas" in file:
        if "default" in file["metas"]:
            if "theme" in file["metas"]["default"]:
                if custom_len(file["metas"]["default"]["theme"]) > 0:
                    value = 100
    return value

def md2_3(request, file):
    value = 0
    if "metas" in file:
        if "default" in file["metas"]:
            if "title" in file["metas"]["default"]:
                if custom_len(remove_html_tags(file["metas"]["default"]["title"])) > 0:
                    value = 100
    return value

def md2_4(request, file):
    value = 0
    if "metas" in file:
        if "default" in file["metas"]:
            if "description" in file["metas"]["default"]:
                if custom_len(remove_html_tags(file["metas"]["default"]["description"])) > 0:
                    value = 100
    return value

def md2_5(request, file):
    value = 0
    if "metas" in file:
        if "dcat" in file["metas"]:
            if "temporal" in file["metas"]["dcat"]:
                if custom_len(file["metas"]["dcat"]["temporal"]) > 0:
                    value = 100
            elif "temporal_coverage_start" in file["metas"]["dcat"]:
                if custom_len(file["metas"]["dcat"]["temporal_coverage_start"]) > 0:
                    value = 100
            elif "temporal_coverage_end" in file["metas"]["dcat"]:
                if custom_len(file["metas"]["dcat"]["temporal_coverage_end"]) > 0:
                    value = 100
    return value

def md2_6(request, file):
    value = 0
    if "metas" in file:
        if "default" in file["metas"]:
            if "territory" in file["metas"]["default"]:
                if custom_len(file["metas"]["default"]["territory"]) > 0:
                    value = 100
        elif "dcat" in file["metas"]:
            if "temporal" in file["metas"]["dcat"]:
                if custom_len(file["metas"]["dcat"]["spatial"]) > 0:
                    value = 100
    return value

def md3_1(request, current_portal, dataset_id):
    more_details = current_portal["system_more_details"]
    portal_link = current_portal["more_details"]["link"]
    link = portal_link + more_details["suffix"] + more_details["explore_dt"]
    link = link.replace("#dt_id#", str(dataset_id))
    response = requests.get(link)
    if response and int(response.status_code) == 200:
        return 100
    return 0


def md3_2_3(request, current_portal, dataset_id):
    more_details = current_portal["system_more_details"]
    portal_link = current_portal["more_details"]["link"]
    link = portal_link + more_details["suffix"] + more_details["explore_dt"]
    link = link.replace("#dt_id#", str(dataset_id))+"exports"
    response = requests.get(link)
    rep1 = 0
    rep2 = 0
    if response and int(response.status_code) == 200:
        exports = response.json()
        if "links" in exports:
            if custom_len(exports["links"]) > 1:
                rep1 = 100
            for v in exports["links"]:
                if v["rel"] != "self":
                    response = requests.get(v["href"])
                    if response and int(response.status_code) == 200:
                        rep2 = 100
                        break
    return rep1, rep2

def md3_3(request, current_portal, dataset_id):
    more_details = current_portal["system_more_details"]
    portal_link = current_portal["more_details"]["link"]
    link = portal_link + more_details["suffix"] + more_details["export_dt"]
    link = link.replace("#dt_id#", str(dataset_id))
    init_link = link

    for fmt in settings.DATASET_EXTENSIONS:
        link = init_link.replace("#format#", str(fmt))
        response = requests.get(link)
        if response and int(response.status_code) == 200:
            return 100
    return 0

def md4_1(request, file):
    #detect urls
    #
    nb = 0
    nb_conform = 0
    if "metas" in file:
        if "default" in file["metas"]:
            if "license_url" in file["metas"]["default"]:
                if file["metas"]["default"]["license_url"]:
                    nb +=1
                    license_url = file["metas"]["default"]["license_url"]
                    if other.url._is(license_url):
                        nb_conform += 1 
            if "references" in file["metas"]["default"]:
                if file["metas"]["default"]["references"]:
                    nb +=1
                    references = file["metas"]["default"]["references"]
                    if other.url._is(references):
                        nb_conform += 1 
    if nb == 0:
        return 100
    else:
        return 100*(nb_conform/nb)

def md4_2(request, file):
    #detect dates
    nb = 0
    nb_conform = 0
    if "metas" in file:
        if "dcat" in file["metas"]:
            if "created" in file["metas"]["dcat"]:
                if file["metas"]["dcat"]["created"]:
                    nb +=1
                    created = file["metas"]["dcat"]["created"]
                    if check_is_date(created):
                        nb_conform += 1 
            if "issued" in file["metas"]["dcat"]:
                if file["metas"]["dcat"]["issued"]:
                    nb +=1
                    issued = file["metas"]["dcat"]["issued"]
                    if check_is_date(issued):
                        nb_conform += 1 
            if "temporal" in file["metas"]["dcat"]:
                if file["metas"]["dcat"]["temporal"]:
                    nb +=1
                    temporal = file["metas"]["dcat"]["temporal"]
                    if check_is_date(temporal):
                        nb_conform += 1 
            if "temporal_coverage_start" in file["metas"]["dcat"]:
                if file["metas"]["dcat"]["temporal_coverage_start"]:
                    nb +=1
                    temporal_coverage_start = file["metas"]["dcat"]["temporal_coverage_start"]
                    if check_is_date(temporal_coverage_start):
                        nb_conform += 1 
            if "temporal_coverage_end" in file["metas"]["dcat"]:
                if file["metas"]["dcat"]["temporal_coverage_end"]:
                    nb +=1
                    temporal_coverage_end = file["metas"]["dcat"]["temporal_coverage_end"]
                    if check_is_date(temporal_coverage_end):
                        nb_conform += 1 

        if "default" in file["metas"]:
            if "modified" in file["metas"]["default"]:
                if file["metas"]["default"]["modified"]:
                    nb +=1
                    modified = file["metas"]["default"]["modified"]
                    if check_is_date(modified):
                        nb_conform += 1 
            if "data_processed" in file["metas"]["default"]:
                if file["metas"]["default"]["data_processed"]:
                    nb +=1
                    data_processed = file["metas"]["default"]["data_processed"]
                    if check_is_date(data_processed):
                        nb_conform += 1 
            if "metadata_processed" in file["metas"]["default"]:
                if file["metas"]["default"]["metadata_processed"]:
                    nb +=1
                    metadata_processed = file["metas"]["default"]["metadata_processed"]
                    if check_is_date(metadata_processed):
                        nb_conform += 1 

    if nb == 0:
        return 100
    else:
        return 100*(nb_conform/nb)

def md4_3(request, file):
    #detect email
    nb = 0
    nb_conform = 0

    if "metas" in file:
        if "dcat" in file["metas"]:
            if "contact_email" in file["metas"]["dcat"]:
                if file["metas"]["dcat"]["contact_email"]:
                    nb +=1
                    contact_email = file["metas"]["dcat"]["contact_email"]
                    if other.email._is(contact_email):
                        nb_conform += 1 
        if "inspire" in file["metas"]:
            if "contact_email" in file["metas"]["inspire"]:
                if file["metas"]["inspire"]["contact_email"]:
                    nb +=1
                    contact_email = file["metas"]["inspire"]["contact_email"]
                    if other.email._is(contact_email):
                        nb_conform += 1 
    if nb == 0:
        return 100
    else:
        return 100*(nb_conform/nb)

def md4_4(request, file):
    #dcat-ap
    if "metas" in file:
        if "dcat" in file["metas"]:
            null_fields = count_null(file["metas"]["dcat"], [], 0)
            total_fields = count_total(file["metas"]["dcat"], [], 0)
            if total_fields == 0:
                return 0
            else:
                return (1 - (null_fields/total_fields))*100
    return 0

def md5_1(request, file_info):
    if file_info["ext"] and file_info["ext"].lower() in settings.DATASET_EXTENSIONS:
        return 100
    return 0

def md6_1(request, file_info):
    if file_info["ext"] and file_info["ext"].lower() in settings.NON_PROPRIO_DATASET_EXTENSIONS:
        return 100
    return 0

def md6_2(request, file):
    if "metas" in file:
        if "default" in file["metas"]:
            if "license" in file["metas"]["default"]:
                if file["metas"]["default"]["license"]:
                    return 100
    return 0

def md6_3(request, file):
    if "metas" in file:
        if "default" in file["metas"]:
            if "license" in file["metas"]["default"]:
                if file["metas"]["default"]["license"]:
                    license = file["metas"]["default"]["license"].upper()
                    list_license = [lic for lic in settings.OPEN_LICENSES if lic in license]
                    if license in settings.OPEN_LICENSES or custom_len(list_license)>0:
                        return 100
    return 0

def md6_4(request, file):
    if "metas" in file:
        if "default" in file["metas"]:
            if "license" in file["metas"]["default"]:
                if file["metas"]["default"]["license"]:
                    license = file["metas"]["default"]["license"].upper()
                    list_license = [lic for lic in settings.LICENCES if lic in license]
                    if license in settings.LICENCES or custom_len(list_license)>0:
                        return 100
    return 0

def md7_1(request, file):
    if "metas" in file:
        if "custom" in file["metas"]:
            if "periodicity" in file["metas"]["custom"]:
                if file["metas"]["custom"]["periodicity"]:
                    if custom_len(file["metas"]["custom"]["periodicity"]) > 0:
                        return 100
    return 0

def md7_2(request, file):
    if "metas" in file:
        if "dcat" in file["metas"]:
            if "created" in file["metas"]["dcat"]:
                if file["metas"]["dcat"]["created"]:
                    return 100
    return 0

def md7_3(request, file):
    if "metas" in file:
        if "default" in file["metas"]:
            if "modified" in file["metas"]["default"]:
                if file["metas"]["default"]["modified"]:
                    return 100
    return 0

def md8_1(request, file_info, select_format):
    if file_info["ext"] == select_format:
        return 100
    return 0

def md8_2(request, file_info, current_portal, dataset_id, select_format):
    if file_info["contentLength"]:
        more_details = current_portal["system_more_details"]
        portal_link = current_portal["more_details"]["link"]
        link = portal_link + more_details["suffix"] + more_details["export_dt"]
        link = link.replace("#dt_id#", str(dataset_id))
        link = link.replace("#format#", str(select_format))
        file_size = 0
        save_path = settings.MEDIA_ROOT+"/"+str(dataset_id)+"."+select_format
        if not os.path.isfile(save_path):
            rep = download_other_file(link, save_path)
        if os.path.isfile(save_path):
            file_size = os.path.getsize(save_path) 
            if abs(file_size -file_info["contentLength"]) < 1000:
                return 100
    return 0

def md9_1(request, file, fields_to_include):
    nb = 0
    nb_desc = 0
    fields = file["fields"]
    for f in fields:
        if f["name"] in fields_to_include:
            nb += 1 
            if f["description"]:
                if custom_len(remove_html_tags(f["description"])) >0 and custom_len(remove_html_tags(f["name"])) >0:
                    nb_desc += 1
    if nb == 0:
        return 0
    else:
        return 100*(nb_desc/nb)

#todo
def md9_2(request, file, fields_to_include):
    nb = 0
    nb_desc = 0
    fields = file["fields"]
    for f in fields:
        if f["name"] in fields_to_include:
            nb += 1 
            if f["description"]:
                if custom_len(remove_html_tags(f["name"])) >0 and custom_len(remove_html_tags(f["description"])) > 30 and remove_html_tags(f["description"]) != remove_html_tags(f["name"]):
                    nb_desc += 1
    if nb == 0:
        return 0
    else:
        return 100*(nb_desc/nb)

def md10_1(request, file):
    if "metas" in file:
        if "dcat" in file["metas"]:
            if "contact_name" in file["metas"]["dcat"]:
                if file["metas"]["dcat"]["contact_name"]:
                    if custom_len(file["metas"]["dcat"]["contact_name"]) > 0:
                        return 100
            if "contact_email" in file["metas"]["dcat"]:
                if file["metas"]["dcat"]["contact_email"]:
                    if custom_len(file["metas"]["dcat"]["contact_email"]) > 0:
                        return 100
    return 0


def md10_2(request, file):
    if "metas" in file:
        if "dcat" in file["metas"]:
            if "creator" in file["metas"]["dcat"]:
                if file["metas"]["dcat"]["creator"]:
                    if custom_len(file["metas"]["dcat"]["creator"]) > 0:
                        return 100
        if "default" in file["metas"]:
            if "publisher" in file["metas"]["default"]:
                if file["metas"]["default"]["publisher"]:
                    if custom_len(file["metas"]["default"]["publisher"]) > 0:
                        return 100
    return 0

def md11_1(request, file, current_portal, dataset_id):
    value = 100
    more_details = current_portal["system_more_details"]
    portal_link = current_portal["more_details"]["link"]
    link = portal_link + more_details["suffix"] + more_details["search_dt"]
    if "default" in file["metas"]:
        if "title" in file["metas"]["default"]:
            if file["metas"]["default"]["title"]:
                if custom_len(file["metas"]["default"]["title"]) > 0:
                    title = file["metas"]["default"]["title"]
                    search = 'search("'+title+'")'
                    link = link.replace("#dt_id#", search)
                    response = requests.get(link)
                    if response and int(response.status_code) == 200:
                        rep = response.json()
                        if "total_count" in rep:
                            if rep["total_count"] > 1:
                                value = 0
    return value

def md11_2(request, file, current_portal):
    value = 100
    more_details = current_portal["system_more_details"]
    portal_link = current_portal["more_details"]["link"]
    link = portal_link + more_details["suffix"] + more_details["search_dt"]
    if "default" in file["metas"]:
        if "description" in file["metas"]["default"]:
            if file["metas"]["default"]["description"]:
                if custom_len(file["metas"]["default"]["description"]) > 0:
                    description = file["metas"]["default"]["description"]
                    search = 'search("'+description+'")'
                    link = link.replace("#dt_id#", search)
                    response = requests.get(link)
                    if response and int(response.status_code) == 200:
                        rep = response.json()
                        if "total_count" in rep:
                            if rep["total_count"] > 1:
                                value = 0
    return value

def md11_3(request, current_portal, dataset_id):
    value = 100
    more_details = current_portal["system_more_details"]
    portal_link = current_portal["more_details"]["link"]
    link = portal_link + more_details["suffix"] + more_details["search_dt"]
    search = 'search("'+dataset_id+'")'
    link = link.replace("#dt_id#", search)
    response = requests.get(link)
    if response and int(response.status_code) == 200:
        rep = response.json()
        if "total_count" in rep:
            if rep["total_count"] > 1:
                value = 0
    return value

def dt(request, dataset_id,fields_to_include, regenerate=1):
    save_path = settings.MEDIA_ROOT+"/"+str(dataset_id)+".csv"
    if not os.path.isfile(save_path):
        dtall = {}
        dtall["dt1_1"] = 0
        dtall["dt1_2"] = 0
        dtall["dt2_1"] = 0 
        dtall["info_dt2_1"] = {}
        dtall["dt3_1"] = 0
        return dtall
    
    df = pd.read_csv(save_path, sep=settings.DEFAULT_SEPERATOR, encoding='utf8')
    table_full = df[fields_to_include]
    nb_rows = table_full.shape[0]
    nb_columns = table_full.shape[1]
    nb_cells = nb_rows*nb_columns

    nb_unique_rows = custom_len(table_full.drop_duplicates())
    dt31 = 0
    if nb_rows != 0:
        dt31 = (nb_unique_rows/nb_rows)*100
    
    dt11 = 0
    nb_incomplete_cells = np.count_nonzero(table_full.isnull())
    if nb_cells > 0:
        dt11 = (1 - float(nb_incomplete_cells)/float(nb_cells))*100.0

    #count number of empty rows
    dt12 = 0
    nb_incomplete_rows = np.count_nonzero(table_full.isnull().any(axis=1))
    if nb_rows > 0:
        dt12 = (1 - float(nb_incomplete_rows)/float(nb_rows))*100.0
    
    dtall = {}
    dtall["dt1_1"] = dt11
    dtall["dt1_2"] = dt12
    dtall["dt2_1"] = 0 
    dtall["info_dt2_1"] = {}
    dtall["dt3_1"] = dt31
    if regenerate==1:
        data_quality = data_quality_dataset(save_path, nb_rows)
        if "error" not in data_quality:
            dtall["info_dt2_1"] = data_quality["accuracy"]
    else:
        dtall["info_dt2_1"] = request.session["quality"]["info_dt2_1"]
    nbcol = 0
    
    for f in fields_to_include:
        if f in dtall["info_dt2_1"]:
            nbcol += 1
            dtall["dt2_1"] += dtall["info_dt2_1"][f]
    if nbcol == 0:
        dtall["dt2_1"] = 0
    else:
        dtall["dt2_1"] = dtall["dt2_1"]/float(nbcol)
    return dtall

def test(request):
    count = 0
    # Opening JSON file
    """save_path = settings.MEDIA_ROOT+"/limites-provinciales-de-castilla-y-leon-recintos@jcyl.json"
    f = open(save_path)
    file_json = json.load(f)
    file = file_json["dataset"]
    fields_to_include = []
    md11 = md1_1(request, file, fields_to_include)
    md21 = md2_1(request, file)
    md22 = md2_2(request, file)
    response = JsonResponse({"md1_1":md11, "md2_1":md21,"md2_2":md22}, safe=False)"""
    url = "https://data.namur.be/api/explore/v2.1/catalog/datasets/covid19be_cases_muni_cum/exports/xlsx?lang=fr&timezone=Europe%2FBrussels&use_labels=true"
    info = get_info_url(url)
    #info = dt(request,"limites-provinciales-de-castilla-y-leon-recintos@jcyl", ["geo_point_2d","geo_shape"])
    #info = get_weights()
    response = JsonResponse(info, safe=False)
    return response

def download_json(url_dict, save_path):
    if "http" in url_dict:
        req = requests.get(url_dict)
        if req and int(req.status_code) == 200:
            content = req.content
    else:
        content = url_dict
    if content:
        content = json.dumps(content, indent=4)
        file = open(save_path, 'w')
        file.write(content)
        file.close()
        return {"success":True, "message":""}
    return {"success":False, "message":"Unable to download the metadata information"}

def download_other_file(url, save_path):
    req = requests.get(url)
    if req and int(req.status_code) == 200:
        content = req.content
    if content:
        file = open(save_path, 'w')
        file.write(content)
        file.close()
        return 1
    return -1

#Get delimiter of csv file
def detectDelimiter(header, can=False):
    if header.find(";") != -1:
        return ";"
    if header.find(",") != -1:
        return ","
    if can:
        return ""
    #default delimiter (MS Office export)
    return ";"

#Check if the link is downloadable
def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'zip' in content_type.lower():
        return {"success":False, "message":"The extension of the dataset is not supported"}
    elif 'html' in content_type.lower():
        return {"success":False, "message":"The extension of the dataset is not supported"}
    content_length = header.get('content-length', 0)
    content_length = int(content_length)
    if content_length and content_length > settings.MAX_UPLOAD_FILE:  # 200 mb approx
        return {"success":False, "message":"The file size is greater than 200Mo"}
    return {"success":True, "message":""}

#convert xls, json, xlsx to csv with ;
def convert_file_to_csv(dataset_id, file_link, file_ext):
    file_ext = "."+file_ext
    rep_d = is_downloadable(file_link)
    if not rep_d["success"]:
        return rep_d
    r = requests.get(file_link, allow_redirects=True)
    content = r.content
    if not content or content is None:
        return {"success":False, "message":"Unable to retrieve the data content"}
    try:
        file_link = io.StringIO(content.decode('utf-8'))
        if (file_ext).lower() == ".csv":
            for header in file_link.getvalue().split('\n'):
                separator=detectDelimiter(header)
                break
            df = pd.read_csv(file_link, sep=separator, encoding='utf8')
        elif (file_ext).lower() == ".json":
            df = pd.read_json(file_link, encoding='utf8')
        elif (file_ext).lower() == ".xls" or (file_ext).lower() == ".xlsx":
            df = pd.read_excel(file_link, 0)
        save_path = settings.MEDIA_ROOT+"/"+str(dataset_id)+".csv"
        df.to_csv(save_path,sep=settings.DEFAULT_SEPERATOR, index=None)
        return {"success":True, "message":""}
    except Exception as e:
        print('Error details: '+ str(e))
        return {"success":False, "message":"Unable to retrieve the data content"}

#Download metadata info
def explore_dataset_ods(request, current_portal, dataset_id):
    dataset = {}
    more_details = current_portal["system_more_details"]
    portal_link = current_portal["more_details"]["link"]
    link = portal_link + more_details["suffix"] + more_details["explore_dt"]
    link = link.replace("#dt_id#", str(dataset_id))
    #print(link)
    rep_d = {"success":False, "message":"The information on the dataset seems to be incorrect"}
    response = requests.get(link)
    if response and int(response.status_code) == 200:
        dataset = response.json()
        save_path = settings.MEDIA_ROOT+"/"+str(dataset_id)+".json"
        rep_d = download_json(dataset, save_path)
    if not rep_d["success"]:
        return rep_d
    else:
        return {"success":True, "message":"", "dataset":dataset}

#download data content
def export_dataset_ods(request, current_portal, dataset_id):
    select_format = ""
    more_details = current_portal["system_more_details"]
    portal_link = current_portal["more_details"]["link"]
    link = portal_link + more_details["suffix"] + more_details["export_dt"]
    link = link.replace("#dt_id#", str(dataset_id))
    init_link = link
    rep_d = {"success":False, "message":"Unable to retrieve the data content"}

    for fmt in settings.DATASET_EXTENSIONS:
        select_format = fmt
        link = init_link.replace("#format#", str(fmt))
        request.session["dataset_link"] = link
        response = requests.get(link)
        if response and int(response.status_code) == 200:
            request.session["select_format"] = select_format
            rep_d = convert_file_to_csv(dataset_id, link, select_format)
            break
    return rep_d

#return all the supported portals to frontend
def portals(request):
    try:
        if "portals" not in request.session:
            portals = get_portals(request)
        else:
            portals = request.session["portals"]
        response = JsonResponse(portals, safe=False)
    except Exception as e:
        print('Error details: '+ str(e))
        response = JsonResponse({'message':"Unable to retrieve list of portals."}, status=500)
    return response

#get all the supported portals
def get_portals(request):
    obj_portals = PlatformPortal.objects.select_related('system').filter(active__exact=True).order_by('sequence')
    portals = []
    for obj in obj_portals:
        portals.append({"id":obj.pk, "sequence":obj.sequence, "name": obj.name, "more_details": obj.more_details, 
        "system":obj.system.pk, "system_name":obj.system.name.lower(), "system_more_details":obj.system.more_details})
    request.session["portals"] = portals
    #print(settings.MEDIA_ROOT)
    return portals

#calculate the data quality
@csrf_exempt
def dataquality(request):
    dataset = {}
    columns = {}
    quality = {}
    weights = {}
    initDt = 1
    metadata_dimensions = settings.SETTINGS_METADATA_DIMENSIONS
    data_dimensions = settings.SETTINGS_DATA_DIMENSIONS
    #try:
    if request.method == 'POST':
        dataset_id = request.POST.get('dataset')
        portal_id = int(request.POST.get('portal'))

        if "columns" in request.POST:
            initDt = 0
            columns = json.loads(request.POST["columns"])
            metadata_dimensions = json.loads(request.POST["metadata_dimensions"])
            data_dimensions = json.loads(request.POST["data_dimensions"])
        
        session_json_path = settings.MEDIA_ROOT+"/"+str(dataset_id)+"_session.json"
        
        if os.path.isfile(session_json_path):
            f = open(session_json_path)
            sessions = json.load(f)
            #print(sessions)
            for k,v in sessions.items():
                print(k)
                request.session[k] = v
            
    #if True:
    #    dataset_id = "limites-provinciales-de-castilla-y-leon-recintos@jcyl"
    #    portal_id = 1
        if "portals" not in request.session:
            portals = get_portals(request)
        if dataset_id and portal_id:
            #print(dataset_id,portal_id)
            current_portal = [portal for portal in request.session["portals"] if int(portal["id"]) == portal_id][0]
            if "ods" in current_portal["system_name"]:
                rep_d = {}
                if initDt == 1 and not os.path.isfile(session_json_path):
                    rep_d = explore_dataset_ods(request, current_portal, dataset_id)
                    rep_e = export_dataset_ods(request, current_portal, dataset_id)
                else:
                    rep_d["success"] = True
                    dataset = request.session["dataset"]
                    dataset_id = request.session["dataset_id"]

                if rep_d["success"]:
                    fields_to_include = []
                    if initDt == 1 and not os.path.isfile(session_json_path):
                        dataset = rep_d["dataset"]
                        
                    if initDt == 1:
                        columns = dataset["dataset"]["fields"]
                        index = 0
                        for col in columns:
                            fields_to_include.append(col["name"])
                            columns[index]["checked"] = True
                            index += 1
                    else:
                        for col in columns:
                            if col["checked"]:
                                fields_to_include.append(col["name"])

                    if os.path.isfile(session_json_path):
                        quality = request.session["quality"]


                    request.session["dataset"] = dataset
                    request.session["dataset_id"] = dataset_id
                    request.session["portal"] = current_portal
                    
                    file = dataset["dataset"]

                    quality["md1_1"] = md1_1(request,file,fields_to_include)
                    if initDt == 1 and not os.path.isfile(session_json_path):
                        quality["md2_1"] = md2_1(request,file)
                        quality["md2_2"] = md2_2(request,file)
                        quality["md2_3"] = md2_3(request,file)
                        quality["md2_4"] = md2_4(request,file)
                        quality["md2_5"] = md2_5(request,file)
                        quality["md2_6"] = md2_6(request,file)
                        quality["md3_1"] = md3_1(request,current_portal, dataset_id)
                        quality["md3_2"],quality["md3_3"] = md3_2_3(request,current_portal, dataset_id)
                        quality["md4_1"] = md4_1(request,file)
                        quality["md4_2"] = md4_2(request,file)
                        quality["md4_3"] = md4_3(request,file)
                        quality["md4_4"] = md4_4(request,file)

                    dataset_link = request.session["dataset_link"]
                    file_info = get_info_url(dataset_link)
                    select_format = request.session["select_format"]

                    if initDt == 1 and not os.path.isfile(session_json_path):
                        quality["md5_1"] = md5_1(request,file_info)
                        quality["md6_1"] = md6_1(request,file_info)
                        quality["md6_2"] = md6_2(request,file)
                        quality["md6_3"] = md6_3(request,file)
                        quality["md6_4"] = md6_4(request,file)
                        quality["md7_1"] = md7_1(request,file)
                        quality["md7_2"] = md7_2(request,file)
                        quality["md7_3"] = md7_3(request,file)
                        quality["md8_1"] = md8_1(request,file_info,select_format)
                        quality["md8_2"] = md8_2(request,file_info,current_portal,dataset_id,select_format)
                        
                        quality["md10_1"] = md10_1(request,file)
                        quality["md10_2"] = md10_2(request,file)
                        quality["md11_1"] = md11_1(request,file,current_portal,dataset_id)
                        quality["md11_2"] = md11_2(request,file,current_portal)
                        quality["md11_3"] = md11_3(request,current_portal,dataset_id)
                        
                    quality["md9_1"] = md9_1(request,file,fields_to_include)
                    quality["md9_2"] = md9_2(request,file,fields_to_include)
                    dtq = dt(request,dataset_id,fields_to_include,initDt)
                    quality["dt1_1"] = dtq["dt1_1"]
                    quality["dt1_2"] = dtq["dt1_2"]
                    quality["dt2_1"] = dtq["dt2_1"]
                    quality["dt3_1"] = dtq["dt3_1"]
                    quality["info_dt2_1"] = dtq["info_dt2_1"]
                    quality["metadata"] = 0
                    quality["data"] = 0
                    quality["overall"] = 0
                    weights = get_weights(metadata_dimensions,data_dimensions)
                    total_weight_metadata = 0
                    total_weight_data = 0

                    for d in settings.SETTINGS_METADATA_DIMENSIONS:
                        quality[d["id"]] = 0
                        total_weight_metadata +=weights[d["id"]]
                        total_weight = 0
                        for m in d["metrics"]:
                            total_weight += weights[m["id"]]
                            quality[d["id"]] += quality[m["id"]]*weights[m["id"]]
                        if total_weight == 0:
                            quality[d["id"]] = 0
                        else:
                            quality[d["id"]] = quality[d["id"]]/float(total_weight)
                        quality["metadata"] += quality[d["id"]]*weights[d["id"]]

                    for d in settings.SETTINGS_DATA_DIMENSIONS:
                        quality[d["id"]] = 0
                        total_weight_data +=weights[d["id"]]
                        total_weight = 0
                        for m in d["metrics"]:
                            total_weight += weights[m["id"]]
                            quality[d["id"]] += quality[m["id"]]*weights[m["id"]]
                        if total_weight == 0:
                            quality[d["id"]] = 0
                        else:
                            quality[d["id"]] = quality[d["id"]]/float(total_weight)
                        quality["data"] += quality[d["id"]]*weights[d["id"]]
                    
                    quality["overall"] = quality["metadata"] + quality["data"]

                    if total_weight_metadata == 0:
                        quality["metadata"] = 0
                    else:
                        quality["metadata"] = quality["metadata"] / float(total_weight_metadata)

                    if total_weight_data == 0:
                        quality["data"] = 0
                    else:
                        quality["data"] = quality["data"] / float(total_weight_data)

                    if total_weight_metadata + total_weight_data == 0:
                        quality["overall"] = 0
                    else:
                        quality["overall"] = quality["overall"] / float(total_weight_metadata + total_weight_data)
                    request.session["quality"] = quality
                    #print(columns)
            elif "ckan" in current_portal["system_name"]:
                print("TODO")
            if bool(dataset):
                if initDt == 1:
                    sessions = {}
                    for k,v in request.session.items():
                        sessions[k] = v
                    session_json_path = settings.MEDIA_ROOT+"/"+str(dataset_id)+"_session.json"
                    rep_d = download_json(sessions, session_json_path)

                response = JsonResponse({"dataset":dataset,"metadata_dimensions":metadata_dimensions, 
                                        "data_dimensions":data_dimensions,"columns":columns, 
                                        "quality":quality}, safe=False)
            else:
                response = JsonResponse({'message':rep_d["message"]}, status=400)
        else:
            response = JsonResponse({'message':"The information on the dataset and portal are required"}, status=500)
    #except Exception as e:
    #    print('Error details: '+ str(e))
    #    response = JsonResponse({'message':"The information on the dataset seems to be incorrect"}, status=400)
    return response