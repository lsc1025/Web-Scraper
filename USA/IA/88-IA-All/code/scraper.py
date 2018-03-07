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
import googlemaps
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib import robotparser
from lxml.html import fromstring, tostring
from lxml import etree


def parse_directory(output_name='output', output_type='csv', file_name=None, overwrite=True):
    
    dir_list = [item for item in os.listdir('../input/details') if re.search('.html', item) is not None] if file_name is None else [file_name]

    output_fname = output_name + '.' + output_type

    if overwrite:
        csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
        csv_writer = csv.writer(csv_f, lineterminator='\n')
        head_row = ['Facility Name', 'Facility Type', 'Address1', 'Address2', 'City', 'Zip', 'State', 'Country', 'County', 'Phone']
        csv_writer.writerow(head_row)
        last_row = ''
    else:
        csv_f = open("../output/" + output_fname, "r")
        last_row = list(csv.reader(csv_f))
        csv_f = open("../output/" + output_fname, "a")
        csv_writer = csv.writer(csv_f, lineterminator='\n')
        last_row = last_row[len(last_row)-1][0]

    for dir in dir_list:
        print(dir)

        csv_writer.writerow(parse_detail(dir))
        
    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(file_name):

    data = []
    csvrow = []
    tree = get_lxml_tree('../input/details/' + file_name)

    address_src = tree.xpath('//*[@id="aspnetForm"]/div[4]/div/div/div[4]/div/div[2]/p[1]/text()')
    address = parse_address(','.join(address_src) + ',US')
    county_src = tree.xpath('//*[@id="ctl00_cphContentInside_pcounty"]/text()')
    phone_src = tree.xpath('//*[@id="ctl00_cphContentInside_pphone"]/text()')

    csvrow.append(tree.xpath('//h1/text()')[0])
    csvrow.append(get_type_by_id(int(file_name.split('_')[0])))
    csvrow += list(address.values())
    csvrow.append(county_src[0][8:] if len(county_src) > 0 else '')
    csvrow.append(parse_phone(phone_src[0]) if len(phone_src) > 0 else '')
    
    return csvrow

def download_pages(facility_type=0, file_name=None):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    url = 'http://www.iowahealthcare.org/aspx/facilitySearch.aspx'

    hb_scraper = HBScraper()

    f = open('../input/pages/' + str(facility_type) + '_page1.html', 'w+')
    f.write(hb_scraper.open_page(url, facility_type))
    f.close()

    page = 2
    next_page = hb_scraper.next_page(page)
    while next_page != None:
        file_name = str(facility_type) + '_page'+ str(page) + '.html'
        f = open('../input/pages/' + file_name, 'w+')
        f.write(next_page)
        f.close()
        print('File saved:', file_name)
        page += 1
        next_page = hb_scraper.next_page(page)

    print('Download complete')

def download_details(file_name=None):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    dir_list = [item for item in os.listdir('../input/pages') if re.search('.html', item) is not None] if file_name is None else [file_name]
    urls = []

    i = 0
    for dir in dir_list:
        facility_type = dir.split('_')[0]
        tree = get_lxml_tree('../input/pages/' + dir)
        src = tree.xpath('//a[contains(@href, "OrganizationId")]')

        for item in src:
            facility_url = 'http://www.iowahealthcare.org' + item.get('href')
            facility_id = facility_url.split('=')[1]
            urls.append(facility_url + '$' + str(facility_type))

            #download(facility_url, '../input/details/' + facility_type + '_' + facility_id + '.html', percent = "{:.1%} ".format(i/640))
            i += 1

    pool = multiprocessing.Pool(processes = 10)
    pool.map(worker, urls)

    print('Download complete')

def worker(url):
        facility_type = url.split('$')[1]
        facility_url = url.split('$')[0]
        facility_id = facility_url.split('=')[1]
        download(facility_url, '../input/details/' + facility_type + '_' + facility_id + '.html')

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

class HBScraper():

    def __init__(self):
        self.web_driver = webdriver.PhantomJS(desired_capabilities=dict(DesiredCapabilities.PHANTOMJS))
        self.web_driver.set_window_size(960, 540)
        self.web_driver.set_page_load_timeout(60)
        self.web_driver.set_script_timeout(60)
        self.web_driver.delete_all_cookies()

    def open_page(self, page_url, facility_type=0):
        try:
            self.web_driver.get(page_url)
            select = self.web_driver.find_element_by_id("ctl00_cphContentInside_drpFacilityType")
            allOptions = select.find_elements_by_tag_name("option")
            for option in allOptions:
                if option.get_attribute("value") == str(facility_type):
                    print('Selecting type:', facility_type)
                    option.click()
            self.web_driver.find_element_by_id("ctl00_cphContentInside_btnSearch").click()
        except:
            return None
        return self.web_driver.page_source

    def next_page(self, index):
        try:
            self.web_driver.find_element_by_xpath('//a[contains(@href, "Page$' + str(index) + '")]').click()
        except:
            return None
        return self.web_driver.page_source

def parse_list(source):
    escape_char = {
        '\r\n': '',
        '\xa0': ' ',
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

def get_type_by_id(id):
    mapping = {
        1: 'Nursing Facility',
        2: 'Assisted Living',
        3: 'Home Health',
        4: 'Senior Apartments',
    }
    return mapping.get(id)

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

def parse_phone(source):
    digits = re.findall('\d', source)
    if len(digits) < 10:
        return ''
    elif len(digits) == 10:
        return '(' + ''.join(digits[0:3]) + ') ' + ''.join(digits[3:6]) + '-' + ''.join(digits[6:10])
    else:
        return '(' + ''.join(digits[0:3]) + ') ' + ''.join(digits[3:6]) + '-' + ''.join(digits[6:10]) + 'x' + ''.join(digits[10:len(digits)])


def download(url, file_name='index', num_retries=3, user_agent='wswp', percent=""):

    if (os.path.isfile("../input/" + file_name)):
        print("File already exists, skipping:", file_name)
        return None

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
