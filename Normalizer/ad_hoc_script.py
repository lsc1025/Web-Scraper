import re
import csv
import glob
import os, sys

name_of_script = "ad_hoc_script.py"
path_to_script = sys.argv[0][:-len(name_of_script)]
sys.path.insert(0, os.path.abspath(path_to_script + "../.."))

from scrapers.Normalizer.common.TypeValidatorRegexes import roman_number_regex, compile_list_of_options

all_filenames = glob.glob('2-FinalizedData/*.csv')

companies = compile_list_of_options(['Inc', "Mchc", 'Llc', 'Alh', 'INC', 'MCHC', 'LLC'])
blacklisted = compile_list_of_options(['Macon', 'Macamic', 'Macarena', 'Macedon', 'Machias', 'Machin', "Mack's", 'Mackellah', 'Mackenzie'])

def apply_name_capitalization(name_str):
	result = []
	space_split = name_str.split(' ')

	for part in space_split:
		if roman_number_regex.match(part) or companies.match(part):
			result.append(part.upper())
		else:
			result.append(part.capitalize())

	return " ".join(result)

def correct_scottish_names(rows):
	'''Input: list of rows for a given CSV file. Output: list of rows that contain name corrections.'''
	city_index = rows[0].index('city')
	name_index = rows[0].index('name')

	scottish_prefix_regex = re.compile("^(mc|mac|o')")

	def return_corrected_capitalization(name_val, match):
		span = match.span()

		if blacklisted.match(name_val) or companies.match(name_val): # i.e. if the value starts with a company abbreviation
			return name_val
		else:
			return name_val[span[0]:span[1]].capitalize() + apply_name_capitalization(name_val[span[1]:])

	for i in range(1, len(rows)):
		if len(rows[i]) >= max(city_index, name_index):
			city = apply_name_capitalization(rows[i][city_index])
			name = apply_name_capitalization(rows[i][name_index])

			original_city = rows[i][city_index]
			original_name = rows[i][name_index]

			city_match = scottish_prefix_regex.match(city.lower())
			name_match = scottish_prefix_regex.match(name.lower())

			if city_match:
				city = return_corrected_capitalization(city, city_match)
			if name_match:
				name = return_corrected_capitalization(name, name_match)

			if city != original_city:
				print("\"" + original_city + "\"" + "," + "\"" + city + "\"")
				rows[i][city_index] = city
			if name != original_name:
				print("\"" + original_name + "\"" + "," + "\"" + name + "\"")
				rows[i][name_index] = name

	return rows

none_array = [None, '']

def capitalize_addresses_and_cities(rows):
	city_index = rows[0].index('city')
	address_line_1_index = rows[0].index('address_line_1')

	#print()
	#print('original_value,ammended_value')

	for i in range(1, len(rows)):
		city = rows[i][city_index]
		address_line_1 = rows[i][address_line_1_index]

		if city not in none_array and city == city.upper():
			rows[i][city_index] = apply_name_capitalization(city)
			print("\"" + city + "\"" + "," + "\"" + rows[i][city_index] + "\"")

		rows[i][address_line_1_index] = apply_name_capitalization(address_line_1)
		'''
		if address_line_1 not in none_array and address_line_1 == address_line_1.upper():
			rows[i][address_line_1_index] = apply_name_capitalization(address_line_1)
			print("\"" + address_line_1 + "\"" + "," + "\"" + rows[i][address_line_1_index] + "\"")
		'''

	return rows

def print_fully_numeric_addresses(rows):
	number_regex = re.compile('^\d+$')
	row_id_index = rows[0].index('row_id')
	address_line_1_index = rows[0].index('address_line_1')
	address_line_2_index = rows[0].index('address_line_2')

	#print()
	#print('row_id,numeric_address_line_1')

	for i in range(1, len(rows)):
		row_id = rows[i][row_id_index]
		address_line_1 = rows[i][address_line_1_index]
		address_line_2 = rows[i][address_line_2_index]
		if number_regex.match(address_line_1):
			print(row_id + ',' + str(address_line_1) + "," + str(address_line_2))

	return None

output_changes = True

def main():
	#print("original_value,ammended_value")
	print('row_id,numeric_address_line_1,address_line_2')
	for filename in all_filenames:
		with open(filename, 'r') as f:
			rows = [row for row in csv.reader(f)]

		#rows = correct_scottish_names(rows)
		rows = capitalize_addresses_and_cities(rows)
		print_fully_numeric_addresses(rows)

		if output_changes:
			with open(filename, 'w') as f:
				writer = csv.writer(f)
				writer.writerows(rows)

main()