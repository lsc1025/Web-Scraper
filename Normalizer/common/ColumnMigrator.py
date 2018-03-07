import csv
import os
import re

from scrapers.Normalizer.common.TypeValidatorRegexes import dollar_amount_regex
from scrapers.Normalizer.common.Filenames import get_normalized_geo_equivalent

input_from_normalized_geo_csvs = True # if true, then rows will be drawn from 0-GeoData/*-NORMALIZED.csv files, with row_id added later
#from scrapers.Normalizer.csv_normalizer import input_from_normalized_geo_csvs

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

def contact_email_migration(rows):
	email_index = None
	contact_email_index = None

	if 'fac._contact_email' in rows[0] and 'email' in rows[0]:
		email_index = rows[0].index('email')
		contact_email_index = rows[0].index('fac._contact_email')
	else:
		return rows

	for i in range(len(rows)):
		row = rows[i]
		if row[email_index] == None and row[contact_email_index] != None:
			rows[i][email_index] = row[contact_email_index]

	return rows

def provider_name_migration(rows):
	email_index = None
	contact_email_index = None

	if 'name' in rows[0] and 'provider_name' in rows[0]:
		email_index = rows[0].index('name')
		contact_email_index = rows[0].index('provider_name')
	else:
		return rows

	for i in range(len(rows)):
		row = rows[i]
		if row[email_index] == None and row[contact_email_index] != None:
			rows[i][email_index] = row[contact_email_index]

	return rows

def consolidate_types_of_care(rows):
	typeofcare_index = None
	typeofcare2_index = None

	header_row = rows[0]
	if 'typeofcare' in header_row:
		typeofcare_index = header_row.index('typeofcare')
	if 'typeofcare2' in header_row:
		typeofcare2_index = header_row.index('typeofcare2')

	#print("typeofcare_index: " + str(typeofcare_index))
	#print("typeofcare2_index: " + str(typeofcare2_index))
	#print("len(rows): " + str(len(rows)))

	if typeofcare_index != None and typeofcare2_index != None:
		typeofcare_index = header_row.index('typeofcare')
		for i in range(1, len(rows)):
			#print(str(i) + " " + str(len(rows[i])))
			row = rows[i]

			if len(row) >= len(header_row):
				typeofcare2 = row[typeofcare2_index]

				type_of_care_value = ''
				typeofcare = row[typeofcare_index]

				if typeofcare and typeofcare2:
					type_of_care_value = typeofcare + ';' + typeofcare2
				elif typeofcare:
					type_of_care_value = typeofcare
				elif typeofcare2:
					type_of_care_value = typeofcare2

				rows[i][typeofcare_index] = type_of_care_value
	elif typeofcare2_index:
		rows[0][typeofcare2_index] = "typeofcare"

	return rows

def alzheimers_care_migration(rows):
	typeofcare_index = None
	specialties_index = None
	alzheimer_facility_index = None
	supports_irreversable_dimentia_alzheimers_index = None

	if 'specialty_programs' in rows[0]:
		specialties_index = rows[0].index('specialty_programs')
	elif 'supports_irreversable_dimentia_alzheimers' in rows[0]:
		supports_irreversable_dimentia_alzheimers_index = rows[0].index('supports_irreversable_dimentia_alzheimers')
	elif 'alzheimer_facility' in rows[0]:
		alzheimer_facility_index = rows[0].index('alzheimer_facility')
	else:
		return rows

	if 'typeofcare' in rows[0]:
		typeofcare_index = rows[0].index('typeofcare')
	else:
		typeofcare_index = len(rows[0])
		rows[0] = rows[0] + ['typeofcare']

	for i in range(1, len(rows)):
		row = rows[i]

		if typeofcare_index == len(row):
			rows[i] = rows[i] + ['']
			row = rows[i]

		if len(rows[i]) >= len(rows[0]):
			current_types_of_care = row[typeofcare_index]

			if specialties_index != None and row[specialties_index] != None:
				specialties = row[specialties_index]
				if "ALZHEIMER" in specialties:
					current_types_of_care = current_types_of_care + ";" + "Alzheimer's Care"
				if "DEMENTIA" in specialties:
					current_types_of_care = current_types_of_care + ";" + "Dementia Care"
			elif alzheimer_facility_index != None and row[alzheimer_facility_index] == 'TRUE':
				current_types_of_care = current_types_of_care + ";" + "Alzheimer's Care"
			elif supports_irreversable_dimentia_alzheimers_index != None and row[supports_irreversable_dimentia_alzheimers_index] == 'TRUE':
				current_types_of_care = current_types_of_care + ";" + "Alzheimer's Care"
				current_types_of_care = current_types_of_care + ";" + "Dementia Care"

			rows[i][typeofcare_index] = current_types_of_care

	return rows

def finances_in_type_of_care_migration(rows):
	finances_index = None
	typeofcare_index = None

	header_row = rows[0]

	if 'typeofcare' in header_row:
		typeofcare_index = header_row.index('typeofcare')
	else:
		return rows

	if 'finances' in header_row:
		finances_index = header_row.index('finances')
	else:
		rows[0] = header_row + ['finances']
		finances_index = -1
		header_row = rows[0]

	for i in range(1, len(rows)):
		row = rows[i]
		if len(row) == header_row:
			if finances_index == -1:
				rows[i] = row + ['']
				row = rows[i]

			#print('len row: ' + str(len(row)))
			#print('finances_index: ' + str(finances_index))

			finances_list = rows[i][finances_index].split(';')
			typeofcare = row[typeofcare_index]

			if 'SUBSIDIZED' in typeofcare:
				finances_list.append('Low income Subsidy')
			elif 'Medicaid' in typeofcare:
				finances_list.append('Medicaid')
			elif 'Medicare' in typeofcare:
				finances_list.append('Medicare')

			rows[i] = ';'.join(finances_list)

	return rows

def parse_city_st_zip_migration(rows):
	citystzip_index = None
	city_index = None
	province_index = None
	postal_code_index = None

	header_row = rows[0]

	if 'citystzip' in header_row:
		citystzip_index = header_row.index('citystzip')
	else:
		return rows

	if 'city' in header_row:
		city_index = header_row.index('city')
	elif 'fac_city' in header_row:
		city_index = header_row.index('fac_city')
	else:
		city_index = len(header_row)
		rows[0] = header_row + ['city']
		header_row = rows[0]

	if 'province' in header_row:
		province_index = header_row.index('province')
	else:
		province_index = len(header_row)
		rows[0] = header_row + ['province']
		header_row = rows[0]

	if 'postal_code' in header_row:
		postal_code_index = header_row.index('postal_code')
	else:
		postal_code_index = len(header_row)
		rows[0] = header_row + ['postal_code']
		header_row = rows[0]

	for i in range(1, len(rows)):
		rows[i] = rows[i] + ([''] * (len(header_row) - len(rows[i])))
		row = rows[i]

		city_st_zip_value = row[citystzip_index]

		comma_split = city_st_zip_value.split(', ')
		space_split = comma_split[1].split('  ')

		city_st_zip_split = [comma_split[0], space_split[0], space_split[1]]

		rows[i][city_index] = city_st_zip_split[0]
		rows[i][province_index] = city_st_zip_split[1]
		rows[i][postal_code_index] = city_st_zip_split[2]

	return rows

def parse_low_high_rate(rows):
	low_high_rate_index = None
	low_high_rate_label = 'low_high_rate'
	header_row = rows[0]

	if low_high_rate_label in header_row:
		low_high_rate_index = header_row.index(low_high_rate_label)
	else:
		return rows

	low_rate_label = 'low_rate'
	high_rate_label = 'high_rate'

	low_rate_index = None
	high_rate_index = None

	if low_rate_label in header_row:
		low_rate_index = header_row.index(low_rate_label)
	else:
		rows[0] = rows[0] + [low_rate_label]
		low_rate_index = len(header_row)

	if high_rate_label in header_row:
		high_rate_index = header_row.index(high_rate_label)
	else:
		rows[0] = rows[0] + [high_rate_label]
		high_rate_index = len(header_row)	

	for i in range(1, len(rows)):
		row = rows[i]
		if len(rows[0]) - 1 == len(row) or len(rows[0]) - 2 == len(row):
			while (len(rows[0]) - len(rows[i])) > 0:
				rows[i] = rows[i] + ['']

		row = rows[i]
		if len(row) == len(rows[0]):
			low_high_rate_value = row[low_high_rate_index]
			split_by_slash = low_high_rate_value.split('/')

			if low_high_rate_value not in [None, '']:
				rows[i][low_rate_index] = split_by_slash[0].strip() if split_by_slash[0] not in none_array else None
				rows[i][high_rate_index] = split_by_slash[1].strip() if split_by_slash[1] not in none_array else None

				

	return rows

def empty_description_migration(rows):
	description_label = 'description'
	description_index = None

	if description_label in rows[0]:
		description_index = rows[0].index(description_label)
	else:
		return rows

	for i in range(1, len(rows)):
		row = rows[i]
		if len(row) == len(rows[0]):
			if row[description_index] not in none_array and len(row[description_index]) < 10:
				rows[i][description_index] = None

	return rows

def consolidate_first_and_last_name(rows, name_root):
	first_name_index = None
	first_name_label = name_root + '_first_name'

	last_name_index = None
	last_name_label = name_root + "_last_name"

	name_index = None
	name_label = name_root + "_name"

	header_row = rows[0]

	if first_name_label in header_row:
		first_name_index = header_row.index(first_name_label)
	elif last_name_label in header_row:
		last_name_index = header_row.index(last_name_label) 
	else:
		return rows

	if name_label in header_row:
		name_index = header_row.index(name_label)
	else:
		name_index = len(header_row)
		rows[0] = rows[0] + [name_label]

	for i in range(1, len(rows)):
		if len(rows[0]) - 1 == len(rows[i]):
			rows[i] = rows[i] + ['']

		row = rows[i]

		if len(row) == len(rows[0]):
			first_name_value = row[first_name_index] if first_name_index != None else ''
			last_name_value = row[first_name_index] if first_name_index != None else ''
			name_value = row[name_index]

			if name_value in none_array:
				separator = ' ' if first_name_value not in none_array and last_name_value not in none_array else ''
				rows[i][name_index] = first_name_value + separator + last_name_value

				#del rows[i][name_index]

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

	'''
	postal_code_index_original = -1
	postal_code_index_geo = -1

	typeofcare_index_original = -1
	typeofcare_index_geo = -1

	typeofcare2_index_original = -1
	typeofcare2_index_geo = -1
	'''
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
		name = name.lower()
		city = city.lower()
		while True:
			if len(rows) <= original_index or len(rows[original_index]) < max(name_index_original, city_index_original):
				return None
			elif rows[original_index][name_index_original].lower().replace("’", "'") == name and rows[original_index][city_index_original].lower().replace("’", "'") == city:
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
		print("Hello!")
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
					'''
					def migrate_upon_non_empty_value(label, append_upon_migration=False):
						if column_to_index_map[label][0] != -1:
							print("Consolidating " +  label)
							original_entry = rows[original_index][column_to_index_map[label][0]]
							original_geo_entry = geo_rows[geo_index][column_to_index_map[label][1]]
							if len(rows[original_index]) > max_original_index and original_entry not in none_array:
								geo_rows[geo_index][column_to_index_map[typeofcare_label][1]] = original_geo_entry + ";" + original_entry if original_geo_entry not in none_array else original_entry

						return geo_rows[geo_index]
					
					geo_rows[geo_index] = migrate_upon_non_empty_value(postal_code_label)
					geo_rows[geo_index] = migrate_upon_non_empty_value(typeofcare_label, append_upon_migration=True)
					geo_rows[geo_index] = migrate_upon_non_empty_value(typeofcare2_label, append_upon_migration=True)
					'''
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

def apply_migrations_to_rows(input_filename, output_filename, rows):
	print(input_filename)
	if rows in [None, []]:
		with open(input_filename, 'r') as infile:
			rows = [row for row in csv.reader(infile)]
			rows = provider_name_to_name_migration(rows)

	print(len(rows))

	rows = contact_email_migration(rows)
	rows = provider_name_migration(rows)
	rows = consolidate_types_of_care(rows)
	rows = alzheimers_care_migration(rows)
	rows = parse_city_st_zip_migration(rows)

	rows = parse_low_high_rate(rows)
	rows = generic_map_y_to_x(rows, 'low_rate', 'high_rate', dollar_amount_regex, dollar_amount_regex)
	rows = empty_description_migration(rows)
	rows = consolidate_first_and_last_name(rows, 'contact')
	rows = consolidate_first_and_last_name(rows, 'admin')
	rows = finances_in_type_of_care_migration(rows)

	with open(output_filename, 'w') as outfile:
		writer = csv.writer(outfile)
		writer.writerows(rows)
	

def get_fieldname_blacklist():
	return ['typeofcare2', 'low_high_rate', 'high_rate', 'admin_first_name', 'admin_last_name', 'contact_first_name', 'contact_last_name']