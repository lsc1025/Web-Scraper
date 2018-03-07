# -*- coding: utf-8 -*-
# scraper.py for 27-AB-SupportiveLiving

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
    
    dir_list = [item for item in os.listdir('../input/details') if re.search('.json', item) is not None] 

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'Address', 'City', 'Postal Code', 'Province', 'Accommodation Type', 'Number of Units', 'Funding Source', 'Operator', 'Contact Phone', 'Fax', 'Last Visit Date', 'Last Visit Type', 'Original Issue Date', 'Licence Issue Date', 'Licence Expiry Date', 'Licence Type', 'ASL Facility ID']
    csv_writer.writerow(head_row)

    for dir in dir_list:
        csvrow = parse_detail(dir)              
        csv_writer.writerow(parse_detail(dir))
    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(file_name):
    csvrow = []
 
    f = open('../input/details/' + file_name, 'rb')
    data = json.load(f)
    f.close()
    data = data['root']['data']

    if 'FUNDINGSOURCE' not in data:
        data['FUNDINGSOURCE'] = ''
    if 'LICENCETYPE' not in data:
        data['LICENCETYPE'] = ''
    if 'LASTVISITTYPE' not in data:
        data['LASTVISITTYPE'] = ''

    csvrow.append(data['ACCOMMODATIONNAME'])
    csvrow.append(data['ADDRESS1'])
    csvrow.append(data['CITY'])
    csvrow.append(data['POSTALCODE'])
    csvrow.append('AB')
    csvrow.append(data['ACCOMMTYPE_TEXT'])
    csvrow.append(data['CAPACITY'])
    csvrow.append(data['FUNDINGSOURCE'])
    csvrow.append(data['OPERATORNAME'])
    csvrow.append(data['PHONE'])
    csvrow.append(data['FAX'])
    csvrow.append(data['LASTVISITDATE'])
    csvrow.append(data['LASTVISITTYPE'])
    csvrow.append(data['ORIGINALISSUEDATE'])
    csvrow.append(data['LIC_ISSUEDATE'])
    csvrow.append(data['LIC_EXPIRYDATE'])
    csvrow.append(data['LICENCETYPE'])
    csvrow.append(data['ASLFACILITYID'])

    return csvrow

def download_details(file_name=None):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    src_path = '../input/data.json'
    f = open(src_path, 'rb')
    data = json.load(f)
    f.close()

    i=0
    for entry in data['aaData']:
        facility_id = entry[9]
        url = 'http://standardsandlicensing.alberta.ca/ibi_apps/WFServlet?IBIC_server=EDASERVE&IBIAPP_app=public%5freporting%5frepl&IBIF_ex=details%5ffacility%5finformation.fex&xform=wf_xmlr_transform_clean&xout=json&FACILITYID=' + facility_id
        download(url, 'details/' + facility_id + '.json', percent = "{:.0%} ".format(i/len(data['aaData'])))
        i+=1

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
