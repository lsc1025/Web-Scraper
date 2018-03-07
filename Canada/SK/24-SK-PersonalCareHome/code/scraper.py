# -*- coding: utf-8 -*-
# scraper.py for 24-SK-PersonalCareHome

import urllib.request
import re
import os
import csv
import sys
import ipgetter
import ipcalc
from requests import Request, Session
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

    head_row = ['Facility Name', 'Address', 'City', 'Postal Code', 'Province', 'Community', 'Licensee', 'Contact Phone', 'Total Unresolved Infractions', 'Approx Start Rate per Month', 'Beds (AC)', 'Attributes', 'Link to Inspection Details']
    csv_writer.writerow(head_row)

    for dir in dir_list:
        csv_writer.writerow(parse_detail(dir))

    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(file_name):

    csvrow =[]
    tree = get_lxml_tree('../input/details/' + file_name)
    facility_name = tree.xpath('//h1[contains(@class, "article-title")]/text()')
    csvrow.append(facility_name[0])

    data = tree.xpath('//span[contains(@class, "display-field")]/text()')
    postalcode_regex = '[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d'
    regex = re.compile(postalcode_regex)
 
    if (re.match('((\(\d{3}\) ?)|(\d{3}-))?\d{3}-\d{4}', data[3]) is None):
        data.insert(3, "") # fix facility with no phone number

    address = data[0].split('\n')
    city = address[1].split('SK')[0]
    postalcode = regex.findall(address[1])
    postalcode = postalcode[0].upper() if len(postalcode) > 0 else ''

    csvrow.append(address[0])
    csvrow.append(city)
    csvrow.append(postalcode)
    csvrow.append('SK')

    for i in range(1, 7):
        csvrow.append(data[i]) # basic info

    attr = ''
    if len(data) > 7: # looking for attributes data
        for i in range(7, len(data)):
            attr += data[i]
            attr += '; '
        csvrow.append(attr[:-2])
    else:
        csvrow.append("")

    inspection_link = ''
    inspection_link_source = tree.xpath('//tr[contains(@class, "hovereffect")]')
    if (len(inspection_link_source) > 0):
        for link in inspection_link_source:
            inspection_link += 'http://personalcarehomes.saskatchewan.ca' + link.get('onclick').split("'")[1][:-1]
            inspection_link += '; '
        csvrow.append(inspection_link[:-2])
    else:
        csvrow.append('')
    return csvrow

def download_details(file_name='index.html'):

    tree = get_lxml_tree('../input/' + file_name)
    facility_urls = tree.xpath('//tr[contains(@onclick, "href")]')
    facility_names = tree.xpath('//td[contains(@class, "facilityName")]/text()')
    facility_ids = tree.xpath('//td[contains(@class, "facilityNumber")]/text()')

    html_file = open('../input/urls.html', 'w+') # create html file for parsebook to download detail pages
    html_file.write('<html>')
    html_file.write('<body>')

    for i in range(0, len(facility_urls)):
        file_path = "details/" + facility_names[i].strip() + '_' + facility_ids[i].strip() + '.html'
        facility_url = 'http://personalcarehomes.saskatchewan.ca/Facility/Details/' + facility_urls[i].get('onclick').split('/')[3][:-2]
        html_file.write('<a href="'+ facility_url +'">link</a>')
   
    html_file.write('</body>')
    html_file.close()
    print('Download complete')

def test():
    download('http://personalcarehomes.saskatchewan.ca/Facility/Details/a9d5b655-71c3-4771-bf77-e95448e6b773', 'test.html', session = get_session())

def get_session():

    headers = {'content-type': 'application/x-www-form-urlencoded'}
    payload = {'AcceptDisclaimerButton': ''}
    params = {'returnUrl': '/PersonalCareHomes/Table'}
    LOGIN_URL = 'http://personalcarehomes.saskatchewan.ca/?returnUrl=%2FPersonalCareHomes%2FTable'
    res1 = requests.post(LOGIN_URL, headers=headers, data=payload, params=params)
    url = 'http://personalcarehomes.saskatchewan.ca/Facility/Details/a9d5b655-71c3-4771-bf77-e95448e6b773'
    print(res1.cookies)
    res2 = requests.get(url, cookies=res1.cookies)
    print(res2.text)
    return None

def download(url, file_name='index', num_retries=3, user_agent='wswp', percent='', session=None):

    if (os.path.isfile(file_name)):
        print("File already exists, skipping:", file_name)
        return None

    # Parsing robots.txt
    rp = robotparser.RobotFileParser()
    rp.set_url('http://www.msss.gouv.qc.ca/robots.txt')
    #rp.read()

    # begin of downloading
    print(percent + 'Downloading:', url)
    #if rp.can_fetch(user_agent, url): # disable for site without robots.txt
    headers = {}
    headers['User-Agent'] = user_agent
    try:
        if session is None:
            response = requests.get(url, headers=headers)
        else:
            print('cookie')
            response = requests.get(url, cookies=cookies)
    except (URLError, HTTPError, ContentTooShortError) as e:
        print('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
            # recursively retry 5xx HTTP errors
                download(url, num_retries - 1, cookies = cookies)
    

    # Output to binary file
    f = open("../input/" + file_name, "wb+")
    f.write(response.content)
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
