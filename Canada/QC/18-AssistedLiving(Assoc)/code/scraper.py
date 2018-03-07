# -*- coding: utf-8 -*-
# scraper.py for 18-QC-AssistedrLiving(Assoc)

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
    
    dir_list = [item for item in os.listdir('../input/details') if re.search('.asp', item) is not None] 

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'Address', 'City', 'Postal Code', 'Phone', 'Province', 'Company Name / Name of operators', 'Number of rental units', 'Number of rental units in private residence for seniors', 'Type of residence', 'Year of opening', 'Date of possession', 'Updated on', 'Member of an association', 'Certification Date of issue', 'Offered services', 'Complete residence information']
    csv_writer.writerow(head_row)

    for dir in dir_list:
        csv_writer.writerow(parse_detail(dir))

    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(file_name):

    tree = get_lxml_tree('../input/details/' + file_name)
    facility_id = file_name.split('_')[0]
    columns = tree.xpath('//td/text()')
    facility_name = tree.xpath('//h1[1]/text()')[0].replace('\x92', '\u00ed')

    #print_list(columns)

    data = []
    for column in columns:
        data.append(column.replace('\xa0', ' ').replace('\x96', '-').replace('\x92', '\u00ed').replace('\x8c', '\u00e5').strip().strip('-').strip())

    csvrow = []
    csvrow.append(facility_name)
    offset = 0

    if (data[12] is not ''): # fixes for broken pages
        offset = 1

    # parsing address
    csvrow.append(data[13-offset])
    csvrow.append(data[14-offset].split('(')[0][:-1])
    for i in range(15 - offset, 17 - offset):
        csvrow.append(data[i])
    csvrow.append('QC')

    # Nom de la compagnie / Name of operators
    name_of_operators = data[19 - offset] + '; ' 
    i = 0
    while (data[20 - offset + i] is not ''):
        name_of_operators += data[20 + i]
        i += 1
    csvrow.append(name_of_operators[:-2]) 
    offset -= i

    # parsing details
    for i in range(22 - offset, 33 - offset, 2):
        csvrow.append(data[i])

    # parsing Membre d'une association / Member of an association
    member_of_association = data[34 - offset] + ' '
    i = 0
    while (data[35 - offset + i] is not ''):
        member_of_association += data[35 - offset + i] + ' '
        i += 1
    offset -= i
    csvrow.append(member_of_association[:-1].replace(',', ';')) 
    csvrow.append(data[36 - offset])
    if data[36 - offset] is '':
        offset += 1
    
    services = ''
    # parsing services available
    for i in range(38 - offset, len(data)):
        if (data[i].strip() is ''):
            break
        services += data[i] + '; '
        
    csvrow.append(services[:-2])
    csvrow.append('http://wpp01.msss.gouv.qc.ca/appl/K10/public/formulaire/K10FormCons.asp?noForm=' + facility_id) # link to complete info form

    return csvrow

def download_details(file_name='index.html'):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    tree = get_lxml_tree('../input/' + file_name)
    facility_ids = tree.xpath('//td[contains(@class, "formSTDroite")]/a/text()')
    facility_names = tree.xpath('//td[3]/a/text()')
    facility_regions = tree.xpath('//td[2]/text()')[1:-1]

    for i in range(0, len(file_names)):

        file_path = "details/" + facility_ids[i] + '_' + facility_regions[i] + '.asp'
        facility_url = 'http://wpp01.msss.gouv.qc.ca/appl/K10/public/K10ConsFormAbg.asp?Registre=' + facility_ids[i]
        download(facility_url, file_path, percent = "{:.0%} ".format(i/len(facility_ids)))
   
    print('Download complete')

def download(url, file_name='index', num_retries=3, user_agent='wswp', percent=None):

    if (os.path.isfile(file_name)):
        print("File already exists, skipping:", file_name)
        return None

    # Parsing robots.txt
    rp = robotparser.RobotFileParser()
    rp.set_url('http://www.msss.gouv.qc.ca/robots.txt')
    #rp.read()

    # begin of downloading
    print(percent + 'Downloading:', url)
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
    i = 0
    for col in columns:
        print(i)
        print(col)
        i += 1
