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

    head_row = ['Facility Name', 'Address1', 'Address2', 'City', 'Zip', 'State', 'County', 'Contact Phone', 'Mailing Address1', 'Mailing Address2', 'Mailing City', 'Mailing Zip', 'Mailing State', 'Mailing County', 'Website', 'Space', 'Link to details', 'Country']
    csv_writer.writerow(head_row)

    for dir in dir_list:

        csv_writer.writerow(parse_detail(dir))
        
    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(file_name):

    data = []
    csvrow = []
    tree = get_lxml_tree('../input/details/' + file_name)

    csvrow.append(tree.xpath('//tr[@class="tableHeadTall"]/td/span/span/text()')[0])

    st_addr_src = parse_list(tree.xpath('//table[@id="tblAddressDetails"]//td[1]/span/text()'))
    region_src = parse_list(tree.xpath('//table[@id="tblAddressDetails"]//td[1]/div/span/text()'))
    mal_addr_src = parse_list(tree.xpath('//*[@id="ctl00_ContentPlaceHolder1_trMailingAddr"]/td/span/text()'))

    if (re.search('FL', st_addr_src[1]) is None):
        st_addr_src[0] += ', ' + st_addr_src[1]
        del st_addr_src[1]

    if len(mal_addr_src) > 2:
        mal_addr_src[0] += ', ' + mal_addr_src[1]
        del mal_addr_src[1]

    st_addr = parse_address(st_addr_src[0:2])
    mal_addr = parse_address(mal_addr_src)

    csvrow += list(st_addr.values())
    csvrow.append(region_src[3])
    csvrow.append(region_src[1])
    csvrow += list(mal_addr.values())
    csvrow.append(region_src[7])
    website_src = tree.xpath('//a[@id="ctl00_ContentPlaceHolder1_lnkFacilityWebsite"]')
    csvrow.append(website_src[0].get('href') if len(website_src) > 0 else '')
    csvrow.append(tree.xpath('//span[@id="ctl00_ContentPlaceHolder1_lblBedsCount"]/text()')[0])
    csvrow.append('http://www.floridahealthfinder.gov/FacilityLocator/FacilityProfilePage.aspx?id=' + file_name[:-5])
    csvrow.append('US')

    return csvrow

def download_details(file_name='index.html'):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    dir_list = [item for item in os.listdir('../input/pages') if re.search('.html', item) is not None] if file_name is None else [file_name]

    urls = []

    i = 0
    for dir in dir_list:
        tree = get_lxml_tree('../input/' + dir)
        src = tree.xpath('//a')

        for item in src:
            facility_id = item.get('href').split('=')[1]
            facility_url = 'http://www.floridahealthfinder.gov/FacilityLocator/FacilityProfilePage.aspx?id=' + facility_id
            urls.append(facility_url)
            
            #download(facility_url, '../input/details/' + facility_id + '.html', percent = "{:.1%} ".format(i/len(src)))
            

    pool = multiprocessing.Pool(processes = 10)
    pool.map(worker, urls)

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

    if re.search(',',source[1]) is None:
        source[0] += ', ' + source[1]
        source[1] = ','
    address = {}
    postalcode_regex = '([A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d)|(\d{5}(?:[-\s]\d{4})?)'
    province_regex = '[A-Z][A-Z]'
    postalcode_re = re.compile(postalcode_regex)
    province_re = re.compile(province_regex)
    address_src = source[0].split(',')
    region_src = source[1].split(',')
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
    address['line1'] = address_src[0].strip()
    address['line2'] = address_src[1].strip() if len(address_src) > 1 else ''
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
