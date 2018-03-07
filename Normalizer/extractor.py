# -*- coding: utf-8 -*-

import os
import csv
import codecs

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
                    print('##############################################################')
                f.close()
                print(source)


                columns = source + rows

                csv_writer.writerow(columns)
                # perform calculation
                
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
    #return [x for x in source if x]
    return source