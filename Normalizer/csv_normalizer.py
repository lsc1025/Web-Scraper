import glob
import csv
import sys
import re
import os

name_of_script = "csv_normalizer.py"
path_to_script = sys.argv[0][:-len(name_of_script)]
sys.path.insert(0, os.path.abspath(path_to_script + "../.."))

from scrapers.Normalizer.common.HeaderNormalizer import *
from scrapers.Normalizer.common.NormalizationException import *
from scrapers.Normalizer.common.ColumnOrderer import *
from scrapers.Normalizer.common.Filenames import *
from scrapers.Normalizer.common.TypeValidators import *
from scrapers.Normalizer.common.FileConsolidator import consolidate_files

use_debug_filenames = True
output_to_tmp = False
re_consolidate_files = False

'''
def add_row_id_to_originals():
	all_filenames = get_csv_filenames(path_to_script, get_original=True)

	def add_row_id_migration(filename, rows):
		rows[0] = ['row_id'] + rows[0]
		for i in range(1, len(rows[1:]) + 1):
			sample_csv_filename_split = filename.split('/')
			rows[i] = [sample_csv_filename_split[2] + "-" + sample_csv_filename_split[3] + "-" + sample_csv_filename_split[4] + "-" + sample_csv_filename_split[6][:-4] + "-" + str(i)] + rows[i]

		return rows

	for csv_filename in all_filenames:
		with open(csv_filename, 'r') as csv_input:
			rows = [row for row in csv.reader(csv_input)]

		rows = add_row_id_migration(csv_filename, rows)

		with open(csv_filename, 'w') as outfile:
			writer = csv.writer(outfile)
			for row in rows:
				writer.writerow(row)

def add_row_id_to_normalized_geo_csvs():
	all_filenames = glob.glob("0-GeoData/*.csv")

	def add_row_id_migration(filename, rows):
		rows[0] = ['row_id'] + rows[0]
		for i in range(1, len(rows)):
			sample_csv_filename_split = filename.split('/')
			rows[i] = [sample_csv_filename_split[-1][:-4] + "-" + str(i)] + rows[i]

		return rows

	for csv_filename in all_filenames:
		with open(csv_filename, 'r') as csv_input:
			rows = [row for row in csv.reader(csv_input)]

		rows = add_row_id_migration(csv_filename, rows)

		with open(csv_filename, 'w') as outfile:
			writer = csv.writer(outfile)
			for row in rows:
				writer.writerow(row)
'''

def input_csvs():
	result = None
	if use_debug_filenames:
		result = get_csv_sample_filenames(path_to_script, get_original=True)
	else:
		result = get_csv_filenames(path_to_script, get_original=True)

	return result

def output_csvs():
	if use_debug_filenames:
		return get_csv_sample_filenames(path_to_script, get_original=False)
	elif output_to_tmp:
		return get_tmp_normalized_csvs(path_to_script)
	else:
		return get_csv_filenames(path_to_script, get_original=False)

def source_files():
	return get_source_files_filenames(path_to_script)

def normalize_headers():
	all_filenames = input_csvs()

	NUMBER_PROVINCES_COVERED = 11
	NUMBER_STATES_COVERED = 26

	assert len(all_filenames) > NUMBER_PROVINCES_COVERED + NUMBER_STATES_COVERED or use_debug_filenames

	for csv_filename in all_filenames:
		with open(csv_filename, 'r') as csv_input:
			try:
				csv_contents = csv_input.readlines()
				csv_header = csv_contents[0].split(',')
				transformed_csv_header = transform_column_line(csv_filename, csv_header)
				csv_contents[0] = ",".join(transformed_csv_header) + "\n"
			except UnicodeDecodeError as ex:
				print("\ncolumn_normalizer.py: Error normalizing " + csv_filename + " for the reason of " + str(ex))
				break
			except NormalizationException as ex:
				print(ex)
				break

		output_filename = generate_normalized_filename(csv_filename, output_to_tmp=output_to_tmp)

		with open(output_filename, 'a') as csv_output:
			csv_output.writelines(csv_contents)

def filter_and_order_csvs():
	for csv_filename in output_csvs():
		rows = []
		source_file = get_source_files_equivalent(csv_filename)
		if re_consolidate_files:
			rows = consolidate_files(csv_filename) 
		if os.path.isfile(source_file):
			filter_and_order_csv(source_file, csv_filename, rows)
		elif os.path.isfile(csv_filename):
			print("ASFD: " + csv_filename)
			os.remove(csv_filename)

def validate_csvs():
	for csv_filename in output_csvs():
		if validate_file(csv_filename) != True:
			return False
	return True

def delete_old_normalized():
	for filename in output_csvs():
		os.remove(filename)

delete_old_normalized()
normalize_headers()
filter_and_order_csvs()

if validate_csvs():
	get_no_match_list()
	get_report()
	get_no_valid_type_of_care_list()
	get_no_type_of_care_list()
