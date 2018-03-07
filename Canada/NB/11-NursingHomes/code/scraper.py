# -*- coding: utf-8 -*-
# scraper.py for 11-NB-NursingHomes

import urllib.request
import re
import os
import csv
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib import robotparser
from lxml.html import fromstring, tostring
from lxml import etree


def parse_region(file_name=None):

    for i in range(1, 9):
        url = 'http://www2.gnb.ca/content/gnb/en/departments/social_development/nursinghomes/content/region' + str(i) + '.html'
        download(url, 'regions/region' + str(i) + '.html')


def parse_directory(output_name='output', output_type='csv', region_name=None):

    if region_name is None: # if no region name specified, parse all region
        dir_list = [item for item in os.listdir('../input/regions') if re.search('.html', item) is not None] 
    else:
        dir_list = [region_name]

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    for dir in dir_list:
        tree = get_lxml_tree('../input/regions/' + dir)
        rows = tree.xpath('//li/a')
        for row in rows:
            facility_url = row.get('href')
            if (facility_url is None):
                continue
            if (re.search('nursinghomes', facility_url) is None):
                continue

            facility_url = 'http://www2.gnb.ca' + facility_url            
            facility_name = facility_url.split('/')[11]
            facility_name = facility_name.split('.')[0]

            details = parse_detail(facility_name + '_' + dir)
            
            csv_writer.writerow(details)
    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(facility_name):

    row = []
    tree = get_lxml_tree("../input/details/" + facility_name)
    name = tree.xpath('//h1')
    row.append(name[0].text) # facility name
    region = tree.xpath('//a[contains(@href, "region")]')[2].xpath("string()").split('-')[1][1:]
    row.append(region) # region
    
    # parsing details
    details = tree.xpath('//div[contains(@class, "text")]/p[text()]')
    for d in details:
        text = d.xpath("string()").replace('\xa0', '').lstrip()
        if len(text) < 2:
            continue
        row.append(text)
   
    csvrow = row[:2] # copy facility name & region

    # parsing address
    address = row[2].split('\n')
    address = [line.strip() for line in address if line.strip()] # remove empty string item in the list
    csvrow.append(address[0].replace(',', '')) # address line 1
    if (len(address) > 3): # looking for address line 2
        csvrow.append(address[1].replace(',', '')) # address line 2
        csvrow.append(address[2].split(',')[0]) # city
        csvrow.append('NB') # hard code for province
        csvrow.append(address[3]) # postal code
    else:      
        csvrow.append("") # placeholder for address line 2
        csvrow.append(address[1].split(',')[0]) # city
        csvrow.append('NB') # hard code for province
        csvrow.append(address[2]) # postal code

    #parsing phone number
    phone = row[3].split('\n')
    phone = [i for i in phone if i] # remove empty string
    csvrow.append(phone[0].split(':')[1].strip()) # primary phone
    if len(phone) > 1: # looking
        csvrow.append(phone[1].lstrip()) # looking for secondary phone
    else:
        csvrow.append("") # add placeholder for secondary phone
     
    csvrow.append(row[4].split(':')[1].strip()) # parsing fax
    csvrow.append(row[5].split(':')[1].strip()) # parsing language
    csvrow.append(re.findall('\\d+', row[6])[0]) # space

    return csvrow

def download_details(file_name=None):

    if file_name is None: # if no file name specified, parse all directories
        dir_list = [item for item in os.listdir('../input/regions') if re.search('.html', item) is not None] 
    else:
        dir_list = [file_name]

    for dir in dir_list:
        tree = get_lxml_tree('../input/regions/' + dir)
        rows = tree.xpath('//li/a')
        for row in rows:
            facility_url = row.get('href')
            if (facility_url is None):
                continue
            if (re.search('nursinghomes', facility_url) is None):
                continue

            facility_url = 'http://www2.gnb.ca' + facility_url            
            facility_name = facility_url.split('/')[11]
            facility_name = facility_name.split('.')[0]
            print(facility_name)
            facility_name = facility_name.replace('"', '') # escape characters to meet NTFS file name requirements
            facility_name = facility_name.replace('/', '')
            download(facility_url, "details/" + facility_name + '_' + dir)
        
    print('Download complete')
    

def download(url, file_name='index', num_retries=3, user_agent='wswp'):

    # Parsing robots.txt
    rp = robotparser.RobotFileParser()
    rp.set_url('http://www2.gnb.ca/robots.txt')
    rp.read()

    # begin of downloading
    print('Downloading:', url)
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

def get_lxml_tree(dir):

    f = open(dir, 'rb')
    binary = f.read()
    f.close()
    return fromstring(binary)
