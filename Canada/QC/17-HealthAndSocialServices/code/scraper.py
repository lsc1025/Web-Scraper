# -*- coding: utf-8 -*-
# scraper.py for 17-QC-HealthAndSocialServices

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
    
    # if no region name specified, parse all region
    dir_list = [item for item in os.listdir('../input/establishments') if re.search('.asp', item) is not None] if (region_name is None) else [region_name]    

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    for dir in dir_list:
        tree = get_lxml_tree('../input/establishments/' + dir)
        rows = tree.xpath('//td/a')
        for row in rows:
            installation_url = row.get('href')

            if (installation_url is None or re.search('Installation', installation_url) is None or re.search('Etablissement', installation_url) is not None):
                continue

            installation_url = 'http://wpp01.msss.gouv.qc.ca/appl/M02/' + installation_url            
            installation_name = 'installation' + installation_url.split('=')[1]
            
            csvrow = parse_establishment(dir, installation_name + '_' + dir)
           
            csv_writer.writerow(csvrow)
    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_establishment(establishment_name, facility_name):

    tree = get_lxml_tree("../input/establishments/" + establishment_name)
    columns = tree.xpath('//td')
    data = []
    for column in columns:
        data.append(column.xpath('string()').strip())

    csv_row = parse_installation(facility_name)

    csv_row.append(data[53]) # Télécopieur / Fax

    for i in range(65, 84, 2):
        csv_row.append(data[i])

    return csv_row

def parse_installation(facility_name):

    tree = get_lxml_tree('../input/installations/' + facility_name)
    columns = tree.xpath('//td')
    data = []
    for column in columns:
        data.append(column.xpath('string()').strip().replace('\x96', '-').replace('\x92', '\u00ed').replace('\x8c', '\u00e5'))

    installation_row = []
    # parsing basic info
    for i in range(37, 52, 2):
        installation_row.append(data[i])

    installation_row.append(data[57]) # Région sociosanitaire / Health Region
    # parsing special info
    for i in range(61, 66, 2):
        installation_row.append(data[i])

    services = ''
    # parsing services available
    for i in range(70, len(data) - 4):
        if re.search('Mission', data[i]):
            continue
        if (data[i].strip() is ''):
            continue
        services += data[i] + '; '
        
    installation_row.append(services[:-2])

    return installation_row

def download_establishments(file_name=None):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        sys.exit()

    if file_name is None: # if no file name specified, parse all directories
        dir_list = [item for item in os.listdir('../input/regions') if re.search('.asp', item) is not None] 
    else:
        dir_list = [file_name]

    for dir in dir_list:
        tree = get_lxml_tree('../input/regions/' + dir)
        rows = tree.xpath('//td/a')

        for row in rows:
            establishment_url = row.get('href')

            if (establishment_url is None):
                continue
            if (re.search('Etablissement', establishment_url) is None):
                continue

            establishment_url = 'http://wpp01.msss.gouv.qc.ca/appl/M02/' + establishment_url            
            establishment_name = 'establishment'
            establishment_name += establishment_url.split('=')[1]
            
            download(establishment_url, "establishments/" + establishment_name + '_' + dir)
   
    print('Download complete')

def download_installations(file_name=None):

    # if no file name specified, parse all directories
    dir_list = [item for item in os.listdir('../input/establishments') if re.search('.asp', item) is not None] if (file_name is None) else [file_name]

    for dir in dir_list:
        tree = get_lxml_tree('../input/establishments/' + dir)
        rows = tree.xpath('//td/a')

        for row in rows:
            installation_url = row.get('href')

            if (installation_url is None or re.search('Installation', installation_url) is None or re.search('Etablissement', installation_url) is not None):
                continue

            installation_url = 'http://wpp01.msss.gouv.qc.ca/appl/M02/' + installation_url            
            installation_name = 'installation'
            installation_name += installation_url.split('=')[1]
           
            download(installation_url, "installations/" + installation_name + '_' + dir)

    print('Download complete')
    

def download(url, file_name='index', num_retries=3, user_agent='wswp'):

    # Parsing robots.txt
    rp = robotparser.RobotFileParser()
    rp.set_url('http://www.msss.gouv.qc.ca/robots.txt')
    #rp.read()

    # begin of downloading
    print('Downloading:', url)
    #if rp.can_fetch(user_agent, url): # disable for non-unicode robots.txt
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
