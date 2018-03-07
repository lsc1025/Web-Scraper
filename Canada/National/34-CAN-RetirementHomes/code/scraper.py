# -*- coding: utf-8 -*-

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

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'Type', 'Short Description', 'Contact Phone', 'Address', 'City', 'Province', 'Postal Code', 'Link to Details']
    csv_writer.writerow(head_row)

    csvrow = []
    tree = get_lxml_tree('../input/' + 'a1.html')
    img_src = tree.xpath('//*[@id="dnn_ctr3064_View_ListView2_groupPlaceholderContainer"]//img')
    facility_names = tree.xpath('//*[@id="dnn_ctr3064_View_ListView2_groupPlaceholderContainer"]//h2/a/text()')
    attr = tree.xpath('//*[@id="dnn_ctr3064_View_ListView2_groupPlaceholderContainer"]//span/text()')
    facility_ids = []
    facility_urls = []
    facility_types = []

    for img in img_src:
        facility_id = img.get('src').split('/')[4][:-4].replace('%20', '-').replace('%c3%a9', 'é').replace('%c3%a8', 'è').replace('%c3%a2', 'â').replace('%c3%b4', 'ô')
        facility_ids.append(facility_id)
        if re.search('Long-Term', facility_id):
            facility_urls.append('http://chartwell.com/Long-Term-Care-Homes/' + facility_id)
            facility_types.append('Long-Term Care')
        else:
            facility_urls.append('http://chartwell.com/Retirement-Homes/' + facility_id)
            facility_types.append('Retirement Home')

    i = 0
    for i in range(0, len(facility_names)):
        csvrow.append(facility_names[i])
        csvrow.append(facility_types[i])
        csvrow += attr[i*6:(i+1)*6]
        csvrow.append(facility_urls[i])
        csvrow[6] = get_province_abbr(csvrow[6])
        csv_writer.writerow(csvrow)
        csvrow = []
    
    print('Output file saved:', output_fname)

def parse_address(source):
    address = {}
    postalcode_regex = '([A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d)|(\d{5})'
    province_regex = '[A-Z][A-Z]'
    postalcode_re = re.compile(postalcode_regex)
    province_re = re.compile(province_regex)
    address_src = source.split(',')
    if (len(address_src) < 4):
        address_src.insert(1, '')
    address['line1'] = address_src[0]
    address['line2'] = address_src[1]
    address['city'] = address_src[2].strip()
    postalcode = postalcode_re.findall(source)
    if postalcode:
        if (len(postalcode) > 1):
            postalcode = postalcode[1][0]
        else:
            postalcode = postalcode[0][0] if postalcode[0][1] == '' else postalcode[0][1]
    else:
        postalcode = ''
    address['postalcode'] = postalcode
    address['province'] = 'BC'
    return address

def get_province_abbr(source):

    province_state_dict = {
        'Alberta': 'AB',
        'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'British Columbia': 'BC',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Manitoba': 'MB',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'New Brunswick': 'NB',
        'Nebraska': 'NE',
        'Newfoundland': 'NL',
        'Nova Scotia': 'NS',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Ohio': 'OH',
        'Ontario': 'ON',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Prince Edward Island': 'PE',
        'Quebec': 'QC',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Saskatchewan': 'SK',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY',
    }

    abbr = province_state_dict.get(source)
    return abbr

def download_regions():

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    for i in range(1, 27):
        url = 'http://housingdirectory.ascha.com/index.php?page=search&CSRFName=CSRF1980565384_1894942497&CSRFToken=c1bb4f3373a7bc12882121bbd34058f2b2039909dd0bdf7b49fd02c150ae1c75a2941a35dbd22b933bb299203d70d426840b2eb3407ebc80df5b4fc9deae643d&sOrder=dt_mod_date&iOrderType=desc&sCategory=98,97,96&sShowAs=list&iPage=' + str(i)
        download(url, 'pages/page' + str(i) + '.html')
        
    print('Download complete')
    return None

def download_details(file_name='1.html'):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    dir_list = [item for item in os.listdir('../input/pages') if re.search('.json', item) is not None] if file_name is None else [file_name]

    i = 0
    for dir in dir_list:
        tree = get_lxml_tree('../input/' + dir)
        urls = tree.xpath('//a')

        for url in urls:
            facility_url = url.get('href')
            facility_id = facility_url.split('=')[1]
            facility_url = 'http://www.vch.ca' + facility_url[1:]

            download(facility_url, '../input/details/' + facility_id + '.html', percent = "{:.0%} ".format(i/len(urls)))
            i+=1
   
    print('Download complete')

def download(url, file_name='index', num_retries=3, user_agent='wswp', percent=""):

    if (os.path.isfile("../input/" + file_name)):
        print("File already exists, skipping:", file_name)
        return None

    # Parsing robots.txt
    rp = robotparser.RobotFileParser()
    rp.set_url('http://www.vch.ca/robots.txt')
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
    if columns is []:
        print('List is empty!')
    i = 0
    for col in columns:
        print(i)
        print(col)
        i += 1
