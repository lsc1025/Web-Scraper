import csv
import os
import re

from scrapers.Normalizer.common.TypeValidatorRegexes import dollar_amount_regex
from scrapers.Normalizer.common.Filenames import get_normalized_geo_equivalent

none_array = [None, '']

def generic_map_y_to_x(rows, x_column_name, y_column_name, x_regex, y_regex):
	'''Maps the contents of y to x if x is empty and y is not.'''
	x_index = None
	y_index = None

	header_row = rows[0]

	if y_column_name in rows[0] and x_column_name in rows[0]:
		x_index = rows[0].index(x_column_name)
		y_index = rows[0].index(y_column_name)
	else:
		return rows

	for i in range(1, len(rows)):
		row = rows[i]
		if len(row) >= len(header_row):
			if x_regex.match(row[x_index]) == None and y_regex.match(row[y_index]) != None:
				rows[i][x_index] = row[y_index]
				rows[i][y_index] = None

	return rows

def consolidate_normalized_files(normalized_rows, normalized_geo_rows):
	assert len(normalized_rows) >= len(normalized_geo_rows)
	standard_row_len = len(normalized_geo_rows[0]) + 1
	for i in range(len(normalized_geo_rows)):
		#if len(normalized_geo_rows[i]) + 1 == standard_row_len:
		normalized_rows[i] = normalized_rows[i][0:1] + normalized_geo_rows[i]

	return normalized_rows

def municipality_to_city_migration(geo_rows):
	# Canada-QC-17-HealthAndSocialServices-output-NORMALIZED
	city_label = 'city'
	municipality_label = 'municipality'

	header_row = geo_rows[0]

	if city_label and municipality_label in header_row:
		city_index = header_row.index(city_label)
		municipality_index = header_row.index(municipality_label)

		for i in range(1, len(geo_rows)):
			row = geo_rows[i]
			if len(row) >= len(header_row):
				city = row[city_index]
				municipality = row[municipality_index]

				if city in none_array and municipality not in none_array:
					geo_rows[i][city_index] = municipality
					geo_rows[i][municipality_index] = None

	return geo_rows

def provider_name_to_name_migration(geo_rows):
	str_regex = re.compile('.+')
	return generic_map_y_to_x(geo_rows, 'name', 'provider_name', str_regex, str_regex)

def consolidate_geo_info(rows, geo_rows):
	'''Adds address info from the original CSVs to the Geo data as need be.'''
	city_label = 'city'
	name_label = 'name'
	postal_code_label = 'postal_code'
	typeofcare_label = 'typeofcare'
	typeofcare2_label = 'typeofcare2'

	original_header = rows[0]
	geo_header = geo_rows[0]

	# original index is the first value, geo index is the second.
	column_to_index_map = {
		postal_code_label: [-1, -1],
		typeofcare_label: [-1, -1],
		typeofcare2_label: [-1, -1]
	}

	if city_label in original_header and city_label in geo_header and name_label in original_header and name_label in geo_header:
		city_index_original = rows[0].index(city_label)
		city_index_geo = geo_rows[0].index(city_label)

		name_index_original = rows[0].index(name_label)
		name_index_geo = geo_rows[0].index(name_label)
	else:
		return geo_rows

	for label in column_to_index_map:
		if label in original_header:
			column_to_index_map[label][0] = rows[0].index(label)
			if label in geo_rows[0]:
				column_to_index_map[label][1] = geo_rows[0].index(label)
			else:
				column_to_index_map[label][1] = len(geo_rows[0])
				geo_rows[0] = geo_rows[0] + [label]

	def find_equivalent_original_index(name, city, original_index):
		'''Checks over rows after original_index to find the index of the row that has the specified name and city.
		If no equivalent is found, then a None is returned. Otherwise, the index of the appropriate row is returned.'''
		name = name.lower().strip()
		city = city.lower().strip()
		while True:
			if len(rows) <= original_index or len(rows[original_index]) < max(name_index_original, city_index_original):
				return None
			elif rows[original_index][name_index_original].lower().replace("’", "'").strip() == name and rows[original_index][city_index_original].lower().replace("’", "'").strip() == city:
				return original_index
			else:
				print(rows[original_index][name_index_original].lower())
				print(name)
				print(rows[original_index][city_index_original].lower())
				print(city)
				original_index += 1

	def indices_are_non_empty():
		are_indices_non_empty = False
		for label in column_to_index_map:
			print(column_to_index_map[label])
			are_indices_non_empty = are_indices_non_empty or column_to_index_map[label][0] != -1
		print(are_indices_non_empty)
		return are_indices_non_empty

	def get_non_empty_keys():
		return [label for label in column_to_index_map if column_to_index_map[label][0] != -1]

	original_index = 0

	original_indices = [
		name_index_original, 
		city_index_original, 
		column_to_index_map[postal_code_label][0], 
		column_to_index_map[typeofcare_label][0], 
		column_to_index_map[typeofcare2_label][0]]
	geo_indices = [
		name_index_geo, 
		city_index_geo, 
		column_to_index_map[postal_code_label][1], 
		column_to_index_map[typeofcare_label][1], 
		column_to_index_map[typeofcare2_label][1]]

	max_original_index = max(original_indices)
	max_geo_index = max(geo_indices)

	if indices_are_non_empty():
		for geo_index in range(1, len(geo_rows)):
			original_index += 1
			print('O: ' + str(original_index) + ' G: ' + str(geo_index) + '-')
			geo_rows[geo_index] = geo_rows[geo_index] + [None] * (len(geo_rows[0]) - len(geo_rows[geo_index]))
			assert len(geo_rows[0]) == len(geo_rows[geo_index])
			if len(geo_rows[geo_index]) > max_geo_index:
				print("Geo_index: " + str(geo_index) + " has row: " + str(geo_rows[geo_index]))
				new_original_index = find_equivalent_original_index(geo_rows[geo_index][name_index_geo], geo_rows[geo_index][city_index_geo], original_index)
				print(new_original_index)
				if new_original_index:
					original_index = new_original_index
					print(original_index)

					if column_to_index_map[postal_code_label][0] != -1:
						print("Consolidating postal code")
						original_postal_code = rows[original_index][column_to_index_map[postal_code_label][0]]
						if len(rows[original_index]) > max_original_index and original_postal_code not in none_array:
							geo_rows[geo_index][column_to_index_map[postal_code_label][1]] = original_postal_code
					if column_to_index_map[typeofcare_label][0] != -1:
						print("Consolidating typeofcare")
						original_entry = rows[original_index][column_to_index_map[typeofcare_label][0]]
						original_geo_entry = geo_rows[geo_index][column_to_index_map[typeofcare_label][1]]
						if len(rows[original_index]) > max_original_index and original_entry not in none_array:
							geo_rows[geo_index][column_to_index_map[typeofcare_label][1]] = original_geo_entry + ";" + original_entry if original_geo_entry not in none_array else original_entry
					if column_to_index_map[typeofcare2_label][0] != -1:
						print("Consolidating typeofcare2")
						original_entry = rows[original_index][column_to_index_map[typeofcare2_label][0]]
						original_geo_entry = geo_rows[geo_index][column_to_index_map[typeofcare2_label][1]]
						if len(rows[original_index]) > max_original_index and original_entry not in none_array:
							geo_rows[geo_index][column_to_index_map[typeofcare2_label][1]] = original_geo_entry + ";" + original_entry if original_geo_entry not in none_array else original_entry
				else:
					original_index -= 1

	return geo_rows 

def consolidate_files(filename):
	'''Input filename is to the header-normalized version of the file. i.e. 2-FinalizedData/USA-AK-70-AssististedLiving-output-NORMALIZED.csv.
	Writes resulting consolidated files to the equivalent 1-ConsolidatedData/ file and returns the rows written for future migration.'''
	print(filename)
	with open(filename, 'r') as infile:
		rows = [row for row in csv.reader(infile)]
		rows = provider_name_to_name_migration(rows)

	if os.path.isfile(get_normalized_geo_equivalent(filename)):
		with open(get_normalized_geo_equivalent(filename), 'r') as geofile:
			geo_rows = [row for row in csv.reader(geofile)]
			geo_rows = provider_name_to_name_migration(geo_rows)
			geo_rows = municipality_to_city_migration(geo_rows)
			rows = consolidate_geo_info(rows, geo_rows)

		with open("1-ConsolidatedData/" + filename.split('/')[-1], 'w') as sourcefile:
			writer = csv.writer(sourcefile)
			writer.writerows(rows)

		return rows
	else:
		os.remove(filename)
		return None

