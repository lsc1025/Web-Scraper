# -*- coding: utf-8 -*-

import os
import re
import csv
import codecs
import googlemaps
import importlib
import streetaddress
import time

def export(province='', country=''):

    dir_list = []

    directory = os.path.join("c:\\","Users\\Shichen\\Documents\\scrapers\\NormalizedOutputGeo")
    output_dir_pre = 'C:\\Users\\Shichen\\Documents\\scrapers\\NormalizedOutput\\'
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith("-NORMALIZED.csv"):
                dir_list.append(root + '\\' + file)
    
    for dir in dir_list:
        output_dir = dir.replace('NormalizedOutputGeo', 'NormalizedOutput')
        address_index = [None, None, None, None, None]
        geo_index = [None, None, None]
        has_geometry = False
        f = codecs.open(dir, 'r', encoding='utf-8-sig')
        head_row = next(csv.reader(f))
        rows = list(csv.reader(f))

        output_f = output_dir.replace('NormalizedOutput', 'NormalizedOutputGeo').replace('.csv', '-FIXED.csv')
        o = codecs.open(output_dir, 'r', encoding='utf-8')
        o_h = next(csv.reader(o))
        input_rows = list(csv.reader(o))
        o_f = codecs.open(output_f, 'w+', encoding='utf-8')
        writer = csv.writer(o_f, lineterminator='\n')

        for i in range(0, len(head_row)): # looking for index of address entries
            if (head_row[i] == 'latitude'):
                has_geometry = True

        for i in range(0, len(head_row)): # looking for index of address entries
            if (head_row[i] == 'address_line_1'):
                address_index[0] = i
            elif (head_row[i] == 'address_line_2'):
                address_index[1] = i
            elif (head_row[i] == 'city'):
                address_index[2] = i
            elif (head_row[i] == 'province'):
                address_index[3] = i
            elif (head_row[i] == 'postal_code'):
                address_index[4] = i
            elif (head_row[i] == 'latitude'):
                geo_index[0] = i
            elif (head_row[i] == 'longitude'):
                geo_index[1] = i
            elif (head_row[i] == 'neighborhood'):
                geo_index[2] = i
        try:
            assert (len(input_rows) == len(rows))
        except:
            print('Line number mismatching:')
            print(output_dir)
            continue

        writer.writerow(o_h)

        i = 0
        try:
            while i < len(input_rows):

                input_rows[i][12] = rows[i][address_index[0]]
                input_rows[i][13] = rows[i][address_index[1]]
                input_rows[i][14] = rows[i][geo_index[2]]
                input_rows[i][15] = rows[i][geo_index[0]]
                input_rows[i][16] = rows[i][geo_index[1]]
                input_rows[i][19] = rows[i][address_index[4]]
            
                writer.writerow(input_rows[i])
                i += 1
            #print('File saved:', output_f)
        except IndexError:
            print('Index:', output_f)
            print(output_dir)
            f.close()
            o.close()
            o_f.close()
            

        f.close()
        o.close()
        o_f.close()

    return None

def get_geometry(check_error=False, province='', country=''):

    dir_list = []

    directory = os.path.join("c:\\","Users\\Shichen\\Documents\\scrapers\\" + country + '\\' + province)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if check_error:
                if file.endswith("-ADDR2.csv") and re.search('output', root):
                    dir_list.append(root + '\\' + file)
            else:
                if file.endswith("-NORMALIZED.csv") and re.search('output', root): # only looks for '*-NORMALIZED.csv' files under optupt folders
                    dir_list.append(root + '\\' + file)

    for dir in dir_list:
        print(dir)
        address_index = [None, None, None, None, None]
        geo_index = [None, None, None]
        has_geometry = False
        f = codecs.open(dir, 'r', encoding='utf-8-sig')
        head_row = next(csv.reader(f))
        f.close()

        for i in range(0, len(head_row)): # looking for index of address entries
            if (head_row[i] == 'latitude'):
                has_geometry = True
            if (head_row[i] == 'address_line_1'):
                address_index[0] = i
            elif (head_row[i] == 'address_line_2'):
                address_index[1] = i
            elif (head_row[i] == 'city'):
                address_index[2] = i
            elif (head_row[i] == 'province'):
                address_index[3] = i
            elif (head_row[i] == 'postal_code'):
                address_index[4] = i
            elif (head_row[i] == 'latitude'):
                geo_index[0] = i
            elif (head_row[i] == 'longitude'):
                geo_index[1] = i
            elif (head_row[i] == 'neighborhood'):
                geo_index[2] = i
        assert bool(geo_index[0]) == bool(geo_index[1]) # check if both lat and lng exist
        retry_count = 5
        try:
            while not add_geometry(dir, address_index, geo_index, check_error) and retry_count > 0: # retry for API error
                print('Attempting to retry after 10 sec...')
                time.sleep(10)
                retry_count -= 1
            if retry_count == 0:
                print('Check data query, or try again by pressing "↑" + "ENTER"')
                break
        except googlemaps.exceptions.Timeout:
            return

def normalize_column(column_name, province, country, manual=False):

    importlib.reload(streetaddress)
    
    directory = os.path.join("c:\\","Users\\Shichen\\Documents\\scrapers\\" + country + '\\' + province) 

    dir_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith("-GEO.csv") and re.search('output', root):
                dir_list.append(root + '\\' + file)
    add_parser = streetaddress.StreetAddressParser()
    for dir in dir_list:
        print(dir)
        output_fname = dir.replace('-GEO', '-ADDR')
        csv_f = open(output_fname, 'w+', encoding='utf-8')
        csv_writer = csv.writer(csv_f, lineterminator='\n')
        
        column_index = None
        try:
            f = codecs.open(dir, 'r', encoding='utf-8-sig')
        except FileNotFoundError:
            print('Invalid province or country.')
            return

        head_row = next(csv.reader(f))
        head_row.append('addr_valid')

        rows = list(csv.reader(f))
        csv_writer.writerow(head_row)
        f.close()
        for i in range(0, len(head_row)):
            if (head_row[i] == column_name):
                column_index = i
                break
        if column_index == None:
            print('Invalid column name')
            return
        for row in rows:
            data = row[column_index] + ' ' + row[column_index+1]
            data = preprocess_address(data)
            addr = add_parser.parse(data)
            if (not addr['house']):
                addr['house'] = ''
            else:
                addr['house'] = addr['house'].strip().strip(',')
            if (not addr['suite_num']):
                addr['suite_num'] = ''

            line1 = addr['house'] + ' ' + addr['street_full'] if addr['street_full'] else data
            line2 = addr['suite_type'] + ' ' + addr['suite_num'] if addr['suite_type'] else ''

            if addr['other']:
                if re.findall('\d', addr['other']):
                    line2 += ' ' + addr['other']
                else:
                    line1 += ' ' + addr['other']
            line1 = line1.strip('-').strip()
            line2 = line2.strip()

            row[column_index] = line1
            row[column_index+1] = line2

            if len(line1) < 1:
                line1 = 'EMPTY'

            if (manual):
                if not line1[0].isdigit() or line1[len(line1)-1].isdigit():
                    print(data)
                    print(line1 + '|' + line2)
                    row.append(False)
                else:
                    row.append(True)
            else:
                print(line1 + '|' + line2)             

            csv_writer.writerow(row)

        csv_f.close()
        print('File saved:', output_fname)
    return None

def pre_dedup(dir, f_name):

    path = dir + '\\' + f_name

    f = codecs.open(path, 'r', encoding='utf-8')
    csv_reader = csv.reader(f)
    head_row = next(csv_reader)
    rows = list(csv_reader)
    f.close()

    ouput_fname = f_name[:-4] + '-FIXED.csv'
    path = dir + '\\' + ouput_fname
    
    csv_f = codecs.open(path, 'w+', encoding='utf-8')
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    # line1, city, state
    address_index = [5, 8, 10] # For current RH data
    add_parser = streetaddress.StreetAddressParser()

    csv_writer.writerow(head_row)

    for row in rows:
            
        data = row[address_index[0]]
        #print(data)
        addr = add_parser.parse(data)
        if (not addr['house']):
            addr['house'] = ''
        else:
            addr['house'] = addr['house'].strip().strip(',')
        if (not addr['suite_num']):
            addr['suite_num'] = ''

        line1 = addr['house'] + ' ' + addr['street_full'] if addr['street_full'] else ''
        line2 = addr['suite_type'] + ' ' + addr['suite_num'] if addr['suite_type'] else ''

        if addr['other']:
            if re.findall('\d', addr['other']):
                line2 += ' ' + addr['other']
            else:
                if re.search('box', addr['other'].lower()):
                    line2 = addr['other']
                else:
                    addr['other'] = addr['other'].replace(' ', '')
                    line1 += ' ' + addr['other']
        line1 = line1.strip('-').strip()
        line2 = line2.strip()

        if addr['street_full'] is None:
            line1 = line2
            line2 = ''

        if re.search('County Road', line1) and re.search('\d', line2):
            line1 += ' ' + line2
            line2 = ''

        line1 = line1.replace('.', ' ').replace('Nbsp;', '')
        #print(addr)
        line1 = normalize_suffix(line1)
        row[address_index[0]] = line1
        row[address_index[0]+1] = line2
        row[address_index[2]] = get_province_abbr(row[address_index[2]])

        if len(line1) < 1:
            line1 = 'EMPTY'

        if not line1[0].isdigit() or line1.split(' ')[-1] not in get_valid_suffix_list():
            #print(data)
            #print(line1 + '|' + line2)
            if line1[-1].isdigit():
                row.append(True)
            else:
                row.append(False)
        else:
            row.append(True)

        csv_writer.writerow(row)

    csv_f.close()
    return None

def abbr_address(column_name, province, country):

    directory = os.path.join("c:\\","Users\\Shichen\\Documents\\scrapers\\" + country + '\\' + province) 

    dir_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith("-ADDR.csv") and re.search('output', root):
                dir_list.append(root + '\\' + file)
    add_parser = streetaddress.StreetAddressParser()
    for dir in dir_list:
        print(dir)
        output_fname = dir.replace('-ADDR', '-ADDR2')
        csv_f = open(output_fname, 'w+', encoding='utf-8')
        csv_writer = csv.writer(csv_f, lineterminator='\n')
        
        column_index = None
        try:
            f = codecs.open(dir, 'r', encoding='utf-8-sig')
        except FileNotFoundError:
            print('Invalid province or country.')
            return

        head_row = next(csv.reader(f))

        rows = list(csv.reader(f))
        csv_writer.writerow(head_row)
        f.close()

        for i in range(0, len(head_row)):
            if (head_row[i] == column_name):
                column_index = i
                break
        if column_index == None:
            print('Invalid column name')
            return
        for row in rows:
            
            data = row[column_index]
            line2 = row[column_index+1]
            
            line1 = normalize_suffix(data).replace('.','').replace(' - ', ' ').strip()
            line1 = ' '.join(line1.split())

            row[column_index] = line1

            if len(line1) < 1:
                row[-1] = False
            else:
                if not line1[0].isdigit() or line1.split(' ')[-1] not in get_valid_suffix_list():
                    if line1[-1].isdigit():
                        row[-1] = True
                    else:
                        row[-1] = False
                else:
                    row[-1] = True
            csv_writer.writerow(row)

        csv_f.close()
        print('File saved:', output_fname)
    return None

def display_error(column_name='addr_valid', province='', country=''):
    directory = os.path.join("c:\\","Users\\Shichen\\Documents\\scrapers\\" + country + '\\' + province) 

    dir_list = []
    ndir_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith("-FIXED.csv") and re.search('output', root):
                dir_list.append(root + '\\' + file)
            if file.endswith("-NORMALIZED.csv") and re.search('output', root):
                ndir_list.append(root + '\\' + file) 
    
    for i in range(0, len(dir_list)):
        #print(dir)
        dir_split = dir_list[i].split('\\')
        normalized_dir = dir_split[6] + '-' + dir_split[7] + '-' + dir_split[8] + '-' + dir_split[10][:-10] + '.csv'
        normalized_dir = 'C:\\Users\\Shichen\\Documents\\scrapers\\NormalizedOutput\\' + normalized_dir
        csv_f = open(dir_list[i], 'r', encoding='utf-8')
        ncsv_f = open(normalized_dir, 'r', encoding='utf-8')
        
        csv_reader = csv.reader(csv_f)
        ncsv_reader = csv.reader(ncsv_f)

        column_index = None
        head_row = next(csv_reader)
        nhead_row = next(ncsv_reader)
        rows = list(csv_reader)
        nrows = list(ncsv_reader)

        print(len(rows), len(nrows))
        if len(rows) != len(nrows):
            print(dir_list[i])

        continue

        for i in range(0, len(head_row)):
            if (head_row[i] == column_name):
                column_index = i
                break
        i = 1
        for row in rows:
            i += 1
            if row[column_index] == '':
                print(dir)
                break
            #if row[-1] == 'False':
                #print(str(i) + ': ' + row[column_index] + '|' + row[column_index+1])
                
        csv_f.close()
    return None

def normalize_suffix(source):

    source_parsed = source.split(' ')
    street_suffix = source_parsed[len(source_parsed)-1]
    has_direction = False
    street_suffix = get_direction_abbr(street_suffix)
    if street_suffix:
        source_parsed[len(source_parsed)-1] = street_suffix

    street_suffix = source_parsed[len(source_parsed)-1]
    direct_abbr_suffix = ['N', 'S', 'W', 'E', 'SE', 'NW', 'NE', 'SW']
    
    if street_suffix in direct_abbr_suffix:
        has_direction = True
        street_suffix = source_parsed[len(source_parsed)-2]
    
    street_suffix = get_suffix_abbr(street_suffix.lower())
    if street_suffix:
        if has_direction:
            source_parsed[len(source_parsed)-2] = street_suffix
        else:
            source_parsed[len(source_parsed)-1] = street_suffix
    
    res = ' '.join(source_parsed)
    res = res.strip()

    return res

def add_geometry(dir, address_index, geo_index, check_error):

    f = codecs.open(dir, 'r', encoding='utf-8-sig')
    csv_reader = csv.reader(f)
    head_row = next(csv_reader)
    rows = list(csv_reader)
    f.close()
    if check_error:
        output_fname = dir.replace('ADDR2', "FIXED")
    else:
        output_fname = dir[:-4] + "-GEO.csv"
    appending = False

    if not check_error:
        if geo_index[2]:
            print()
        elif geo_index[0]:
            head_row.append('neighborhood')
        else:
            head_row += ['latitude', 'longitude', 'neighborhood']

    if os.path.isfile(output_fname): # output file existed, appending to bottom
        print('file exists:')
        csv_f = codecs.open(output_fname, "r", encoding='utf-8-sig')
        last_row = list(csv.reader(csv_f))
        csv_f.close()
        csv_f = open(output_fname, "a", encoding='utf-8-sig')
        csv_writer = csv.writer(csv_f, lineterminator='\n')
        last_size = len(last_row)-1
        last_row = last_row[len(last_row)-1]
        appending = True
    else:
        csv_f = open(output_fname, "w+", encoding='utf-8')
        csv_writer = csv.writer(csv_f, lineterminator='\n')
        csv_writer.writerow(head_row)
    
    gmap = GoogleMapUtil()

    i = 0
    for row in rows:
        if appending:
            if i == last_size:
                print('Resuming...')
                appending = False
            i+=1
            continue
        if check_error:
            if row[address_index[4]] and row[geo_index[0]] != 'ERROR':
                csv_writer.writerow(row)
                i+=1
                continue
            try:
                print('Processing facility:', row[address_index[0]])
                if row[address_index[0]] == '':
                    geometry=['', '']
                    neighborhood = ''
                    postalcode = ''
                else:
                    region = gmap.get_regions(get_address_query(row, address_index))
                    if not region:
                        print('Using basic address information...')
                        region = gmap.get_regions(get_address_query(row, address_index, True))
                    geometry = gmap.get_geometry()
                    neighborhood = gmap.get_neighborhood()
                    postalcode = gmap.get_postalcode()     
            except:
                csv_f.close()
                raise
                return False
            row[geo_index[0]] = geometry[0]
            row[geo_index[1]] = geometry[1]
            row[geo_index[2]] = neighborhood
            if row[address_index[4]] == '':
                row[address_index[4]] = postalcode
        else:
            print("{:.1%} ".format(i/len(rows)) + 'Processing facility:', row[address_index[0]])
            try:
                region = gmap.get_regions(get_address_query(row, address_index))
                geometry = gmap.get_geometry()
                neighborhood = gmap.get_neighborhood()
            except googlemaps.exceptions.ApiError as apie:          
                print('API error:', apie)
                print('Query:', get_address_query(row, address_index))
                csv_f.close()
                return False
            except googlemaps.exceptions.Timeout as te:
                print('Daily query limit reached.')
                csv_f.close()
                raise

            if not geo_index[0]: # append to end
                row += geometry
            else:  
                row[geo_index[0]] = geometry[0]
                row[geo_index[1]] = geometry[1]
            row.append(neighborhood)  
        i+=1 
        csv_writer.writerow(row)

    csv_f.close()
    print('File saved:', output_fname)
    return True

def extract_columns():

    directory = os.path.join("c:\\","Users\\Shichen\\Documents\\scrapers")

    csv_f = open("columns.csvf", "w+") # Initialize csv file & writer (output_type is reserved for future use)
    csv_writer = csv.writer(csv_f, lineterminator='\n')

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):

                source = []
                print(root)
                source.append(root.split('\\')[6])
                source.append(root.split('\\')[7])
                source.append(file)
                rows = ['ERROR']
                f = open(root + '\\' + file, 'r')
                try:
                    rows = next(csv.reader(f))
                except:
                    print('###############')
                f.close()
                columns = source + rows
                csv_writer.writerow(columns)
            
    csv_f.close()
    return None

def fix_csv(path_to_file, file_name):
    
    path = path_to_file + '\\' + file_name

    f = codecs.open(path, 'r', encoding='unicode-escape')
    rows = list(csv.reader(f))
    f.close()

    f_out = open(path_to_file + '\\fixed.csv', 'w+')
    csv_writer = csv.writer(f_out, lineterminator='\n')
    for row in rows:
        print(row)
        row = parse_list(row)
        csv_writer.writerow(row)
    
    f_out.close()
    return None

def preprocess_address(source):
    mappings = {
        'C. P.': 'CP',
        'case postale': 'CP',
        'C.P': 'CP',
        '(': ' ',
        ')': ' ',
        'P.O. Box': 'PO',
        '#': '# ',
        'c.p.': 'CP ',
        'Range Road': 'RR'
    }
    for key, value in mappings.items():
        source = source.replace(key, value)
   
    return source.strip()

def get_address_query(row, address_index, get_basic=False):

    if get_basic:
        query = row[address_index[2]] + ',' + row[address_index[3]]
        return query
    try:
        query = row[address_index[0]]
        query += ', ' + row[address_index[2]]
        query += ', ' + row[address_index[3]]
        return query
    except:
        raise ValueError('No address found!')

class GoogleMapUtil:

    #AIzaSyCmgHKUJyhj8DtzqwjLZXt2ubeqMoszaN0
    #AIzaSyBcxJttORSgrHUrd3BidFN_lMZYSRJDuOs
    #AIzaSyBf15pyAx0sS8n-1PEmjE3NCiTM04Rhigs

    def __init__(self, **kwargs):
        self.gmaps = googlemaps.Client(key='AIzaSyBf15pyAx0sS8n-1PEmjE3NCiTM04Rhigs')
        
    def get_regions(self, address):
        self.error = False
        try:
            result = self.gmaps.places(query=address)['results'][0]
            self.place_id = result['place_id']
            self.geometry = result['geometry']
            self.postalcode = result['formatted_address']
        except IndexError:
            print('Result not found!')
            self.error = True
            return None
        except KeyError:
            print('Result not found!')
            self.error = True
            return None
        return result

    def get_geometry(self):
        if self.error:
            return ['ERROR', 'ERROR']
        if not self.geometry:
            print('Call get_region() first!')
        geometry = list(self.geometry['location'].values())
        self.geometry = None
        return geometry

    def get_neighborhood(self):
        if self.error:
            return 'ERROR'
        if not self.place_id:
            print('Call get_region() first!')
            return None
        result = self.gmaps.place(self.place_id)['result']
        neighborhood = None
        for entry in result['address_components']:
            if 'neighborhood' in entry['types']:
                neighborhood = entry['long_name']
                break
        self.place_id = None
        return neighborhood

    def get_postalcode(self):
        if self.error:
            return 'ERROR'
        if not self.postalcode:
            print('Call get_region() first!')
            return None
        postalcode_regex = '([A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d)|(\d{5}(?:[-\s]\d{4})?)'
        postalcode_re = re.compile(postalcode_regex)
        postalcode = postalcode_re.findall(self.postalcode)
        if postalcode:
            if (len(postalcode) > 1):
                postalcode = postalcode[1][0]
            else:
                postalcode = postalcode[0][0] if postalcode[0][1] == '' else postalcode[0][1]
        else:
            postalcode = ''
        return postalcode

def parse_list(source):
    escape_char = {
        '\r\n ': '',
        '\x89Û\x90': '-',
        'â\x80\x90': ' ',
        'â\x80\x99': ',',
    }
    for i in range(0, len(source)):
        for key, value in escape_char.items():
            source[i] = source[i].replace(key, value)
        source[i] = source[i].strip()
    return [x for x in source if x]
    #return source

def get_direction_abbr(source):
    direction_abbr_dict = {
        'north': 'N',
        'south': 'S',
        'west': 'W',
        'east': 'E',
        'northeast': 'NE',
        'southwest': 'SW',
        'northwest': 'NW',
        'southeast': 'SE',
    }
    if source.upper() in list(direction_abbr_dict.values()):
        return source.upper()
    else:
        return direction_abbr_dict.get(source.lower())

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
        'District of Columbia': 'DC',
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
    if source in list(province_state_dict.values()):
        abbr = source
    else:
        abbr = province_state_dict.get(source)
    return abbr

def get_suffix_abbr(source):
    suffix_dict = {
            'avenue' : 'Ave',
            'street' : 'St',
            'boulevard': 'Blvd',
            'parkway': 'Pkwy',
            'highway': 'Hwy',
            'drive': 'Dr',
            'place': 'Pl',
            'expressway': 'Expy',
            'heights': 'Hts',
            'junction' : 'Jct',
            'circle' : 'Cir',
            'lane' : 'Ln',
            'road' : 'Rd',
            'crt' : 'Ct',
            'cres': 'Cr',
            'crescent' : 'Cr',
            'cresent' : 'Cr',
            'court' : 'Ct',
            'trail': 'Trl',
            'tr': 'Trl',
            'square' : 'Sq',
            }
    if source in list(suffix_dict.values()):
        abbr = source.title()
    else:
        abbr = suffix_dict.get(source)
    return abbr

def get_valid_suffix_list():
    return [
        'Ave',
        'St',
        'Blvd',
        'Broadway',
        'Pkwy',
        'Hwy',
        'Dr',
        'Pl',
        'Expy',
        'Close',
        'Hts',
        'Jct',
        'Cir',
        'Ln',
        'Cr',
        'Rd',
        'Ct',
        'Sq',
        'Trl',
        'Way',
        'N',
        'S',
        'W',
        'E',
        'NE',
        'SW',
        'NW',
        'SE',    
        ]
