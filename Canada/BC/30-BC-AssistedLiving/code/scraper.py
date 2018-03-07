# -*- coding: utf-8 -*-
# scraper.py for 1-ON-AssistedLiving
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
    
    dir_list = [item for item in os.listdir('../input/details') if re.search('.html', item) is not None] 

    output_fname = output_name + '.' + output_type
    csv_f = open("../output/" + output_fname, "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    head_row = ['Facility Name', 'Address', 'City', 'Postal Code', 'Province', 'Contact Phone', 'Toll-Free Phone', 'Fax', 'Email', 'Services Hours', 'Wheelchair accessible', 'Parking Notes']
    csv_writer.writerow(head_row)

    for dir in dir_list:

        csvrow = parse_detail(dir)
        if csvrow != None:
            csv_writer.writerow(csvrow)

    csv_f.close()
    print('Output file saved: ' + output_fname)

def parse_detail(file_name):

    data = {}
    csvrow = []

    tree = get_lxml_tree('../input/details/' + file_name)
    content = tree.xpath('//div[@class="mb10"]')

    for entry in content:
        id = entry.get('id')
        if id is None:
            continue
        if id == 'address':
            data[id] = entry.xpath('./div/text()')
            data['postalcode'] = entry.xpath('./div/span/text()')
        else:
            data[id] = entry.xpath('./text()')

    csvrow.append(data['address'][0])
    csvrow.append(data['address'][1])
    csvrow.append(data['address'][2].split(',')[0])
    csvrow.append(data['postalcode'])
    csvrow.append('BC')
    csvrow.append(data['phoneDiv'])
    csvrow.append(data['tollFreeDiv'])
    csvrow.append(data['faxDiv'])
    csvrow.append(data['emailDiv'])
    csvrow.append(data['hoursDiv'])
    csvrow.append(data['wheelChairDiv'])
    csvrow.append(data['parkingDiv'])

    for i in range(0, len(csvrow)):

        csvrow[i] = str(csvrow[i]).replace("['", '').replace("']", '').replace('[]', '')

    return csvrow

    postalcode_regex = '([A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d)|(\d{5})'
    province_regex = '[A-Z][A-Z]'
    
    csvrow.append(tree.xpath('//b[contains(@class, "homename")]/text()')) # facility name
    data_source = tree.xpath('//table[contains(@class, "drilldownhome")]')
    
    csvrow = (data_source[0].xpath('.//td[contains(@class, "value")]/text()'))
    if (csvrow[3] in ['Terminated', 'Surrendered'] or csvrow[2] in ['Revoked', 'Refused - Prosecution'] or len(csvrow) < 6):
        return None
    if (csvrow[2] == 'None'):
        del csvrow[2]
    postalcode_re = re.compile(postalcode_regex)
    province_re = re.compile(province_regex)
    
    if len(postalcode_re.findall(csvrow[4])) > 0: 
        csvrow.insert(4, '')
    if len(postalcode_re.findall(csvrow[6])) > 0: # fix for 3-line-address
        csvrow[4:6] = [''.join(csvrow[4:6])]
    postalcode = postalcode_re.findall(csvrow[5])[0]
    postalcode = postalcode[0] if postalcode[1] == '' else postalcode[1] # fix for US zip code
    province = province_re.findall(csvrow[5])[0]
    city = csvrow[5].split(province)[0].strip()
    csvrow[5] = city
    csvrow.insert(6, postalcode)
    csvrow.insert(7, province)
    csvrow = csvrow[:-(len(csvrow)-11)]

    links = tree.xpath('//a')
    website = ''
    email = ''
    for link in links:
        url = link.get('href')
        if re.search('http', str(url)):
            website = url
        if re.search('mailto', str(url)):
            email = url.split(':')[1]
    csvrow.append(website)
    csvrow.append(email)
    # parsing available services
    booleans = []
    booleans_src = tree.xpath('//ul[contains(@class, "cs_list")]/li')
    for entry in booleans_src:
        if (entry.get('class') == 'cs_yes'):
            booleans.append(True)
        else:
            booleans.append(False)
    csvrow.append(booleans)

    # parsing details
    details = data_source[2].getchildren()
    for child in details:
        data = child.xpath('./td[@class="value"]/text()')
        if data != []:
            csvrow.append(data[0])
    return csvrow

def download_details(file_name=None):

    if (not ip_check()):
        print('Running script from local IP, script terminating...')
        return None

    dir_list = [item for item in os.listdir('../input/aeiou') if re.search('.html', item) is not None] if file_name is None else [file_name]

    for dir in dir_list:
        tree = get_lxml_tree('../input/aeiou/' + dir)
        rows_src = tree.xpath('//tr[@class="item"]')
        
        for row in rows_src:
            facility_id = row.get('onclick').split('=')[2][:-2]
            url = 'http://www.fraserhealth.ca/find-us/locations/our-locations?site_id=' + facility_id
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
