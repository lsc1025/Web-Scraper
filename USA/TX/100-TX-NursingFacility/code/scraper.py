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

def parse_pdf(output_name='output', output_type='csv', file_name='nf.html'):

    dir_list = [item for item in os.listdir('../input') if re.search('.html', item) is not None] if file_name is None else [file_name]

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'Facility ID', 'License Exp.', 'Facility Type', 'Address1', 'Address2', 'City', 'State', 'Zip', 'Owner', 'Owner Address1', 'Owner Address2', 'Owner City', 'Owner State', 'Owner Zip', 'Facility Phone', 'Facility Fax', 'Owner Phone', 'Owner Fax', 'Capacity', 'Country',]
    csv_writer.writerow(head_row)

    for dir in dir_list:
        print(dir)
        csvrows = []
        tree = get_lxml_tree('../input/' + dir)

        src = tree.xpath('//tr[@valign="bottom"]/td/font/text()')

        i = 0
        while (i < len(src)):

            for k in range(0, 6):
                csvrow = []

                if i + 49 > len(src):
                    break

                if re.findall('\d', src[i+12]) == []:
                    src[i+11] += '\r\n ' + src[i+12]
                    del src[i+12]
                if re.findall('\d', src[i+13]) == []:
                    src[i+12] += '\r\n ' + src[i+13]
                    del src[i+13]
                if re.search(',', src[i+14]): # found addr line 2
                    src[i+13] += src[i+14]
                    del src[i+14]
                if re.search('Fax', src[i+22]) is None:
                    src.insert(i+21, '')
                if re.search('PHONE', src[i+24]) is None:
                    src.insert(i+23, '')
                if re.search('FAX', src[i+25]):
                    src.insert(i+25, '')
                if re.search('Capacity', src[i+28]) is None:
                    src.insert(i+27, '')
                if re.search('/', src[i+47]) is None:
                    src.insert(i+47, '')

                csvrow.append(src[i+10])
                csvrow.append(src[i+8])
                csvrow.append(src[i+47])
                csvrow.append(src[i+39])
                csvrow += list(parse_address(src[i+12]).values())
                csvrow += (src[i+14:i+17])    
                csvrow.append(src[i+11])
                csvrow += list(parse_address(src[i+13]).values())
                csvrow += (src[i+17:i+20])

                for j in range(21, 30, 2):
                    csvrow.append(src[i+j])
                csvrow.append('US')
                
                csv_writer.writerow(parse_list(csvrow))

                i += 48

            i += 2

        csv_writer.writerows(csvrows)   

    csv_f.close()
    print('Output file saved: ' + output_fname)


def download_details(file_name=None):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    dir_list = [item for item in os.listdir('../input/pages') if re.search('.html', item) is not None] if file_name is None else [file_name]

    i = 0
    for dir in dir_list:
        tree = get_lxml_tree('../input/pages/' + dir)
        facility_name = tree.xpath('//h1/text()')[1].replace('/', ' ').strip()
        facility_id = dir.split('.')[0]
        facility_url = 'https://profiles.health.ny.gov/nursing_home/tab_overview/' + facility_id
        download(facility_url, '../input/details/' + facility_name + '_' + facility_id + '.html', percent = "{:.1%} ".format(i/len(dir_list)))
        print(facility_name)
        continue
        for url in urls:
            facility_id = url.split('/')[5]
            facility_url = 'https://profiles.health.ny.gov/nursing_home/view/' + facility_id
            
            i+=1
   
    print('Download complete')


def insert_into_list(index, content, item):

    temp = content[index:len(content)]
    return content[0:index] + item + temp


def parse_list(source):
    escape_char = {
        '\r\n ': '',

    }
    for i in range(0, len(source)):
        for key, value in escape_char.items():
            source[i] = source[i].replace(key, value)
        source[i] = source[i].strip()
    #return [x for x in source if x]
    return source

def parse_address(source):

    address = {}
    postalcode_regex = '([A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d)|(\d{5}(?:[-\s]\d{4})?)'
    province_regex = '[A-Z][A-Z]'
    postalcode_re = re.compile(postalcode_regex)
    province_re = re.compile(province_regex)
    address_src = source.split(',')
    region_src = []
    if len(region_src) < 2:
        region_src = ['', '']
    postalcode = postalcode_re.findall(region_src[1])
    if postalcode:
        if (len(postalcode) > 1):
            postalcode = postalcode[1][0]
        else:
            postalcode = postalcode[0][0] if postalcode[0][1] == '' else postalcode[0][1]
    else:
        postalcode = ''
    province = province_re.findall(region_src[1])
    if province:
        province = province[0]
    else:
        province = ''
    address['line1'] = address_src[0].strip()
    address['line2'] = address_src[1].strip() if len(address_src) > 1 else ''
    #address['city'] = region_src[0].strip()
    #address['postalcode'] = postalcode
    #address['province'] = province

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
    return True
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

def print_list(columns, limit=9999):
    if columns is []:
        print('List is empty!')
    i = 0
    for col in columns:
        print(i)
        print(col)
        i += 1
        if i > limit:
            break
