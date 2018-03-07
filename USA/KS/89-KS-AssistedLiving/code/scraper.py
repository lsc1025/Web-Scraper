# -*- coding: utf-8 -*-

import urllib.request
import re
import os
import csv
import sys
import ipgetter
import ipcalc
import json
import multiprocessing
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

def parse_directory(output_name='output', output_type='csv', file_name=None):
    
    dir_list = [item for item in os.listdir('../input/details') if re.search('.html', item) is not None] if file_name is None else [file_name]

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'Facility Type(s)', 'Address1', 'Address2', 'City', 'Zip', 'State', 'Phone', 'Fax', 'Website', 'Country']
    csv_writer.writerow(head_row)

    for dir in dir_list:

        csv_writer.writerow(parse_detail(dir))
        
    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(file_name):

    data = []
    csvrow = []
    tree = get_lxml_tree('../input/details/' + file_name)

    csvrow.append(tree.xpath('//h1/text()')[0])

    address_src = tree.xpath('//*[@id="main"]/p[1]/text()')
    contact = parse_list(tree.xpath('//p[@class="ill_directory_item_contact_info"]/span/text()'))
    if len(contact) < 2:
        contact.append('')
    facility_type_src = tree.xpath('//*[@id="main"]/div[4]/ul/li')
    facility_type = ''

    for type in facility_type_src:
        facility_type += type.xpath('./a/text()')[0] + '; '

    csvrow.append(facility_type[:-2])
    csvrow += list(parse_address(address_src[0] + ',' + address_src[1]).values())
    csvrow += contact
    website = tree.xpath('//a[@class="ill_directory_web_url"]/text()')
    csvrow.append('' if len(website) < 1 else website[0])
    csvrow.append('US')

    return csvrow

def download_details(file_name='index.html'):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    dir_list = [item for item in os.listdir('../input/pages') if re.search('.html', item) is not None] if file_name is None else [file_name]

    f = open('../input/fac.html', 'w+')
    urls = []

    i = 0
    for dir in dir_list:
        tree = get_lxml_tree('../input/' + dir)
        src = tree.xpath('//div[@id="ill_directory_list"]/div/ul/li/a')

        for item in src:
            facility_url = item.get('href')
            facility_name = item.text

            f.write('<a href=" '+ facility_url +' ">' + facility_name + '</a>')

            #download(facility_url, '../input/details/' + facility_name + '.html', percent = "{:.1%} ".format(i/len(src)))
            i += 1

    f.close()
    #pool = multiprocessing.Pool(processes = 10)
    #pool.map(worker, urls)

    print('Download complete')

def worker(url):
        facility_id = url.split('=')[1]
        download(url, '../input/details/' + facility_id + '.html')

def parse_list(source):
    escape_char = {
        '\r\n': '',

    }
    for i in range(0, len(source)):
        for key, value in escape_char.items():
            source[i] = source[i].replace(key, value)
        source[i] = source[i].strip()
    return [x for x in source if x]

def parse_address(source):

    address = {}
    postalcode_regex = '([A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d)|(\d{5}(?:[-\s]\d{4})?)'
    province_regex = '[A-Z][A-Z]'
    postalcode_re = re.compile(postalcode_regex)
    province_re = re.compile(province_regex)

    address_src = source.split(',')[0:2] if len(source.split(',')) > 3 else [source.split(',')[0], '']
    region_src = source.split(',')[-2:]
    postalcode = postalcode_re.findall(region_src[1])
    province = province_re.findall(region_src[1])
    if province:
        province = province[0]
    else:
        province = ''
    if postalcode:
        if (len(postalcode) > 1):
            postalcode = postalcode[1][0]
        else:
            postalcode = postalcode[0][0] if postalcode[0][1] == '' else postalcode[0][1]
    else:
        postalcode = ''
    address['line1'] = address_src[0]
    address['line2'] = '' if len(address_src) < 2 else address_src[1]
    address['city'] = region_src[0].strip()
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

def download(url, file_name='index', num_retries=3, user_agent='wswp', percent=""):

    if (os.path.isfile("../input/" + file_name)):
        print("File already exists, skipping:", file_name)
        #return None

    # Parsing robots.txt
    rp = robotparser.RobotFileParser()
    rp.set_url('https://www.khca.org/robots.txt')
    rp.read()

    # begin of downloading
    print(percent + 'Downloading:', url)
    #if rp.can_fetch(user_agent, url):
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
