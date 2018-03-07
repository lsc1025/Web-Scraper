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

def parse_directory(output_name='output', output_type='csv', file_name='index.html'):
    
    dir_list = [item for item in os.listdir('../input/details') if re.search('.html', item) is not None] if file_name is None else [file_name]

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'Address1', 'Address2', 'City', 'Postal Code', 'Province', 'Contact Phone', 'Website', 'Link to Details']
    csv_writer.writerow(head_row)

    for dir in dir_list:
        tree = get_lxml_tree('../input/' + file_name)
        src = tree.xpath('//tr[@class="ms-rteTableOddRow-5"]/td')
        src += tree.xpath('//tr[@class="ms-rteTableEvenRow-5"]/td')

        for source in src:
            csvrow = []
            data = parse_list(source.xpath('.//text()'))
            if len(data) < 2:
                continue
            if len(data) == 7:
                data[2] += ', ' + data[3]
                del data[3]

            csvrow.append(data[1])
            address = parse_address(data[2:4])
            csvrow += list(address.values())
            csvrow.append(data[4].split(':')[1].strip())
            if len(data) > 7:
                csvrow.append(source.xpath('.//a[1]')[0].get('href'))
                csvrow.append('https://www.saskatoonhealthregion.ca' + source.xpath('.//a[2]')[0].get('href'))
            else:
                csvrow.append('')
                csvrow.append('https://www.saskatoonhealthregion.ca' + source.xpath('.//a[1]')[0].get('href'))

            csv_writer.writerow(csvrow)

    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(file_name):

    data = []
    csvrow = []
    tree = get_lxml_tree('../input/details/' + file_name)
    csvrow.append(tree.xpath('//h1/text()')[0]) # facility name
    address = parse_address(tree.xpath('//div[@class="community-contact"]/address/text()'))
    csvrow += (list(address.values()))
    contact = tree.xpath('//div[@class="community-contact"]/p/a')
    for i in range(0, len(contact)):
        contact[i] = contact[i].get('href').split(':')[1]
    
    csvrow += contact
    csvrow.append('http://www.verveseniorliving.com/' + file_name.split('.')[0])

    return csvrow

def parse_list(source):
    escape_char = {
        '\r\n': '',
        '\xa0♠': '',
        '♠': ''
    }
    for i in range(0, len(source)):
        if source[i] == '':
            del source[i]
        else:
            for key, value in escape_char.items():
                source[i] = source[i].replace(key, value)
            source[i] = source[i].strip()
    return source

def parse_address(source):
    address = {}
    postalcode_regex = '([A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d)|(\d{5})'
    province_regex = '[A-Z][A-Z]'
    postalcode_re = re.compile(postalcode_regex)
    province_re = re.compile(province_regex)
    
    address_src = source[0].split(',') + source[1].split(',')
    if len(address_src) < 4:
        address_src.insert(1, '')
    postalcode = postalcode_re.findall(address_src[3])
    if postalcode:
        if (len(postalcode) > 1):
            postalcode = postalcode[1][0]
        else:
            postalcode = postalcode[0][0] if postalcode[0][1] == '' else postalcode[0][1]
    else:
        postalcode = ''
    address['line1'] = address_src[0].strip()
    address['line2'] = address_src[1].strip()
    address['city'] = address_src[2].strip()
    address['postalcode'] = postalcode
    address['province'] = province_re.findall(address_src[3])[0]
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

def download_details(file_name='index.html'):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    dir_list = [item for item in os.listdir('../input/pages') if re.search('.json', item) is not None] if file_name is None else [file_name]

    i = 0
    for dir in dir_list:
        tree = get_lxml_tree('../input/' + dir)
        urls = tree.xpath('//ul[@class="small-block-grid-2 xsmall-block-grid-1 text-left"]/li/a')

        for url in urls:
            facility_url = url.get('href')
            facility_name = facility_url.replace('/', '')
            facility_url = 'http://www.verveseniorliving.com' + facility_url
            download(facility_url, '../input/details/' + facility_name + '.html', percent = "{:.0%} ".format(i/len(urls)))
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
