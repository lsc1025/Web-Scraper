# -*- coding: utf-8 -*-
# scraper.py

import urllib.request
import re
import os
import csv
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib import robotparser
from lxml.html import fromstring, tostring


def parse_region(file_name):

    # read source file
    f = open('../input/' + file_name, 'rb')
    binary = f.read()
    f.close()
    tree = fromstring(binary) # parse binary file
    regions = tree.xpath('//script[contains(.,"jobs_table_parent")]')
    # extract urls to directories
    for region in regions:
        region_list = [item for item in region.text.split("'")]
        i = 0
        for item in region_list:
            if (re.search("gnb.ca", item) is not None):
                download(item, "regions/" + item.split("/")[6]) # download directory from all region

def parse_directory(output_name='output', output_type='csv', region_name=None):

    if region_name is None: # if no file name specified, parse all directories
        dir_list = [item for item in os.listdir('../input/regions') if re.search('.asp', item) is not None] 
    else:
        dir_list = [region_name]

    csv_f = open("../output/" + output_name + '.' + output_type, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    for dir in dir_list:
        f = open('../input/regions/' + dir, 'rb')
        binary = f.read()
        f.close()
        tree = fromstring(binary)
        rows = tree.xpath('//tr')
        for row in rows:
            if row[1].text is not None: # filter out table head
                continue
            
            facility_name = row[1].xpath('./a')[0].text
            facility_name = facility_name.replace('"', '') # escape characters to meet NTFS file name requirements
            facility_name = facility_name.replace('/', '')
            details = parse_detail(facility_name + ".html")[1]
            csvrow = []
            i = 0
            for entry in details:
                if re.search("Inspection", entry.xpath("string()")) is not None:
                    continue
                entry = entry.xpath("string()").split(':')[1][1:]
                
                if i == 2: # parsing address
                    for address_entry in entry.split(','):
                        address_entry = address_entry.replace('\xa0', ' ')[1:]
                        csvrow.append(address_entry)
                else:
                    csvrow.append(entry)
                i+=1
            csv_writer.writerow(csvrow)
            
    csv_f.close()
    print('Output file saved: ' + output_name + '.' + output_type)


def parse_detail(facility_name):

    f = open("../input/details/" + facility_name, 'rb')
    binary = f.read()
    f.close()
    tree = fromstring(binary)
    data = tree.xpath('//div[contains(@class, "text")]')
    
    return data

def download_details(file_name=None):

    if file_name is None: # if no file name specified, parse all directories
        dir_list = [item for item in os.listdir('../input/regions') if re.search('.asp', item) is not None] 
    else:
        dir_list = [file_name]

    for dir in dir_list:
        f = open('../input/regions/' + dir, 'rb')
        binary = f.read()
        f.close()
        tree = fromstring(binary)
        rows = tree.xpath('//tr')
        for row in rows:
            if row[1].text is not None: # table head
                continue
            facility_name = row[1].xpath('./a')[0].text
            facility_name = facility_name.replace('"', '') # escape characters to meet NTFS file name requirements
            facility_name = facility_name.replace('/', '')
            url = "http://www1.gnb.ca/0017/specialCareHome_new/iframe/" + row[1].xpath('./a')[0].get('href')
            download(url, "details/" + facility_name + ".html")
        
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
