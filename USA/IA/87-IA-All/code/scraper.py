# -*- coding: utf-8 -*-

import urllib.request
import re
import os
import csv
import sys
import ipgetter
import ipcalc
import json
import requests
import multiprocessing
import googlemaps
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

def parse_directory(output_name='output', output_type='csv', file_name=None, overwrite=True):
    
    dir_list = [item for item in os.listdir('../input/types') if re.search('.html', item) is not None] if file_name is None else [file_name]

    output_fname = output_name + '.' + output_type

    if overwrite:
        csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
        csv_writer = csv.writer(csv_f, lineterminator='\n')
        head_row = ['Facility Name', 'Facility Type', 'Address1', 'Address2', 'City', 'Zip', 'State', 'Country', 'Phone', 'Latitude', 'Longitude']
        csv_writer.writerow(head_row)
        last_row = ''
    else:
        csv_f = open("../output/" + output_fname, "r")
        last_row = list(csv.reader(csv_f))
        csv_f = open("../output/" + output_fname, "a")
        csv_writer = csv.writer(csv_f, lineterminator='\n')
        last_row = last_row[len(last_row)-1][0]
        print(last_row)

    gmap = GoogleMapUtil()

    for dir in dir_list:
        print(dir)
        tree = get_lxml_tree('../input/types/' + dir)
        src = parse_list(tree.xpath('//tr[contains(@class, "Row")]/td//text()'))

        i = 0
        while i + 6 < len(src):
            csvrow = []
            
            if src[i] == last_row:
                print('Resuming...')
                overwrite = True
                i += 6
                continue
            if not overwrite:
                i += 6
                continue

            csvrow.append(src[i])
            csvrow.append(src[i+1])
            
            addr_src = src[i+2].split(',')
            line1 = addr_src[0]
            line2 = addr_src[1].strip() if len(addr_src) > 1 else ''

            addr_src = line1 + ', ' + src[i+3] + ', IA'      
            print('Parsing facility:', src[i])
            address_result = gmap.get_regions(addr_src)
            address = parse_address(address_result['formatted_address'])
            address['line2'] = line2
            loc = address_result['geometry']['location']

            csvrow += list(address.values())
            csvrow.append(src[i+4])
            csvrow += list(loc.values())
            csv_writer.writerow(csvrow)
            i += 6
        
    csv_f.close()
    print('Output file saved: ' + output_fname)

def modi():

    csv_f = open("../output/output.csv", "r")
    rows = list(csv.reader(csv_f))
    csv_f.close()

    csv_fo = open("../output/output2.csv", "w+")
    csv_writer = csv.writer(csv_fo, lineterminator='\n')
    head_row = ['Facility Name', 'Facility Type', 'Address1', 'Address2', 'City', 'Zip', 'State', 'Country', 'Phone', 'Latitude', 'Longitude']
    csv_writer.writerow(head_row)
    for row in rows:
        row[3] = row[3].strip()
        row[7] = 'US'
        csv_writer.writerow(row)
    csv_fo.close()


def download_details(file_name=None):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    dir_list = [item for item in os.listdir('../input/types') if re.search('.html', item) is not None] if file_name is None else [file_name]
    urls = []

    entity_id_mapping = {
        '': '',
        }

    i = 0
    for dir in dir_list:
        tree = get_lxml_tree('../input/types/' + dir)
        src = tree.xpath('//tr/td/a')
        for item in src:
            facility_url = item.get('href')
            if re.search('openNewInfoWin', facility_url):
                continue
            facility_id = (facility_url[54:-3])
            continue          
            if facility_url is None:
                continue    
            if len(facility_url.split('/')) < 5:
                continue 
            facility_name = facility_url.split('/')[4]
            download(facility_url, '../input/details/' + facility_name + '.html', percent = "{:.1%} ".format(i/len(src)))
            i += 1

    #pool = multiprocessing.Pool(processes = 10)
    #pool.map(worker, urls)

    print('Download complete')

def worker(url):
        facility_id = url.split('=')[1]
        download(url, '../input/details/' + facility_id + '.html')

class GoogleMapUtil:

    #AIzaSyCmgHKUJyhj8DtzqwjLZXt2ubeqMoszaN0
    #AIzaSyBcxJttORSgrHUrd3BidFN_lMZYSRJDuOs
    #AIzaSyBf15pyAx0sS8n-1PEmjE3NCiTM04Rhigs

    def __init__(self, **kwargs):
        self.gmaps = googlemaps.Client(key='AIzaSyBf15pyAx0sS8n-1PEmjE3NCiTM04Rhigs')
        
    def get_regions(self, address):

        result = self.gmaps.places(query=address)['results'][0]
        #result = self.gmaps.place(place_id)['result']
        return result

def download_post(file_name, facility_id):

    if (os.path.isfile("../input/" + file_name)):
        print("File already exists, skipping:", file_name)
        #return None

    url = "https://dia-hfd.iowa.gov/DIA_HFD/CTLEntitySearch.do"
    payload = "cmd=View&selectedColumnId=" + str(facility_id) + "&closeWindow=false&parentWindow=default&searchCriteria.entityName=&searchCriteria.looseSearch=true&searchCriteria.entityAlias=&searchCriteria.category.entityTypeCategoryId=&searchCriteria.entityTypeId=17&searchCriteria.countyTypeId=15505&searchCriteria.city=&result.pageSize=500&listName=Entity&result.totalCount=32&result.currentPage=1&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17&entityTypeId=17"
    headers = {
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.8",
        'cache-control': "no-cache",
        'connection': "keep-alive",
        'content-length': "879",
        'content-type': "application/x-www-form-urlencoded",
        'cookie': "JSESSIONID=37AD556166A5B6E887FF7B4DFC81F7D7.worker1; visid_incap_953578=uYttLdUPQNOTTJB32i0kJYBgylkAAAAAQUIPAAAAAABnUHCrBjDjqpZm3RZaYFkS; incap_ses_530_953578=479DCs+W3VmHC8fhp/BaB9FqylkAAAAATnfMmXOk6g1/xOhpHWyOjQ==",
        'host': "dia-hfd.iowa.gov",
        'origin': "https://dia-hfd.iowa.gov",
        'referer': "https://dia-hfd.iowa.gov/DIA_HFD/CTLEntitySearch.do",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    if (len(response.text)) < 17000:
        print('Site down, file not saved!')
        return None

    f = open("../input/" + file_name, "w+")
    f.write(response.text)
    f.close()
    print('File saved: ' + file_name)

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

    address_src = source.split(',')[0:2] if len(source.split(',')) > 4 else [source.split(',')[0], '']
    region_src = source.split(',')[-3:]
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
    address['country'] = region_src[2]
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
