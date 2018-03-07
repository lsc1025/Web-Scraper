import csv
import os, sys
import re

name_of_script = "csv_iterator.py"
path_to_script = sys.argv[0][:-len(name_of_script)]
sys.path.insert(0, os.path.abspath(path_to_script + "../.."))

from scrapers.Normalizer.common.Filenames import *
from scrapers.Normalizer.common.TypeValidatorRegexes import compile_list_of_options, dollar_amount_regex

none_array = [None, '']

use_debug_filenames = False
output_to_temp = False

point_regex = re.compile("åá *")
comma_point_regex = re.compile(r"(,(\xa0| )+)(,(\xa0| )+)+")
comma_garbage_regex = re.compile(r"(,|\xa0|-| )+")
point_character_regex = re.compile("(,|-)(\xa0| )+•(\xa0| )+")
point_character_no_prefix_regex = re.compile("(\xa0| )+•(\xa0| )+")
small_point_character_regex = re.compile(r',(\xa0| )+·(\xa0| )+')
period_comma_regex = re.compile(r"\., ")

master_csv_filename = '2-FinalizedData/MASTER.csv'

# HELPER FUNCTIONS
def get_temp_name(filename):
	return filename[:-4] + '-TMP.csv'

def delete_tmps():
	for filename in get_tmp_normalized_csvs(path_to_script):
		os.remove(filename)

def delete_master():
	master_does_exist = os.path.isfile(master_csv_filename)
	if master_does_exist:
		os.remove(master_csv_filename)
	else:
		print("No Master CSV found!")

# MIGRATIONS
def low_rate_non_dollar_value_migration(rows):
	low_rate_label = 'low_rate'
	print(rows[0])
	low_rate_index = rows[0].index(low_rate_label)

	for i in range(1, len(rows)):
		low_rate_value = rows[i][low_rate_index]
		match = dollar_amount_regex.match(low_rate_value)
		if match is None:
			rows[i][low_rate_index] = None
		else:
			final_value = re.compile('(\$|,)').sub('', match.group())
			rows[i][low_rate_index] = final_value

	return rows

def fix_ascii_description_problems_migration(rows):
	'''Checks for and fixes common problems in descriptions not being strictly ASCII.'''
	description_index = rows[0].index('description')

	point_regexes = [point_regex, 
		comma_point_regex, 
		point_character_regex, 
		point_character_no_prefix_regex, 
		small_point_character_regex, 
		period_comma_regex]

	for row in rows:
		row_id = row[0]
		description = row[description_index]
		if len(description) != len(description.encode()):
			description = description.replace("’", "'")

			for point_separator_regex in point_regexes:
				point_split = point_separator_regex.split(description)
				if len(point_split) > 1:
					description = "\n".join(["- " + point for point in point_split if comma_garbage_regex.match(point) is None])

			if description[:2] == "- ":
				description = description[2:]

			row[description_index] = description

	return rows

def check_asciii_problems_in_descriptions(rows, filename):
	description_index = rows[0].index('description')

	faulty_descriptions = {}

	for row in rows[1:]:
		row_id = row[0]
		description = row[description_index]
		if description not in [None, ''] and len(description) != len(description.encode()):
			if faulty_descriptions.get(description) is None:
				faulty_descriptions[description] = [row_id]
			else:
				faulty_descriptions[description] = faulty_descriptions[description] + [row_id]

	for description in faulty_descriptions:
		print(description)
		for row_id in faulty_descriptions[description]:
			print('\t' + row_id)
		print()

	return faulty_descriptions

def add_company_name_and_eliminate_bad_values(rows):
	company_name_label = 'company_name'
	if company_name_label not in rows[0]:
		rows[0] = rows[0] + [company_name_label]

	company_name_index = rows[0].index(company_name_label)

	for i in range(1, len(rows)):
		if len(rows[i]) == len(rows[0]) - 1:
			rows[i] = rows[i] + [None]
		row = rows[i]
		if row[company_name_index] in ['TRUE', 'FALSE', True, False]:
			rows[i][company_name_index] = None

	return rows

def add_province_and_country_where_missing(rows):
	province_label = 'province'
	country_label = 'country'

	header_row = rows[0]
	row_id_index = 0
	province_index = header_row.index(province_label)
	country_index = header_row.index(country_label)

	for i in range(1, len(rows)):
		row = rows[i]
		row_id = row[row_id_index]
		province = row[province_index]
		country = row[country_index]

		if province in none_array:
			rows[i][province_index] = row_id.split('-')[1]
		if country in none_array or country == "Chesterfield":
			rows[i][country_index] = row_id.split('-')[0]

	return rows

# MAIN FUNCTIONS
def iterate():
	for filename in get_csv_filenames(path_to_script, get_original=False) if not use_debug_filenames else get_csv_sample_filenames(path_to_script, get_original=False):
		with open(filename, 'r') as infile:
			rows = [row for row in csv.reader(infile)]

		print(filename)

		rows = low_rate_non_dollar_value_migration(rows)
		rows = fix_ascii_description_problems_migration(rows)
		check_asciii_problems_in_descriptions(rows, filename)
		rows = add_province_and_country_where_missing(rows)

		with open(get_temp_name(filename) if output_to_temp else filename, 'w') as outfile:
			writer = csv.writer(outfile)
			for row in rows:
				writer.writerow(row)

def generate_master_csv():
	master_rows = []
	filenames = get_csv_filenames(path_to_script, get_original=False) if not use_debug_filenames else get_csv_sample_filenames(path_to_script, get_original=False)

	for filename in filenames:
		with open(filename, 'r') as infile:
			reader = csv.reader(infile)
			header_row = next(reader)
			rows = [header_row + ['company_name'] if header_row[-1] != 'company_name' else header_row]
			rows = rows + [row + [None] if rows[0] != 'company_name' else row for row in reader]
		
		master_rows = master_rows + rows if filename == filenames[0] else master_rows + rows[1:]

	with open(master_csv_filename, 'w') as master_file:
		master_rows = add_company_name_and_eliminate_bad_values(master_rows)
		csv_writer = csv.writer(master_file)
		csv_writer.writerows(master_rows)

def main():
	delete_tmps()
	delete_master()
	iterate()
	if not output_to_temp:
		generate_master_csv()

main()