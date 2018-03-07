# -*- coding: utf-8 -*-
# scraper.py for 29-BC-AssistedLiving
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


def parse_directory(output_name='output', output_type='csv', region_name=None):
    
    dir_list = [item for item in os.listdir('../input/details') if re.search('.html', item) is not None] if region_name is None else [region_name]

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'Address', 'City', 'Postal Code', 'Province', 'Contact Phone', 'Fax', 'Website', 'Health Authority', 'Publicly subsidized units', 'Private-pay units', 'Total Assisted Living units']
    csv_writer.writerow(head_row)

    for dir in dir_list:

        tree = get_lxml_tree('../input/details/' + dir)
        source = tree.xpath('//p')
        
        i = 1
        while i < len(source):
            csvrow = []
            basic = source[i].xpath('string()').strip().split('\r\n')
            csvrow.append(basic[0])
            csvrow.append(basic[1])
            if (basic[2] != 'n/a'):
                csvrow.append(basic[2].split(',')[0])
                csvrow.append(basic[3])
                csvrow.append(basic[2].split(',')[1].strip())
            else:
                csvrow.append('')
                csvrow.append(basic[3])
                csvrow.append('')
            
            contact = source[i+1].xpath('string()').strip().split('\r\n')

            for p in range(0, len(contact)):
                if contact[p] != '':
                    contact[p] = contact[p].split(':')[1].replace('\xa0', '')

            csvrow.append(contact[0])
            csvrow.append(contact[1])
            csvrow.append(contact[2])
            if len(contact) > 3:
                csvrow.append(contact[4])
            else:
                csvrow.append('')
            
            detail = source[i+2].xpath('string()').split('\xa0')
            for k in range(0, 3): 
                csvrow.append(detail[k].split(':')[1].strip())

            csv_writer.writerow(csvrow)
            i += 3

    csv_f.close()
    print('Output file saved: ' + output_fname)

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

    tree = get_lxml_tree('../input/index.html')
    urls = tree.xpath('//a')

    for url in urls:
        url = url.get('href')
        if re.search('locator', str(url)):
            facility_id = url.split('/')[6]
            url = 'http://www.health.gov.bc.ca' + url
            download(url, '../input/details/' + facility_id + '.html')
   
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
