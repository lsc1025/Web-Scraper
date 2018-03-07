# -*- coding: utf-8 -*-
# scraper.py for 28-AB-ContinuningAndLongtermCare
import urllib.request
import re
import os
import csv
import sys
import ipgetter
import ipcalc
import json
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib import robotparser
from lxml.html import fromstring, tostring
from lxml import etree


def parse_region(file_name=None):

    dir_list = [item for item in os.listdir('../input/pages') if re.search('.json', item) is not None] 

    for dir in dir_list:
        f = open('../input/pages/' + dir, 'rb')
        data = json.load(f)
        f.close()
        key = list(data[12])[0]
        result_rows = data[12][key]['ResultTables'][0]['ResultRows']
        for row in result_rows:
            facility_id = row['Path'].split('=')[1]
            download(row['Path'], '../input/details/' + row['TitleForWP'] + '_' + facility_id + '.html')

    print('Download complete')


def parse_directory(output_name='output', output_type='csv', region_name=None):
    
    dir_list = [item for item in os.listdir('../input/details') if re.search('.html', item) is not None] 

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'Address', 'City', 'Postal Code', 'Province', 'Contact Phone', 'Fax', 'Accessibility', 'Service hours', 'Eligibility', 'facility_type']
    csv_writer.writerow(head_row)

    for dir in dir_list:
        csv_writer.writerow(parse_detail(dir))

    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(file_name):

    data = []
    csvrow = []
    print(file_name)
    tree = get_lxml_tree('../input/details/' + file_name)
    csvrow.append(tree.xpath('//h1/text()')[0]) # facility name
    data_source = tree.xpath('//div[contains(@class, "itemrow")]')
    service_src = tree.xpath('//div')
    
    type_src = tree.xpath('//*[@id="mainServicesProvidedContent"]/div/div[1]/h3/a/span/text()')
    type = ''
    for item in type_src:
        type += item + '; '

    type = type[:-2]

    content = {}
    for source in data_source:
        key = source.xpath('./h4/text()')[0]
        data = source.xpath('./p/text()')
        if key not in content:
            content[key] = data

    for row in content['Address']:
        csvrow.append(row.strip())

    csvrow[2] = csvrow[2][:-8]
    csvrow.append('AB')
    if len(content['Telephone']) > 0:
        csvrow.append(content['Telephone'][0])
    else:
        csvrow.append('')
    if 'Fax' in content:
        csvrow.append(content['Fax'][0])
    else:
        csvrow.append('')

    acc_string = ''
    if 'Accessibility' in content:
        for item in content['Accessibility']:
            acc_string += item.strip()
            acc_string += '; '
        csvrow.append(acc_string[:-2])
    else:
        csvrow.append('')

    svc_hr = ''
    if 'Service hours' in content:
        for item in content['Service hours']:
            svc_hr += item.strip()
            acc_string += '; '
        csvrow.append(svc_hr[:-2])
    else:
        csvrow.append('')

    if len(content['Eligibility']) > 0:
        csvrow.append(content['Eligibility'][0])
    else:
        csvrow.append('')

    csvrow.append(type)

    return csvrow

def download_regions():

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    for i in range(1, 27):
        url = 'http://housingdirectory.ascha.com/index.php?page=search&CSRFName=CSRF1980565384_1894942497&CSRFToken=c1bb4f3373a7bc12882121bbd34058f2b2039909dd0bdf7b49fd02c150ae1c75a2941a35dbd22b933bb299203d70d426840b2eb3407ebc80df5b4fc9deae643d&sOrder=dt_mod_date&iOrderType=desc&sCategory=98,97,96&sShowAs=list&iPage=' + str(i)
        download(url, 'pages/page' + str(i) + '.html')
        
    print('Download complete')
    return None

def download_details(file_name=None):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    dir_list = [item for item in os.listdir('../input/pages') if re.search('.json', item) is not None] 

    for dir in dir_list:
        f = open('../input/pages/' + dir, 'rb')
        data = json.load(f)
        f.close()
        key = list(data[12])[0]
        result_rows = data[12][key]['ResultTables'][0]['ResultRows']
        for row in result_rows:
            facility_id = row['Path'].split('=')[1]
            facility_name = row['TitleForWP'].replace('?', '').replace('/', '')
            download(row['Path'], '../input/details/' + facility_name + '_' + facility_id + '.html')
   
    print('Download complete')

def download(url, file_name='index', num_retries=3, user_agent='wswp', percent=""):

    if (os.path.isfile("../input/" + file_name)):
        print("File already exists, skipping:", file_name)
        return None

    # Parsing robots.txt
    rp = robotparser.RobotFileParser()
    rp.set_url('http://housingdirectory.ascha.com/robots.txt')
    rp.read()

    # begin of downloading
    print(percent + 'Downloading:', url)
    if rp.can_fetch(user_agent, url):
        request = urllib.request.Request(url)
        request.add_header('User-agent', user_agent)
        try:
            binary = urllib.request.urlopen(url).read()
        except (URLError, HTTPError, ContentTooShortError) as e:
            print('Download error:', e.reason)
            binary = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                # recursively retry 5xx HTTP errors
                    download(url, num_retries - 1)

    # Output to binary file
    f = open("../input/" + file_name, "wb+")
    f.write(binary)
    f.close()
    print('File saved: ' + file_name)

def ip_check():
    #return True
    print('Checking IP address...')
    myip = ipgetter.myip()
    print('Running script from:', myip)
    if myip in ipcalc.Network('192.0.163.0/24'): # using netmask /24 for Teksavvy
        return False
    return True
    

def get_lxml_tree(dir):

    f = open(dir, 'rb')
    binary = f.read()
    f.close()
    return fromstring(binary)

def print_list(columns):
    if columns is None:
        print('List is empty!')
    i = 0
    for col in columns:
        print(i)
        print(col)
        i += 1
