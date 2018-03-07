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

def parse_rc(output_name='output', output_type='csv', file_name='rc2.pdf.html'):

    dir_list = [item for item in os.listdir('../input') if re.search('.html', item) is not None] if file_name is None else [file_name]

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'License Number', 'License Exp.', 'Business Type', 'Address', 'County', 'City', 'Zip', 'State', 'Contact Phone', 'Mailing Address', 'Administrator', 'Admin Phone', 'Mailing City', 'Mailing Zip', 'Mailing State', 'Facility Email', 'Licensee', 'Fac. Contact Email', 'Country',]
    csv_writer.writerow(head_row)

    for dir in dir_list:
        print(dir)
        csvrows = []
        tree = get_lxml_tree('../input/' + dir)

        src = tree.xpath('//span/text()')

        i = 12
        while (i < len(src)):

            for k in range(0, 4):
                print(i)
                if i + 31 > len(src):
                    break

                if (re.search('PH#', src[i+5])): # no mailing addr
                    src.insert(i+5, '')
                    src.insert(i+7, '')

                if (re.search('Alzheimer', src[i+13]) is None): # two-line licensee
                    src[i+12] = src[i+12] + ' ' + src[i+13]
                    del src[i+13]

                if(re.findall('\d', src[i+15])):
                    src.insert(i+15, '####')
                if(re.findall('\d', src[i+19])):
                    src.insert(i+19, '###')
                if(re.findall('\d', src[i+21])):
                    src.insert(i+21, '##')
                csvrow = (src[i:i+14])
                i += 31

                del csvrow[8]
                del csvrow[10]
                del csvrow[11]


                lic_info = parse_list(csvrow[1].split(' / '))
                csvrow[1] = lic_info[0]
                csvrow.insert(2, lic_info[1])
                region_info = parse_list(csvrow[4].split('/'))
                csvrow[4] = region_info[0]
                if (len(region_info) < 2):
                    region_info.append('')
                csvrow.insert(3, region_info[1])
                address = parse_address(csvrow[6])
                del csvrow[6]
                csvrow = insert_into_list(6, csvrow, list(address.values()))
                csvrow.append('US')
                admin_info = parse_list(csvrow[11].split('PH#:'))
                if len(admin_info) < 1:
                    admin_info = ['','']
                else:
                   if len(admin_info) < 2:
                        admin_info.append('')
                csvrow[11] = admin_info[0]
                csvrow.insert(12, admin_info[1])

                mailing_address = parse_address(csvrow[13])
                del csvrow[13]
                csvrow = insert_into_list(13, csvrow, list(mailing_address.values()))

                csvrow[18] = csvrow[18].strip()



                csvrows.append(csvrow)

            i += 15

        csv_writer.writerows(csvrows)   

    csv_f.close()
    print('Output file saved: ' + output_fname)


def parse_directory(output_name='output', output_type='csv', file_name='nh2.pdf.html'):
    
    dir_list = [item for item in os.listdir('../input') if re.search('.html', item) is not None] if file_name is None else [file_name]

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'License Number', 'License Exp.', 'Type', 'Address', 'County', 'City', 'Zip', 'State', 'Contact Phone', 'Mailing Address', 'Administrator', 'Admin Phone', 'Mailing City', 'Mailing Zip', 'Mailing State', 'Facility Email', 'Licensee', 'Fac. Contact Email', 'Country']
    csv_writer.writerow(head_row)

    for dir in dir_list:
        print(dir)
        csvrows = []
        tree = get_lxml_tree('../input/' + dir)

        src = tree.xpath('//span/text()')

        i = 12
        while i < len(src):
            for k in range(0, 5):
                if i + 20> len(src):
                    break
                print(i)
                if i == 4132:
                    i-= 2
                    del src[i]
                if re.findall('\d', src[i]):
                    del src[i]
                
                #if i in [1484, 2528, 2720, 2760, 3088, 3184] and re.findall('\d', src[i]):
                    #del src[i]
                if re.search('Email:', src[i +12]):
                    src[i + 10] += ' ' + src[i+11]
                    del src[i+11]
                if re.search('Yes', src[i + 13]) or re.search('No', src[i + 13]):
                    src.insert(i+13, '#')
                if re.findall('\d', src[i + 16]):
                    src.insert(i+16, '######')

                if re.search('PH#', src[i + 5]): # no mailing addr.
                    src.insert(i+5,'')
                    src.insert(i+7, '####')
                
                csvrow = src[i:i+14]
                del csvrow[8]
                del csvrow[10]
                del csvrow[11]

                lic_info = parse_list(csvrow[1].split(' / '))
                csvrow[1] = lic_info[0]
                csvrow.insert(2, lic_info[1])
                region_info = parse_list(csvrow[4].split('/'))
                csvrow[4] = region_info[0]
                if (len(region_info) < 2):
                    region_info.append('')
                csvrow.insert(3, region_info[1])
                address = parse_address(csvrow[6])
                del csvrow[6]
                csvrow = insert_into_list(6, csvrow, list(address.values()))
                csvrow.append('US')
                admin_info = parse_list(csvrow[11].split('PH#:'))
                if len(admin_info) < 1:
                    admin_info = ['','']
                else:
                   if len(admin_info) < 2:
                        admin_info.append('')
                csvrow[11] = admin_info[0]
                csvrow.insert(12, admin_info[1])

                mailing_address = parse_address(csvrow[13])
                del csvrow[13]
                csvrow = insert_into_list(13, csvrow, list(mailing_address.values()))

                csvrow[18] = csvrow[18].strip()

                csvrows.append(csvrow)

                
                i += 20
            i += 16
        csv_writer.writerows(csvrows)
        
    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(file_name):

    data = []
    csvrow = []
    tree = get_lxml_tree('../input/details/' + file_name)

    csvrow.append(file_name.split('_')[0])
    basic = parse_list(tree.xpath('//p[1]/text()'))
    csvrow += (list(parse_address(basic[0:2]).values()))
    csvrow.append('US')
    csvrow.append(basic[2])
    if (len(basic) > 3): # found website
        website = tree.xpath('//p[1]/a')[0].get('href')
    else:
        website = ''
    csvrow.append(website)
    csvrow.append('https://profiles.health.ny.gov/nursing_home/view/' + file_name[:-5].split('_')[1])

    return csvrow

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
    #address_src = source[0].split(',')
    region_src = source.split(',')
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
    #address['line1'] = address_src[0].strip()
    #address['line2'] = address_src[1].strip() if len(address_src) > 1 else ''
    address['city'] = region_src[0].strip()
    address['postalcode'] = postalcode
    address['province'] = province
    if re.search(':', region_src[1]):
        address['phone'] = region_src[1].split(':')[1]
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

def print_list(columns):
    if columns is []:
        print('List is empty!')
    i = 0
    for col in columns:
        print(i)
        print(col)
        i += 1
        if i > 5000:
            break
