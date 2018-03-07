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

    head_row = ['Facility Name', 'Type', 'Address', 'City', 'Province', 'Postal Code', 'Contact Phone', 'Link to Details']
    csv_writer.writerow(head_row)

    csvrow = []
    tree = get_lxml_tree('../input/' + 'index.html')
    facility_src = tree.xpath('//div[@class="location_details"]')
    data_src = tree.xpath('//div[@class="location_details"]/p/text()')

    for src in facility_src:
        csvrow=[]
        csvrow.append(src.xpath('./p/a/text()')[0])
        facility_url = src.xpath('./p/a')[0].get('href')
        if re.search('http', facility_url) is None:
            facility_url = 'http://www.reveraliving.com' + facility_url
        
        data = src.xpath('./p/text()')
        for i in range(0, len(data)-1):
            if data[i].strip() == '':
                del data[i]
            else:
                data[i] = data[i].strip()

        csvrow.append(data[2][1:])
        csvrow.append(data[0])
        address = parse_address(data[1])
        csvrow.append(address['city'])
        csvrow.append(address['province'])
        csvrow.append(address['postalcode'])
        csvrow.append(src.xpath('./p/strong/a/text()')[0])
        csvrow.append(facility_url)
        csv_writer.writerow(csvrow)
    
    csv_f.close()
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
    address['city'] = address_src[0].strip()
    postalcode = postalcode_re.findall(source)
    province = province_re.findall(source)
    if postalcode:
        if (len(postalcode) > 1):
            postalcode = postalcode[1][0]
        else:
            postalcode = postalcode[0][0] if postalcode[0][1] == '' else postalcode[0][1]
    else:
        postalcode = ''
    province = province[0] if province else ''
    address['postalcode'] = postalcode
    address['province'] = province
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
