# -*- coding: utf-8 -*-
# scraper.py for 26-AB-HousingDirecotry

import urllib.request
import re
import os
import csv
import sys
import ipgetter
import ipcalc
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib import robotparser
from lxml.html import fromstring, tostring
from lxml import etree


def parse_region(file_name=None):

    for i in range(1, 19):
        url = 'http://wpp01.msss.gouv.qc.ca/appl/M02/M02ListeInstall.asp?cdRss=' + str(i).zfill(2) + '&CodeTri=Mct&Install=Mct'
        download(url, 'regions/region' + str(i) + '.asp')
    print('Download Complete')


def parse_directory(output_name='output', output_type='csv', region_name=None):
    
    dir_list = [item for item in os.listdir('../input/details') if re.search('.html', item) is not None] 

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'Address', 'City', 'Postal Code', 'Province', 'Terms of Occupancy', 'Housing Type', 'Number of Units', 'Eligibility Criteria', 'Application Procedure', 'Additional Criteria', 'Minimum Rate $', 'Maximum Rate $', 'RGI Rent Rate', 'Service Package Rate', 'Unit Square Footage Minimum', 'Unit Square Footage Maximum', 'Additional Suite Information', 'Additional Suite Features', 'Additional Services', 'Additional Building Information', 'Booleans (see readme)', 'Site Contact Name', 'Site Phone', 'Site Email', 'Facebook', 'Twitter', 'Site Website', 'Site Description', 'facility_type']
    csv_writer.writerow(head_row)

    for dir in dir_list:
        csv_writer.writerow(parse_detail(dir))

    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(file_name):

    data = []
    bools = []
    csvrow = []

    tree = get_lxml_tree('../input/details/' + file_name)
    csvrow.append(tree.xpath('//h1/text()')[0]) # facility name
    
    data_source = tree.xpath('//td/text()')
    bools_source = tree.xpath('//td[contains(@class, "chk_img")]/img')
    type_src = tree.xpath('//*[@id="type_dates"]/strong/text()')[0]
    
    for source in data_source:
        data.append(source.strip())
    for source in bools_source:
        src = source.get('src')
        if (re.search('tick', src)):
            bools.append(True)
        if (re.search('cross', src)):
            bools.append(False)
    
    csvrow.append(tree.xpath('//div[@class="has-icon"][1]/span/text()')[0])
    csvrow.append(tree.xpath('//div[@class="has-icon"][1]/a[1]/text()')[0])
    
    postalcode_regex = '[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d'
    regex = re.compile(postalcode_regex)
    postalcode_source = tree.xpath('//div[@class="item-next-to-content"][1]/span/text()')[0]

    postalcode = regex.findall(postalcode_source)
    postalcode = postalcode[0].upper() if len(postalcode) != 0 else ''
    csvrow.append(postalcode)
    csvrow.append('AB') # province

    offset = 0
    if data[4] is not '':
        offset -= 2

    for i in [6, 8, 10, 12, 15, 22, 32, 34, 38, 40, 43, 45, 48, 56, 66, 76]:
        csvrow.append(data[i+offset].replace('\uf0fc', '').replace('\uf0a7', '').replace('\u25e6', '').replace('\u25fe', '').replace('\u2713', ''))

    # bools
    csvrow.append(bools)

    contact_source = tree.xpath('//div[@id="listing_attributes"]/table[7]//td[contains(@class, "detail_value")]')
    for source in contact_source:
        csvrow.append(source.xpath('string()').strip()) # contact details

    descriptions = ''.join(tree.xpath('//div[@id="custom_fields"]//text()')).strip().replace('\u2033', '').replace('\uf0b7', '').replace('\n', ', ').replace('\r', '')
    csvrow.append(descriptions)
   
    csvrow.append(type_src)

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

    dir_list = [item for item in os.listdir('../input/pages/') if re.search('.html', item) is not None] 

    for dir in dir_list:
        
        tree = get_lxml_tree('../input/pages/' + dir)
        facility_urls = tree.xpath('//div[contains(@class, "info")]/div/a[1]')
        
        for facility_url in facility_urls:
            facility_url = facility_url.get('href')
            facility_id = facility_url.split('=')[2]
            file_path = "details/" + facility_id + '.html'
            download(facility_url, file_path)
   
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
